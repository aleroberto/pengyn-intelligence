import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_reconcile_fixture_output() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pengyn_intelligence",
            "reconcile",
            str(FIXTURES / "vendas.csv"),
            str(FIXTURES / "recebimentos.csv"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout == (
        "Total de vendas: 4\n"
        "Total de recebimentos: 4\n"
        "Vendas conciliadas: 2\n"
        "Recebimentos sem venda: 1\n"
        "Vendas sem recebimento: 1\n"
        "Divergências de valor: 1\n"
        "Valor total das divergências: 60.00\n"
    )


def test_cli_missing_file_exits_2(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pengyn_intelligence",
            "reconcile",
            str(tmp_path / "ausente.csv"),
            str(FIXTURES / "recebimentos.csv"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2


def test_cli_missing_second_file_exits_2(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pengyn_intelligence",
            "reconcile",
            str(FIXTURES / "vendas.csv"),
            str(tmp_path / "ausente.csv"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
