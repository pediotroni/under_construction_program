def test_send_friend_request():
    response = client.post(
        "/friends/request/09121112222",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert "Friend request sent" in response.json()["message"]

def test_accept_friend_request():
    response = client.post(
        "/friends/respond/1?response=accept",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert "accepted" in response.json()["message"].lower()