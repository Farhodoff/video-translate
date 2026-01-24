
def test_read_root(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_dashboard(test_client):
    response = test_client.get("/dashboard")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_favicon(test_client):
    response = test_client.get("/favicon.ico")
    assert response.status_code == 200
