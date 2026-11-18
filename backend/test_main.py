from fastapi.testclient import TestClient

import main

client = TestClient(main.app)

def test_health():
    respose = client.get("/api/health")
    assert respose.status_code == 200
    assert respose.json() == {"status": "ok"}

def test_unreachable_site_is_down():
    result = main.check_sites("http://localhost:1")
    assert result["up"] is False
    assert result["status_code"] is None

def test_status_returns_sites(monkeypatch):
    def fake_check(url):
        return {"url": url, "up": True, "status_code": 200, "response_ms": 10}
    
    monkeypatch.setattr(main, "check_sites", fake_check)
    monkeypatch.setattr(main, "SITES", ["http://example.com"])
    main.cache["time"] = 0

    response = client.get("/api/status")
    assert response.status_code == 200
    assert response.json()["sites"][0]["up"] is True