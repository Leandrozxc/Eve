from django.apps import AppConfig


class UsersettingsConfig(AppConfig):
    name = 'apps.usersettings'

    def ready(self):
        import apps.usersettings.signals  # noqa
