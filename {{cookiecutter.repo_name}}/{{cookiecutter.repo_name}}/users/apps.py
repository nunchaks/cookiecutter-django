from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = '{{cookiecutter.repo_name}}.users'
    verbose_name = "Users"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass