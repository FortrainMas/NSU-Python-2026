import itertools
import unittest

from descartes import Descartes


class TestDescartes(unittest.TestCase):
    def test_simple(self):
        d = Descartes([1, "a"], 2)
        produced = []
        for _ in range(4):
            produced.append(d.current())
            d.advance()
        self.assertEqual(
            produced,
            [(1, 1), (1, "a"), ("a", 1), ("a", "a")],
        )

    def test_matches_itertools_product(self):
        x = [1, 2, 3]
        n = 3
        expected = list(itertools.product(x, repeat=n))
        d = Descartes(x, n)
        produced = []
        for _ in range(len(expected)):
            produced.append(d.current())
            d.advance()
        self.assertEqual(produced, expected)

    def test_cycling(self):
        d = Descartes(["a", "b"], 2)
        size = 2 ** 2
        first = []
        for _ in range(size):
            first.append(d.current())
            d.advance()
        second = []
        for _ in range(size):
            second.append(d.current())
            d.advance()
        self.assertEqual(first, second)

    def test_cycle_after_extra_calls(self):
        d = Descartes([0, 1], 3)
        for _ in range(2 ** 3 * 2 + 3):
            d.advance()
        self.assertEqual(d.current(), (0, 1, 1))

    def test_n_zero(self):
        d = Descartes([1, 2, 3], 0)
        self.assertEqual(d.current(), ())
        d.advance()
        self.assertEqual(d.current(), ())

    def test_singleton_x(self):
        d = Descartes(["x"], 4)
        self.assertEqual(d.current(), ("x", "x", "x", "x"))
        d.advance()
        self.assertEqual(d.current(), ("x", "x", "x", "x"))

    def test_full_enumeration_unique(self):
        x = ["a", "b", "c", "d"]
        n = 3
        d = Descartes(x, n)
        produced = set()
        for _ in range(len(x) ** n):
            produced.add(d.current())
            d.advance()
        self.assertEqual(len(produced), len(x) ** n)

    def test_lexicographic_order(self):
        d = Descartes([0, 1, 2], 2)
        produced = []
        for _ in range(9):
            produced.append(d.current())
            d.advance()
        self.assertEqual(produced, sorted(produced))

    def test_input_list_mutation_does_not_affect_state(self):
        x = [1, 2]
        d = Descartes(x, 2)
        x.append(3)
        produced = []
        for _ in range(4):
            produced.append(d.current())
            d.advance()
        self.assertEqual(produced, [(1, 1), (1, 2), (2, 1), (2, 2)])

    def test_negative_n_rejected(self):
        with self.assertRaises(ValueError):
            Descartes([1, 2], -1)

    def test_empty_x_with_positive_n_rejected(self):
        with self.assertRaises(ValueError):
            Descartes([], 2)


if __name__ == "__main__":
    unittest.main()
