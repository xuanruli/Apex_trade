import pytest
from datetime import datetime
from app.models.transaction import Transaction


def test_save_insert(monkeypatch):
    called = {}

    def fake_update(q, params):
        called["query"] = q
        called["params"] = params

    monkeypatch.setattr("app.models.transaction.execute_update", fake_update)
    monkeypatch.setattr(
        "app.models.transaction.execute_query",
        lambda q, p: [{"id": 999}],
    )

    tx_date = "2025-04-22"
    t = Transaction(
        user_id=1,
        stock_symbol="AAPL",
        shares=5,
        price_per_share=10.0,
        transaction_type="buy",
        transaction_date=tx_date,
        id=None,
    )
    t.save()

    assert "INSERT INTO transactions" in called["query"]
    assert called["params"] == (1, "AAPL", 5, 10.0, "buy", tx_date)
    assert t._id == 999


def test_save_update(monkeypatch):
    called = {}

    def fake_update(q, params):
        called["query"] = q
        called["params"] = params

    monkeypatch.setattr("app.models.transaction.execute_update", fake_update)

    tx_date = datetime(2025, 4, 20)
    t = Transaction(
        user_id=2,
        stock_symbol="GOOG",
        shares=3,
        price_per_share=20.0,
        transaction_type="sell",
        transaction_date=tx_date,
        id=50,
    )
    t.save()

    assert "UPDATE transactions SET" in called["query"]
    assert called["params"] == (2, "GOOG", 3, 20.0, "sell", tx_date, 50)


def test_get_all_transactions(monkeypatch):
    rows = [
        {
            "id": 1,
            "user_id": 1,
            "stock_symbol": "A",
            "shares": 2,
            "price_per_share": 30.0,
            "transaction_type": "buy",
            "transaction_date": "2025-04-20",
        },
        {
            "id": 2,
            "user_id": 1,
            "stock_symbol": "B",
            "shares": 3,
            "price_per_share": 40.0,
            "transaction_type": "sell",
            "transaction_date": "2025-04-21",
        },
    ]
    monkeypatch.setattr("app.models.transaction.execute_query", lambda q, p: rows)
    result = Transaction.get_all_transactions(1)

    assert len(result) == 2
    assert result[0]["total"] == -(2 * 30.0)
    assert result[1]["total"] == 3 * 40.0
    assert result[0]["stock_symbol"] == "A"
    assert result[1]["transaction_date"] == "2025-04-21"


def test_get_transaction_by_id_none(monkeypatch):
    monkeypatch.setattr("app.models.transaction.execute_query", lambda q, p: [])
    assert Transaction.get_transaction_by_id(5) is None


def test_get_transaction_by_id_found(monkeypatch):
    row = {
        "id": 5,
        "user_id": 2,
        "stock_symbol": "X",
        "shares": 4,
        "price_per_share": 50.0,
        "transaction_type": "buy",
        "transaction_date": "2025-04-22",
    }
    monkeypatch.setattr("app.models.transaction.execute_query", lambda q, p: [row])
    tx = Transaction.get_transaction_by_id(5)

    assert isinstance(tx, Transaction)
    assert tx._id == 5
    assert tx._user_id == 2
    assert tx._stock_symbol == "X"
    assert tx._shares == 4
    assert tx._price_per_share == 50.0
    assert tx._transaction_type == "buy"
    assert tx._transaction_date == "2025-04-22"


def test_get_by_stock_and_user(monkeypatch):
    rows = [
        {
            "id": 7,
            "user_id": 3,
            "stock_symbol": "Z",
            "shares": 1,
            "price_per_share": 100.0,
            "transaction_type": "sell",
            "transaction_date": "2025-04-23",
        },
        {
            "id": 8,
            "user_id": 3,
            "stock_symbol": "Z",
            "shares": 2,
            "price_per_share": 110.0,
            "transaction_type": "buy",
            "transaction_date": "2025-04-24",
        },
    ]
    monkeypatch.setattr("app.models.transaction.execute_query", lambda q, p: rows)
    txs = Transaction.get_by_stock_and_user(3, "Z")

    assert len(txs) == 2
    for obj, row in zip(txs, rows):
        assert isinstance(obj, Transaction)
        assert obj._id == row["id"]


def test_basic_attributes():
    tx_date = datetime(2025, 4, 25)
    t = Transaction(
        user_id=4,
        stock_symbol="Y",
        shares=6,
        price_per_share=25.0,
        transaction_type="buy",
        transaction_date=tx_date,
        id=99,
    )
    assert t._id == 99
    assert t._user_id == 4
    assert t._stock_symbol == "Y"
    assert t._shares == 6
    assert t._price_per_share == 25.0
    assert t._transaction_type == "buy"
    assert t._transaction_date == tx_date
