
import threading

class ThreadJob(threading.Thread):
    def __init__(self, callback, event, interval):
        threading.Thread.__init__(self)
        self.callback = callback
        self.event = event
        self.interval = interval
        super(ThreadJob, self).__init__()

    def run(self):
        while not self.event.wait(self.interval):
            self.callback()

def set_interval(callback, interval):
    event = threading.Event()
    job = ThreadJob(callback, event, interval)
    job.start()
    return job

