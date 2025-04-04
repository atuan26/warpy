class History:
    def __init__(self):
        self.BUF_SZ = 16
        self.head = 0
        self.tail = 0
        self.full = False
        self.cur = 0
        self.buf = [{"x": 0, "y": 0} for _ in range(self.BUF_SZ)]

    def add(self, x, y):
        if self.full:
            self.tail = (self.tail + 1) % self.BUF_SZ

        self.buf[self.head]["x"] = x
        self.buf[self.head]["y"] = y

        self.cur = self.head
        self.head = (self.head + 1) % self.BUF_SZ
        self.full = self.head == self.tail

    def truncate_hist(self):
        if not self.full and self.tail == self.head:
            return

        self.head = (self.cur + 1) % self.BUF_SZ
        self.full = self.tail == self.head

    def hist_get(self):
        if not self.full and self.tail == self.head:
            return None, None

        x = self.buf[self.cur]["x"]
        y = self.buf[self.cur]["y"]

        return x, y

    def hist_add(self, x, y):
        cx, cy = self.hist_get()

        if cx is not None and cy is not None and cx == x and cy == y:
            return  # dedup

        self.truncate_hist()
        self.add(x, y)

    def hist_prev(self):
        if not self.full and self.tail == self.head:
            return

        if self.cur == self.tail:
            return

        self.cur = self.BUF_SZ - 1 if self.cur == 0 else self.cur - 1

    def hist_next(self):
        if not self.full and self.tail == self.head:
            return

        n = (self.cur + 1) % self.BUF_SZ

        if n != self.head:
            self.cur = n


_history = History()


def hist_get(x=None, y=None) -> tuple[int, int, int]:
    """
    Get current history position coordinates.
    Returns -1 if no history exists, 0 otherwise.
    Updates x and y by reference in the original C API,
    but here returns the values directly.
    """
    x_val, y_val = _history.hist_get()
    if x_val is None or y_val is None:
        return -1, 0, 0
    return 0, x_val, y_val


def hist_add(x: int, y: int):
    """Add a position to history"""
    _history.hist_add(x, y)


def hist_prev():
    """Move to previous history position"""
    _history.hist_prev()


def hist_next():
    """Move to next history position"""
    _history.hist_next()
