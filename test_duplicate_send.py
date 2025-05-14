import threading
from queue_stub import DuplicateGuardQueue

def worker(q, msg):
    q.put_unique(msg)

def test_duplicate_blocked():
    q = DuplicateGuardQueue()
    text = "Saturated PoR answer"
    threads = [threading.Thread(target=worker, args=(q, text)) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert q.count(text) == 1
