# rheoproc.interprocess
# Methods here for enabling cross process communication. Relatively poor design - should be replaced by a more complete
# 'logger' class which encompasses this rather than having bare methods and a global variable.

__is_worker = False
def set_worker():
    global __is_worker
    __is_worker = True

def is_worker():
    return __is_worker

__q = None
def push(payload):
    if __q is not None:
        __q.put(payload)

def pop():
    if __q is not None:
        return __q.get()

def set_q(q):
    global __q
    __q = q