from django.apps import AppConfig


class CommandConfig(AppConfig):
    name = 'command'

    def ready(self):
        import command.signals
