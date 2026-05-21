class TableError(ValueError):
    pass


class Table:
    def __init__(self, data=None):
        if data is None:
            self._rows = []
            self.width = None
        else:
            try:
                self._rows = [list(row) for row in data]
            except TypeError as e:
                raise TableError("unsupported data for Table creation") from e

            if len(self._rows) != 0:
                self.width = len(self._rows[0])
                for i, row in enumerate(self._rows):
                    if len(row) != self.width:
                        raise TableError(
                            f"row {i + 1} has {len(row)} columns, expected {self.width}"
                        )
            else:
                self.width = None

    @classmethod
    def from_tsv(cls, text, sep="\t"):
        if not text:
            return cls()
        lines = text.split("\n")
        if lines and lines[-1] == "":
            lines = lines[:-1]
        if not lines or lines == [""]:
            return cls()
        rows = [line.split(sep) for line in lines]
        return cls(rows)

    def to_tsv(self, sep="\t"):
        return "\n".join(sep.join(str(c) for c in row) for row in self._rows)

    def head(self, n=5):
        if n < 0:
            raise TableError("n for head must be positive value")
        n = len(self._rows) if n > len(self._rows) else n
        return Table(self._rows[:n])

    def tail(self, n=5):
        if n < 0:
            raise TableError("n for tail must be positive value")
        n = len(self._rows) if n > len(self._rows) else n
        if n == 0:
            return Table()
        return Table(self._rows[-n:])

    def select_rows(self, indices):
        try:
            return Table([self._rows[i] for i in indices])
        except IndexError as e:
            raise TableError("unsupported index for select rows") from e
        except TypeError as e:
            raise TableError("indices must be iterable") from e

    def select_columns(self, indices):
        try:
            return Table([[row[i] for i in indices] for row in self._rows])
        except IndexError as e:
            raise TableError("unsupported index for select columns") from e
        except TypeError as e:
            raise TableError("indices must be iterable") from e

    def concat_rows(self, other):
        if self.width is not None and other.width is not None and self.width != other.width:
            raise TableError("tables must have the same width")
        return Table(self._rows + other._rows)

    def concat_cols(self, other):
        if len(self._rows) != len(other._rows):
            raise TableError("tables must be the same length")
        return Table([a + b for a, b in zip(self._rows, other._rows)])

    def __eq__(self, other):
        if not isinstance(other, Table):
            return NotImplemented
        return self._rows == other._rows

    def __len__(self):
        return len(self._rows)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return Table(self._rows[index])
        return list(self._rows[index])

    def __repr__(self):
        return "Table(" + repr(self._rows) + ")"
