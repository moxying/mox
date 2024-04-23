import threading
import queue


class EventDispatcher:
    """
    Generic event dispatcher which listen and dispatch events
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_instance()
        return cls._instance

    def _init_instance(self):
        self._event_queue = queue.Queue()
        self._events = {}

    def add_event_listener(self, event_type, listener):
        """
        Add an event listener for an event type
        """
        with self._lock:
            if event_type not in self._events.keys():
                self._events[event_type] = []
            self._events[event_type].append(listener)

    def remove_event_listener(self, event_type, listener):
        """
        Remove event listener.
        """
        with self._lock:
            if event_type in self._events.keys():
                listeners = self._events[event_type]
                if len(listeners) == 1:
                    # Only this listener remains so remove the key
                    del self._events[event_type]
                else:
                    # Update listeners chain
                    listeners.remove(listener)
                    self._events[event_type] = listeners

    def dispatch_event(self, event_type, event_data):
        """
        Dispatch Event
        """
        self._event_queue.put((event_type, event_data))

    def start_dispatching(self):
        while True:
            try:
                event_type, event_data = self._event_queue.get()
                self._dispatch(event_type, event_data)
            except queue.Empty:
                pass

    def _dispatch(self, event_type, event_data):
        with self._lock:
            if event_type in self._events.keys():
                for listener in self._events[event_type]:
                    listener(event_data)
