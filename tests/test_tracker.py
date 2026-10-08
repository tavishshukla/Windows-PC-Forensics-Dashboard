from tracker import compare
import tracker


def test_tracker_initializes():
    tracker._previous = None
    result = compare({"processes": [], "connections": [], "services": [], "startup": []})
    assert result["initialized"] is True


def test_tracker_detects_process_and_connection_changes():
    tracker._previous = None
    base = {
        "processes": [{"pid": 10, "name": "old.exe"}],
        "connections": [{"pid": 10, "local": "127.0.0.1:1", "remote": "1.1.1.1:443", "status": "ESTABLISHED"}],
        "services": [{"Name": "Demo", "Status": "Running"}],
        "startup": [],
    }
    compare(base)
    current = {
        "processes": [{"pid": 11, "name": "new.exe"}],
        "connections": [{"pid": 11, "local": "127.0.0.1:2", "remote": "2.2.2.2:443", "status": "ESTABLISHED"}],
        "services": [{"Name": "Demo", "Status": "Stopped"}],
        "startup": [],
    }
    result = compare(current)
    assert len(result["new_processes"]) == 1
    assert len(result["ended_processes"]) == 1
    assert len(result["new_connections"]) == 1
    assert len(result["ended_connections"]) == 1
    assert result["service_changes"][0]["name"] == "Demo"
