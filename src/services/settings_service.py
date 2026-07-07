from core import App
from events import bus, Events

from .base_service import BaseService


class SettingsService(BaseService):

    def __init__(self):
        super().__init__(App)

    def get(self, key, default=None):
        return self.app.config.get(key, default)

    def set(self, key, value):
        self.app.config.set(key, value)
        bus.emit(Events.SETTINGS_CHANGED, key, value)

    def all(self):
        return self.app.config.all()