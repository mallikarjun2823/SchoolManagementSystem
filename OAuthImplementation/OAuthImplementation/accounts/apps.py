from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'OAuthImplementation.accounts'

    def ready(self):
        # import signal handlers
        try:
            import OAuthImplementation.accounts.signals  # noqa: F401
        except Exception:
            pass
