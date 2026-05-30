## School Management System

### Backend

Run the Django backend with:

```bash
uv run python manage.py runserver 8000
```

### Frontend verifier

Run the local verification frontend with:

```bash
python frontend/server.py
```

Then open:

- http://localhost:3000
- http://localhost:3000/auth/google/callback

The frontend can be used to verify:

- Register
- Login
- Google OAuth callback exchange
