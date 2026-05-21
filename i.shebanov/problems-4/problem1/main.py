import argparse
import sys

from table import Table, TableError


def parse_columns(text):
    try:
        nums = [int(x) for x in text.split(",") if x != ""]
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"invalid column list: {text!r} (expected comma-separated integers)"
        )
    if not nums:
        raise argparse.ArgumentTypeError("column list is empty")
    for n in nums:
        if n == 0:
            raise argparse.ArgumentTypeError(
                "column numbers are 1-based; use negatives to index from the end"
            )
    return [n - 1 if n > 0 else n for n in nums]


def read_table(path, sep):
    with open(path, "r", encoding="utf-8") as f:
        return Table.from_tsv(f.read(), sep=sep)


def cmd_head(args):
    t = read_table(args.file, args.sep)
    return t.head(args.n)


def cmd_tail(args):
    t = read_table(args.file, args.sep)
    return t.tail(args.n)


def cmd_cut(args):
    t = read_table(args.file, args.sep)
    return t.select_columns(args.fields)


def cmd_paste(args):
    tables = [read_table(p, args.sep) for p in args.files]
    if not tables:
        return Table()
    result = tables[0]
    for t in tables[1:]:
        result = result.concat_cols(t)
    return result


def build_parser():
    parser = argparse.ArgumentParser(
        prog="table.py",
        description="Утилита для работы с таблицами (head/tail/cut/paste).",
    )
    parser.add_argument(
        "--sep",
        default="\t",
        help="разделитель столбцов (по умолчанию таб)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_head = sub.add_parser("head", help="первые N строк")
    p_head.add_argument("-n", type=int, default=5)
    p_head.add_argument("file")
    p_head.set_defaults(func=cmd_head)

    p_tail = sub.add_parser("tail", help="последние N строк")
    p_tail.add_argument("-n", type=int, default=5)
    p_tail.add_argument("file")
    p_tail.set_defaults(func=cmd_tail)

    p_cut = sub.add_parser("cut", help="выборка столбцов")
    p_cut.add_argument(
        "-f",
        dest="fields",
        type=parse_columns,
        required=True,
        help="список столбцов (нумерация с 1), например 1,3,2",
    )
    p_cut.add_argument("file")
    p_cut.set_defaults(func=cmd_cut)

    p_paste = sub.add_parser("paste", help="соединение таблиц по столбцам")
    p_paste.add_argument("files", nargs="+")
    p_paste.set_defaults(func=cmd_paste)

    return parser


def main(argv=None):
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except argparse.ArgumentTypeError as e:
        print(f"error: {e}", file=sys.stderr)

    try:
        result = args.func(args)
    except TableError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"error: file not found: {e.filename}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(result.to_tsv(sep=args.sep))
    return 0


if __name__ == "__main__":
    sys.exit(main())
