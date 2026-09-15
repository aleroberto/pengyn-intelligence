from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


class UnreadableCsvError(Exception):
    pass


@dataclass(frozen=True)
class Summary:
    total_sales: int
    total_receipts: int
    matched_sales: int
    receipts_without_sale: int
    sales_without_receipt: int
    amount_mismatches: int
    divergence_total_cents: int


def parse_money_to_cents(value: str) -> int:
    try:
        amount = Decimal(value.strip())
    except (InvalidOperation, AttributeError) as exc:
        raise UnreadableCsvError(f"valor inválido: {value!r}") from exc
    cents = (amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(cents)


def format_reais(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"


def format_summary(summary: Summary) -> str:
    return "\n".join(
        [
            f"Total de vendas: {summary.total_sales}",
            f"Total de recebimentos: {summary.total_receipts}",
            f"Vendas conciliadas: {summary.matched_sales}",
            f"Recebimentos sem venda: {summary.receipts_without_sale}",
            f"Vendas sem recebimento: {summary.sales_without_receipt}",
            f"Divergências de valor: {summary.amount_mismatches}",
            f"Valor total das divergências: {format_reais(summary.divergence_total_cents)}",
        ]
    )


def _load_amount_by_id(path: Path, amount_column: str) -> dict[str, int]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise UnreadableCsvError(f"CSV sem cabeçalho: {path}")
            if "external_id" not in reader.fieldnames:
                raise UnreadableCsvError(f"coluna external_id ausente: {path}")
            if amount_column not in reader.fieldnames:
                raise UnreadableCsvError(f"coluna {amount_column} ausente: {path}")
            records: dict[str, int] = {}
            for row in reader:
                external_id = (row.get("external_id") or "").strip()
                if not external_id:
                    continue
                records[external_id] = parse_money_to_cents(row.get(amount_column) or "")
            return records
    except OSError as exc:
        raise UnreadableCsvError(str(exc)) from exc


def reconcile(sales_path: str | Path, receipts_path: str | Path) -> Summary:
    sales = _load_amount_by_id(Path(sales_path), "expected_net")
    receipts = _load_amount_by_id(Path(receipts_path), "amount")

    sale_ids = set(sales)
    receipt_ids = set(receipts)
    common_ids = sale_ids & receipt_ids

    matched = 0
    mismatches = 0
    divergence = 0

    for external_id in common_ids:
        expected = sales[external_id]
        received = receipts[external_id]
        if expected == received:
            matched += 1
        else:
            mismatches += 1
            divergence += abs(expected - received)

    only_sales = sale_ids - receipt_ids
    only_receipts = receipt_ids - sale_ids
    divergence += sum(sales[external_id] for external_id in only_sales)
    divergence += sum(receipts[external_id] for external_id in only_receipts)

    return Summary(
        total_sales=len(sales),
        total_receipts=len(receipts),
        matched_sales=matched,
        receipts_without_sale=len(only_receipts),
        sales_without_receipt=len(only_sales),
        amount_mismatches=mismatches,
        divergence_total_cents=divergence,
    )
