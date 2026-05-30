// Minimal frontend JS: fetch profile JSON and log it when on profile page
document.addEventListener('DOMContentLoaded', function(){
  if (window.location.pathname.includes('/auth/profile')){
    fetch('/auth/api/profile/')
      .then(r => {
        if (!r.ok) throw r
        return r.json()
      })
      .then(data => console.log('Profile data:', data))
      .catch(err => console.warn('Could not load profile:', err))
  }
});
