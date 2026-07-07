from collections import defaultdict


class EventBus:

    def __init__(self):
        self._events = defaultdict(list)

    def subscribe(self, event_name, callback):
        if callback not in self._events[event_name]:
            self._events[event_name].append(callback)

    def unsubscribe(self, event_name, callback):
        if callback in self._events[event_name]:
            self._events[event_name].remove(callback)

    def emit(self, event_name, *args, **kwargs):
        for callback in self._events[event_name]:
            callback(*args, **kwargs)

    def clear(self):
        self._events.clear()