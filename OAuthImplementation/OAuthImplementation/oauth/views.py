from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
from django.conf import settings
from django.core import signing
from urllib.parse import urlencode
import requests
import secrets

from django.contrib.auth import login, get_user_model, logout
from OAuthImplementation.accounts.models import Profile
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_GET
import logging


logger = logging.getLogger('OAuthImplementation.oauth')


def google_login(request):
    """Start the OAuth2 authorization flow by redirecting to Google's auth endpoint."""
    state = signing.dumps(
        {
            'nonce': secrets.token_urlsafe(16),
        },
        salt='google-oauth-state',
    )
    logger.info('google_login start state=%s callback=%s session_key=%s', state, settings.GOOGLE_OAUTH_CALLBACK_URL, request.session.session_key)
    params = {
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_OAUTH_CALLBACK_URL,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'access_type': 'offline',
        'prompt': 'consent',
    }
    url = 'https://accounts.google.com/o/oauth2/v2/auth'
    auth_url = f"{url}?{urlencode(params)}"
    logger.info('google_login redirect_url=%s', auth_url)
    return redirect(auth_url)


def google_callback(request):
    error = request.GET.get('error')
    logger.info('google_callback query params=%s', dict(request.GET))
    if error:
        logger.warning('google_callback received error=%s', error)
        return HttpResponseBadRequest(f"OAuth error: {error}")

    state = request.GET.get('state')
    if not state:
        logger.warning('google_callback missing state')
        return HttpResponseBadRequest('Invalid or missing state')
    try:
        signing.loads(state, salt='google-oauth-state', max_age=600)
    except signing.BadSignature:
        logger.warning('google_callback invalid state signature state=%s', state)
        return HttpResponseBadRequest('Invalid or missing state')

    code = request.GET.get('code')
    if not code:
        logger.warning('google_callback missing code')
        return HttpResponseBadRequest('Missing code')

    # Exchange code for tokens
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_OAUTH_CALLBACK_URL,
        'grant_type': 'authorization_code',
    }
    logger.info('google_callback exchanging code for token token_url=%s redirect_uri=%s', token_url, settings.GOOGLE_OAUTH_CALLBACK_URL)
    resp = requests.post(token_url, data=data, headers={'Accept': 'application/json'})
    logger.info('google_callback token response status=%s body=%s', resp.status_code, resp.text[:800])
    if resp.status_code != 200:
        return HttpResponseBadRequest('Token exchange failed')
    token_data = resp.json()
    access_token = token_data.get('access_token')
    if not access_token:
        logger.warning('google_callback no access_token token_data_keys=%s', list(token_data.keys()))
        return HttpResponseBadRequest('No access token received')

    # Fetch user info
    userinfo_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
    logger.info('google_callback fetching userinfo userinfo_url=%s', userinfo_url)
    uresp = requests.get(userinfo_url, headers={'Authorization': f'Bearer {access_token}'})
    logger.info('google_callback userinfo response status=%s body=%s', uresp.status_code, uresp.text[:800])
    if uresp.status_code != 200:
        return HttpResponseBadRequest('Failed to fetch user info')
    userinfo = uresp.json()

    # Get or create local user
    User = get_user_model()
    email = userinfo.get('email') or userinfo.get('sub')
    if not email:
        return HttpResponseBadRequest('Email not available from provider')

    user, created = User.objects.get_or_create(username=email, defaults={
        'email': email,
        'first_name': userinfo.get('given_name', ''),
        'last_name': userinfo.get('family_name', ''),
    })
    logger.info('google_callback user lookup username=%s created=%s id=%s email=%s', user.username, created, user.id, user.email)

    # Update or create Profile with token info
    expires_in = token_data.get('expires_in')
    refresh_token = token_data.get('refresh_token')
    try:
        profile = user.profile
    except Exception:
        profile = Profile.objects.create(user=user)
        logger.info('google_callback created profile user_id=%s', user.id)

    profile.provider = 'google'
    profile.provider_id = userinfo.get('sub')
    profile.picture = userinfo.get('picture')
    profile.access_token = access_token
    if refresh_token:
        profile.refresh_token = refresh_token
    if expires_in:
        try:
            profile.token_expires_at = timezone.now() + timedelta(seconds=int(expires_in))
        except Exception:
            pass
    profile.save()
    logger.info('google_callback saved profile user_id=%s provider=%s provider_id=%s', user.id, profile.provider, profile.provider_id)

    # Log the user in
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    logger.info('google_callback login complete user_id=%s authenticated=%s', user.id, request.user.is_authenticated)
    # save some profile info in session
    request.session['oauth_userinfo'] = userinfo
    logger.info('google_callback session saved keys=%s', list(request.session.keys()))

    return redirect('profile')


def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    userinfo = request.session.get('oauth_userinfo')
    return render(request, 'oauth/profile.html', {'userinfo': userinfo})


def profile_api(request):
    """Return JSON profile info for the authenticated user."""
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)
    try:
        profile = request.user.profile
    except Exception:
        return JsonResponse({'detail': 'Profile not found'}, status=404)

    data = {
        'username': request.user.username,
        'email': request.user.email,
        'provider': profile.provider,
        'provider_id': profile.provider_id,
        'picture': profile.picture,
        'token_expires_at': profile.token_expires_at.isoformat() if profile.token_expires_at else None,
    }
    return JsonResponse(data)


def logout_view(request):
    logout(request)
    return redirect('login')


@require_GET
def home(request):
    """Public home page with login link."""
    logger.info('home view hit user_authenticated=%s path=%s', request.user.is_authenticated, request.path)
    return render(request, 'oauth/home.html')
