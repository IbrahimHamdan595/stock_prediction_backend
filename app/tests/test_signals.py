import datetime as dt

import pytest

from app.services.signal_service import SignalService


@pytest.mark.asyncio
async def test_signal_generation_uses_defaults(monkeypatch):
    class FakeCollection:
        def __init__(self):
            self.saved = []

        async def insert_one(self, doc):
            self.saved.append(doc)

        def find(self, *_args, **_kwargs):
            return []

    service = SignalService(db=type("db", (), {"signals": FakeCollection()})())
    payload = type("SignalIn", (), {"symbol": "AAPL", "strategy_id": "strat", "timestamp": dt.datetime.utcnow(), "timeframe": "1d"})()
    signals = await service.generate(payload)
    assert signals and signals[0].symbol == "AAPL"
    assert signals[0].take_profit > signals[0].entry_price
