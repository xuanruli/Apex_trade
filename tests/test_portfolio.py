import pytest
from app.models.portfolio import Portfolio


def _no_rows(*_args, **_kwargs):
    return []


def test_load_holdings(monkeypatch):
    sample = [
        {"stock_symbol": "AAPL", "total_shares": 10, "cost_basis": 1000},
        {"stock_symbol": "TSLA", "total_shares": 5, "cost_basis": 2000},
    ]
    monkeypatch.setattr("app.models.portfolio.execute_query", lambda q, p: sample)
    p = Portfolio(1)
    assert p.holdings == {"AAPL": (10, 1000), "TSLA": (5, 2000)}


def test_update_new_symbol(monkeypatch):
    monkeypatch.setattr("app.models.portfolio.execute_query", _no_rows)
    calls = []
    monkeypatch.setattr(
        "app.models.portfolio.execute_update",
        lambda q, params: calls.append((q, params)),
    )
    p = Portfolio(42)
    assert p.update_portfolio("GOOG", 3, 100.0, "buy") is True
    assert any("INSERT INTO portfolio" in q for q, _ in calls)


def test_update_buy_existing(monkeypatch):
    monkeypatch.setattr("app.models.portfolio.execute_query", _no_rows)
    last = {}
    monkeypatch.setattr(
        "app.models.portfolio.execute_update",
        lambda q, params: last.update({"q": q, "params": params}),
    )
    p = Portfolio(10)
    p._holdings = {"MSFT": (2, 200.0)}
    assert p.update_portfolio("MSFT", 3, 50.0, "buy") is True
    assert "UPDATE portfolio" in last["q"]
    assert last["params"] == (5, 350.0, 10, "MSFT")


def test_update_sell_to_zero(monkeypatch):
    monkeypatch.setattr("app.models.portfolio.execute_query", _no_rows)
    last = {}
    monkeypatch.setattr(
        "app.models.portfolio.execute_update",
        lambda q, params: last.update({"q": q, "params": params}),
    )
    p = Portfolio(7)
    p._holdings = {"NFLX": (4, 400.0)}
    assert p.update_portfolio("NFLX", 4, 120.0, "sell") is True
    assert "DELETE FROM portfolio" in last["q"]


def test_update_invalid_order(monkeypatch):
    monkeypatch.setattr("app.models.portfolio.execute_query", _no_rows)
    p = Portfolio(5)
    p._holdings = {"AMZN": (1, 100.0)}
    with pytest.raises(ValueError):
        p.update_portfolio("AMZN", 1, 200.0, "hold")


def test_get_portfolio_summary(monkeypatch):
    monkeypatch.setattr("app.models.portfolio.execute_query", _no_rows)
    p = Portfolio(1)
    p._holdings = {"AAA": (2, 30.0), "BBB": (3, 90.0)}

    def fake_q(q, params):
        return [{"close_price": 10}] if params[0] == "AAA" else [{"close_price": 20}]

    monkeypatch.setattr("app.models.portfolio.execute_query", fake_q)
    summary = p.get_portfolio_summary()
    assert summary["total_holdings"] == 5
    assert summary["total_value"] == 80.0
    assert summary["total_cost"] == 120.0
    assert summary["total_pl"] == -40.0
    assert pytest.approx(summary["total_pl_percent"], rel=1e-6) == -33.3333333


def test_get_holding_summary(monkeypatch):
    monkeypatch.setattr("app.models.portfolio.execute_query", _no_rows)
    p = Portfolio(2)
    p._holdings = {"X": (4, 200.0)}
    monkeypatch.setattr(
        "app.models.portfolio.execute_query", lambda q, params: [{"close_price": 60.0}]
    )
    result = p.get_holding_summary()
    assert len(result) == 1
    h = result[0]
    assert h["symbol"] == "X"
    assert h["shares"] == 4
    assert h["avg_cost"] == 50.0
    assert h["market_value"] == 240.0
    assert h["gain_loss"] == 40.0
    assert pytest.approx(h["percent_change"], rel=1e-6) == 20.0


def test_check_portfolio(monkeypatch):
    monkeypatch.setattr(
        "app.models.portfolio.execute_query", lambda q, p: [{"count": 0}]
    )
    assert Portfolio.check_portfolio(123) is False
    monkeypatch.setattr(
        "app.models.portfolio.execute_query", lambda q, p: [{"count": 5}]
    )
    assert Portfolio.check_portfolio(123) is True


def test_get_by_user_id(monkeypatch):
    monkeypatch.setattr("app.models.portfolio.execute_query", _no_rows)
    p = Portfolio.get_by_user_id(77)
    assert isinstance(p, Portfolio)
    assert p.user_id == 77


def test_get_holdings_by_symbol(monkeypatch):
    monkeypatch.setattr(
        "app.models.portfolio.execute_query",
        lambda q, p: [{"total_shares": 8, "cost_basis": 800}],
    )
    assert Portfolio.get_holdings_by_symbol(9, "Z") == (8, 800)
    monkeypatch.setattr("app.models.portfolio.execute_query", _no_rows)
    assert Portfolio.get_holdings_by_symbol(9, "Z") is None


def test_get_all_portfolios(monkeypatch):
    data = [{"user_id": 1}, {"user_id": 2}]
    monkeypatch.setattr("app.models.portfolio.execute_query", lambda q, p: data)
    assert Portfolio.get_all_portfolios() == data
