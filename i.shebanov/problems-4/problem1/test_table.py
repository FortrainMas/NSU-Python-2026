import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from main import main, parse_columns
from table import Table, TableError


class TestTable(unittest.TestCase):
    def setUp(self):
        self.t = Table([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])

    def test_head(self):
        self.assertEqual(self.t.head(2), Table([[1, 2, 3], [4, 5, 6]]))
        self.assertEqual(self.t.head(0), Table())
        self.assertEqual(self.t.head(100), self.t)
        self.assertEqual(Table().head(3), Table())

    def test_tail(self):
        self.assertEqual(self.t.tail(2), Table([[7, 8, 9], [10, 11, 12]]))
        self.assertEqual(self.t.tail(0), Table())
        self.assertEqual(self.t.tail(100), self.t)
        self.assertEqual(Table().tail(3), Table())
        

    def test_select_rows(self):
        self.assertEqual(self.t.select_rows([2, 0, 0]), Table([[7, 8, 9], [1, 2, 3], [1, 2, 3]]))
        self.assertEqual(self.t.select_rows([]), Table())
        self.assertEqual(self.t.select_rows([-1]), Table([[10, 11, 12]]))

    def test_select_columns(self):
        self.assertEqual(self.t.select_columns([2, 0]), Table([[3, 1], [6, 4], [9, 7], [12, 10]]))
        self.assertEqual(self.t.select_columns([0, 0]), Table([[1, 1], [4, 4], [7, 7], [10, 10]]))
        self.assertEqual(self.t.select_columns([]), Table([[], [], [], []]))
        self.assertEqual(Table().select_columns([0]), Table())

    def test_select_columns_negative(self):
        self.assertEqual(self.t.select_columns([-1]), Table([[3], [6], [9], [12]]))
        self.assertEqual(
            self.t.select_columns([-1, -3]),
            Table([[3, 1], [6, 4], [9, 7], [12, 10]]),
        )

    def test_concat_rows(self):
        a = Table([[1, 2]])
        b = Table([[3, 4], [5, 6]])
        self.assertEqual(a.concat_rows(b), Table([[1, 2], [3, 4], [5, 6]]))
        self.assertEqual(a.concat_rows(Table()), a)
        self.assertEqual(Table().concat_rows(Table()), Table())
        
        with self.assertRaises(TableError):
            a = Table([1,2,3])
            a.concat_rows(b)

    def test_concat_cols(self):
        a = Table([[1, 2], [3, 4]])
        b = Table([[5], [6]])
        self.assertEqual(a.concat_cols(b), Table([[1, 2, 5], [3, 4, 6]]))
        self.assertEqual(Table().concat_cols(Table()), Table())
        
        with self.assertRaises(TableError):
            a = Table([1,2,3])
            a.concat_cols(b)

    def test_from_tsv_basic(self):
        text = "a\tb\tc\n1\t2\t3\n4\t5\t6"
        self.assertEqual(
            Table.from_tsv(text),
            Table([["a", "b", "c"], ["1", "2", "3"], ["4", "5", "6"]]),
        )

    def test_from_tsv_trailing_newline(self):
        self.assertEqual(Table.from_tsv("a\tb\n1\t2\n"), Table([["a", "b"], ["1", "2"]]))

    def test_from_tsv_custom_sep(self):
        self.assertEqual(
            Table.from_tsv("a;b\n1;2", sep=";"),
            Table([["a", "b"], ["1", "2"]]),
        )

    def test_from_tsv_empty(self):
        self.assertEqual(Table.from_tsv(""), Table())
        self.assertEqual(Table.from_tsv("\n"), Table())

    def test_from_tsv_ragged_raises(self):
        with self.assertRaises(TableError):
            Table.from_tsv("a\tb\tc\n1\t2")

    def test_to_tsv(self):
        t = Table([["a", "b"], ["1", "2"]])
        self.assertEqual(t.to_tsv(), "a\tb\n1\t2")
        self.assertEqual(t.to_tsv(sep=";"), "a;b\n1;2")
        self.assertEqual(Table().to_tsv(), "")

    def test_tsv_roundtrip(self):
        text = "x\ty\tz\n1\t2\t3\n4\t5\t6"
        self.assertEqual(Table.from_tsv(text).to_tsv(), text)

    def test_dunder(self):
        self.assertEqual(len(self.t), 4)
        self.assertEqual(self.t[1], [4, 5, 6])
        self.assertEqual(self.t[1:3], Table([[4, 5, 6], [7, 8, 9]]))
        self.assertEqual(list(self.t), [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
        self.assertNotEqual(self.t, [[1, 2, 3]])


class TempFiles:
    def __init__(self):
        self._paths = []

    def make(self, content):
        fd, path = tempfile.mkstemp(suffix=".tsv", text=True)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        self._paths.append(path)
        return path

    def cleanup(self):
        for p in self._paths:
            try:
                os.remove(p)
            except OSError:
                pass


def run_cli(argv):
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = TempFiles()

    def tearDown(self):
        self.tmp.cleanup()

    def test_head(self):
        p = self.tmp.make("a\tb\n1\t2\n3\t4\n5\t6\n")
        code, out, _ = run_cli(["head", "-n", "2", p])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip("\n"), "a\tb\n1\t2")

    def test_tail(self):
        p = self.tmp.make("a\tb\n1\t2\n3\t4\n5\t6\n")
        code, out, _ = run_cli(["tail", "-n", "2", p])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip("\n"), "3\t4\n5\t6")

    def test_cut(self):
        p = self.tmp.make("a\tb\tc\n1\t2\t3\n4\t5\t6\n")
        code, out, _ = run_cli(["cut", "-f", "1,1,3,2", p])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip("\n"), "a\ta\tc\tb\n1\t1\t3\t2\n4\t4\t6\t5")

    def test_cut_negative(self):
        p = self.tmp.make("a\tb\tc\n1\t2\t3\n")
        code, out, _ = run_cli(["cut", "-f=-1,-3", p])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip("\n"), "c\ta\n3\t1")

    def test_paste(self):
        p1 = self.tmp.make("a\tb\n1\t2\n3\t4\n")
        p2 = self.tmp.make("c\n5\n6\n")
        code, out, _ = run_cli(["paste", p1, p2])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip("\n"), "a\tb\tc\n1\t2\t5\n3\t4\t6")

    def test_paste_three_files(self):
        p1 = self.tmp.make("1\n2\n")
        p2 = self.tmp.make("a\nb\n")
        p3 = self.tmp.make("x\ty\nz\tw\n")
        code, out, _ = run_cli(["paste", p1, p2, p3])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip("\n"), "1\ta\tx\ty\n2\tb\tz\tw")

    def test_parse_columns_accepts_duplicates(self):
        self.assertEqual(parse_columns("1,1,3,2"), [0, 0, 2, 1])

    def test_parse_columns_negative(self):
        self.assertEqual(parse_columns("-1,-2"), [-1, -2])
        self.assertEqual(parse_columns("1,-1"), [0, -1])

    def test_custom_sep(self):
        p = self.tmp.make("a;b;c\n1;2;3\n")
        code, out, _ = run_cli(["--sep", ";", "cut", "-f", "1,3", p])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip("\n"), "a;c\n1;3")

    def test_ragged_input_fails(self):
        p = self.tmp.make("a\tb\tc\n1\t2\n")
        code, _, err = run_cli(["head", "-n", "5", p])
        self.assertEqual(code, 1)
        self.assertIn("error", err)

    def test_cut_out_of_range_fails(self):
        p = self.tmp.make("a\tb\n1\t2\n")
        code, _, err = run_cli(["cut", "-f", "5", p])
        self.assertEqual(code, 1)
        self.assertIn("error", err)

    def test_cut_negative_out_of_range_fails(self):
        p = self.tmp.make("a\tb\n1\t2\n")
        code, _, err = run_cli(["cut", "-f=-5", p])
        self.assertEqual(code, 1)
        self.assertIn("error", err)

    def test_missing_file(self):
        code, _, err = run_cli(["head", "/nonexistent/path/xyz.tsv"])
        self.assertEqual(code, 1)
        self.assertIn("error", err)

    def test_paste_row_count_mismatch(self):
        p1 = self.tmp.make("1\n2\n")
        p2 = self.tmp.make("a\nb\nc\n")
        code, _, err = run_cli(["paste", p1, p2])
        self.assertEqual(code, 1)
        self.assertIn("error", err)

    def test_invalid_columns_arg(self):
        p = self.tmp.make("a\tb\n1\t2\n")
        with self.assertRaises(SystemExit):
            run_cli(["cut", "-f", "0", p])
        with self.assertRaises(SystemExit):
            run_cli(["cut", "-f", "abc", p])


if __name__ == "__main__":
    unittest.main()
