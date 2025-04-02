import ctypes

BUF_SZ = 16


class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]


class History(ctypes.Structure):
    _fields_ = [
        ("head", ctypes.c_size_t),
        ("tail", ctypes.c_size_t),
        ("full", ctypes.c_int),
        ("cur", ctypes.c_size_t),
        ("buf", Point * BUF_SZ),
    ]


hist = History()


def add(x: int, y: int):
    global hist

    if hist.full:
        hist.tail = (hist.tail + 1) % BUF_SZ

    hist.buf[hist.head].x = x
    hist.buf[hist.head].y = y

    hist.cur = hist.head
    hist.head = (hist.head + 1) % BUF_SZ
    hist.full = int(hist.head == hist.tail)


def truncate_hist():
    global hist

    if not (hist.full and hist.tail == hist.head):
        return

    hist.read = (hist.cur + 1) % BUF_SZ
    hist.full = hist.tail == hist.read


def hist_get(*args):
    global hist

    if not hist.full and hist.tail == hist.head:
        return None, ctypes.c_int(), ctypes.c_int()

    return 1, ctypes.c_int(hist.buf[hist.cur].x), ctypes.c_int(hist.buf[hist.cur].y)


def hist_add(x: int, y: int):
    get, cx, cy = hist_get()
    if not get and cx.value == x and cy.value == y:
        return

    truncate_hist()
    add(x, y)


def hist_prev():
    global hist

    if not hist.full and hist.tail == hist.head:
        return

    if hist.cur == hist.tail:
        return

    hist.cur = BUF_SZ - 1 if hist.cur == 0 else hist.cur - 1


def hist_next():
    global hist

    if not hist.full and hist.tail == hist.head:
        return

    n = (hist.cur + 1) % BUF_SZ

    if n != hist.head:
        hist.cur = n
