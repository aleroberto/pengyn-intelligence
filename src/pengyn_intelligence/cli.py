from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pengyn_intelligence.reconcile import UnreadableCsvError, format_summary, reconcile


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pengyn_intelligence")
    subparsers = parser.add_subparsers(dest="command", required=True)
    reconcile_parser = subparsers.add_parser("reconcile")
    reconcile_parser.add_argument("vendas")
    reconcile_parser.add_argument("recebimentos")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    sales_path = Path(args.vendas)
    receipts_path = Path(args.recebimentos)
    if not sales_path.is_file() or not receipts_path.is_file():
        return 2
    try:
        summary = reconcile(sales_path, receipts_path)
    except UnreadableCsvError:
        return 2
    print(format_summary(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
