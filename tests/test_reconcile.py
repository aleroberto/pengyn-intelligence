from pathlib import Path

from pengyn_intelligence.reconcile import format_summary, reconcile

FIXTURES = Path(__file__).parent / "fixtures"


def _write_csv(path: Path, header: str, rows: list[str]) -> None:
    path.write_text(header + "\n" + "\n".join(rows) + "\n", encoding="utf-8")


def test_perfect_match(tmp_path: Path) -> None:
    sales = tmp_path / "vendas.csv"
    receipts = tmp_path / "recebimentos.csv"
    _write_csv(sales, "external_id,expected_net", ["PED-1,100.00", "PED-2,50.00"])
    _write_csv(receipts, "external_id,amount", ["PED-1,100.00", "PED-2,50.00"])
    summary = reconcile(sales, receipts)
    assert summary.total_sales == 2
    assert summary.total_receipts == 2
    assert summary.matched_sales == 2
    assert summary.receipts_without_sale == 0
    assert summary.sales_without_receipt == 0
    assert summary.amount_mismatches == 0
    assert summary.divergence_total_cents == 0


def test_sale_without_receipt(tmp_path: Path) -> None:
    sales = tmp_path / "vendas.csv"
    receipts = tmp_path / "recebimentos.csv"
    _write_csv(sales, "external_id,expected_net", ["PED-1,40.00"])
    _write_csv(receipts, "external_id,amount", [])
    summary = reconcile(sales, receipts)
    assert summary.sales_without_receipt == 1
    assert summary.divergence_total_cents == 4000


def test_receipt_without_sale(tmp_path: Path) -> None:
    sales = tmp_path / "vendas.csv"
    receipts = tmp_path / "recebimentos.csv"
    _write_csv(sales, "external_id,expected_net", [])
    _write_csv(receipts, "external_id,amount", ["PED-9,15.50"])
    summary = reconcile(sales, receipts)
    assert summary.receipts_without_sale == 1
    assert summary.divergence_total_cents == 1550


def test_amount_mismatch(tmp_path: Path) -> None:
    sales = tmp_path / "vendas.csv"
    receipts = tmp_path / "recebimentos.csv"
    _write_csv(sales, "external_id,expected_net", ["PED-1,80.00"])
    _write_csv(receipts, "external_id,amount", ["PED-1,70.00"])
    summary = reconcile(sales, receipts)
    assert summary.matched_sales == 0
    assert summary.amount_mismatches == 1
    assert summary.divergence_total_cents == 1000


def test_last_row_wins_for_duplicate_id(tmp_path: Path) -> None:
    sales = tmp_path / "vendas.csv"
    receipts = tmp_path / "recebimentos.csv"
    _write_csv(sales, "external_id,expected_net", ["PED-1,10.00", "PED-1,20.00"])
    _write_csv(receipts, "external_id,amount", ["PED-1,20.00"])
    summary = reconcile(sales, receipts)
    assert summary.total_sales == 1
    assert summary.matched_sales == 1
    assert summary.divergence_total_cents == 0


def test_last_row_wins_for_duplicate_receipt_id(tmp_path: Path) -> None:
    sales = tmp_path / "vendas.csv"
    receipts = tmp_path / "recebimentos.csv"
    _write_csv(sales, "external_id,expected_net", ["PED-1,20.00"])
    _write_csv(receipts, "external_id,amount", ["PED-1,10.00", "PED-1,20.00"])
    summary = reconcile(sales, receipts)
    assert summary.total_receipts == 1
    assert summary.matched_sales == 1
    assert summary.amount_mismatches == 0
    assert summary.divergence_total_cents == 0


def test_header_only_csvs_are_all_zeros(tmp_path: Path) -> None:
    sales = tmp_path / "vendas.csv"
    receipts = tmp_path / "recebimentos.csv"
    _write_csv(sales, "external_id,expected_net", [])
    _write_csv(receipts, "external_id,amount", [])
    summary = reconcile(sales, receipts)
    assert summary.total_sales == 0
    assert summary.total_receipts == 0
    assert summary.matched_sales == 0
    assert summary.receipts_without_sale == 0
    assert summary.sales_without_receipt == 0
    assert summary.amount_mismatches == 0
    assert summary.divergence_total_cents == 0
    assert format_summary(summary).splitlines()[-1] == "Valor total das divergências: 0.00"


def test_extra_columns_are_ignored(tmp_path: Path) -> None:
    sales = tmp_path / "vendas.csv"
    receipts = tmp_path / "recebimentos.csv"
    sales.write_text(
        "external_id,channel,expected_net,notes\nPED-1,marketplace,100.00,ok\n",
        encoding="utf-8",
    )
    receipts.write_text(
        "external_id,instrument,amount,extra\nPED-1,acquirer,100.00,ignored\n",
        encoding="utf-8",
    )
    summary = reconcile(sales, receipts)
    assert summary.total_sales == 1
    assert summary.total_receipts == 1
    assert summary.matched_sales == 1
    assert summary.divergence_total_cents == 0


def test_external_id_is_stripped_before_matching(tmp_path: Path) -> None:
    sales = tmp_path / "vendas.csv"
    receipts = tmp_path / "recebimentos.csv"
    _write_csv(sales, "external_id,expected_net", ["PED-1 ,100.00"])
    _write_csv(receipts, "external_id,amount", [" PED-1,100.00"])
    summary = reconcile(sales, receipts)
    assert summary.total_sales == 1
    assert summary.total_receipts == 1
    assert summary.matched_sales == 1
    assert summary.divergence_total_cents == 0


def test_zero_amounts_on_both_sides_are_matched(tmp_path: Path) -> None:
    sales = tmp_path / "vendas.csv"
    receipts = tmp_path / "recebimentos.csv"
    _write_csv(sales, "external_id,expected_net", ["PED-1,0.00"])
    _write_csv(receipts, "external_id,amount", ["PED-1,0.00"])
    summary = reconcile(sales, receipts)
    assert summary.matched_sales == 1
    assert summary.sales_without_receipt == 0
    assert summary.receipts_without_sale == 0
    assert summary.amount_mismatches == 0
    assert summary.divergence_total_cents == 0


def test_blank_external_id_is_not_used_as_key(tmp_path: Path) -> None:
    sales = tmp_path / "vendas.csv"
    receipts = tmp_path / "recebimentos.csv"
    _write_csv(sales, "external_id,expected_net", [",100.00", "   ,50.00", "PED-1,40.00"])
    _write_csv(receipts, "external_id,amount", [" ,20.00", "PED-1,40.00"])
    summary = reconcile(sales, receipts)
    assert summary.total_sales == 1
    assert summary.total_receipts == 1
    assert summary.matched_sales == 1
    assert summary.divergence_total_cents == 0


def test_combined_fixture_totals() -> None:
    summary = reconcile(FIXTURES / "vendas.csv", FIXTURES / "recebimentos.csv")
    assert summary.total_sales == 4
    assert summary.total_receipts == 4
    assert summary.matched_sales == 2
    assert summary.receipts_without_sale == 1
    assert summary.sales_without_receipt == 1
    assert summary.amount_mismatches == 1
    assert summary.divergence_total_cents == 6000
    assert format_summary(summary).splitlines()[-1] == "Valor total das divergências: 60.00"
