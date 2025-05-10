import threading, hashlib

class DuplicateGuardQueue:
    def __init__(self):
        self._lock = threading.Lock()
        self._seen = set()
        self._queue = []

    def put_unique(self, msg: str):
        h = hashlib.sha256(msg.encode()).hexdigest()
        with self._lock:
            if h in self._seen:
                return  # duplicate suppressed
            self._seen.add(h)
            self._queue.append(msg)

    # helper for tests
    def count(self, msg: str):
        return self._queue.count(msg)
