from threading import Thread

def async(f):
    """Make a function asynchronous"""
    def wrapper(*args, **kwargs):
        thr = Thread(target = f, args = args, kwargs = kwargs)
        thr.start()
        return thr
    return wrapper
