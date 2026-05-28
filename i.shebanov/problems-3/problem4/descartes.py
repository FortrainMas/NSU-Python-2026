class Descartes:
    def __init__(self, x, n):
        if n < 0:
            raise ValueError("n must be non-negative")
        if n > 0 and not x:
            raise ValueError("x must be non-empty when n > 0")
        self._x = list(x)
        self._n = n
        self._indices = [0] * n

    def current(self):
        return tuple(self._x[i] for i in self._indices)

    def advance(self):
        for i in range(self._n - 1, -1, -1):
            self._indices[i] += 1
            if self._indices[i] < len(self._x):
                return
            self._indices[i] = 0
