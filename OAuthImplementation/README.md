# OAuthImplementation

This project demonstrates a minimal custom Google OAuth2 (authorization code) integration in Django without using third-party libraries like `django-allauth`.

Quick start

1. Install dependencies
```powershell
pip install -r requirements.txt
```
2. Set environment variables (or edit `settings.py` for quick testing):
```powershell
$env:GOOGLE_OAUTH_CLIENT_ID = 'your-client-id'
$env:GOOGLE_OAUTH_CLIENT_SECRET = 'your-client-secret'
$env:GOOGLE_OAUTH_CALLBACK_URL = 'http://localhost:8000/auth/callback/google/'
```
3. Run migrations and start server
```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
4. Open http://127.0.0.1:8000/ and click "Sign in with Google".

Notes
- Tokens are stored in the `Profile` model at `OAuthImplementation/accounts/models.py`.
- This is a demo; do not use this code in production without adding secure token storage, HTTPS, and further hardening.
