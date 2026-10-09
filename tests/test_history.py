import history


def test_history_round_trip(tmp_path, monkeypatch):
    db = tmp_path / "history.db"
    monkeypatch.setattr(history, "DB", str(db))
    history.init_db()

    sample = {
        "time": "2026-10-08T12:00:00",
        "cpu": 12.5, "memory": 44, "disk": 61,
        "processes": [{}, {}], "connections": [{}]
    }
    risk = {
        "score": 10, "level": "low",
        "findings": [{"severity": "info", "reason": "test"}]
    }

    history.record(sample, risk)

    assert history.recent(1)[0]["process_count"] == 2
    assert history.recent(1)[0]["connection_count"] == 1
    assert history.findings(1)[0]["reason"] == "test"
