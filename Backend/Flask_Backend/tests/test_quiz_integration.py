
def test_get_random_questions(client, auth_header):
    response = client.get('/quiz/questions', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert all("question" in q for q in data)


def test_get_quiz_history(client, auth_header, mocker):
    response = client.get('/quiz/history', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
