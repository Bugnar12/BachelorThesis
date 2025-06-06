def test_get_all_questions(client, mocker, auth_header):
    mock_questions = [{'id': 1, 'question': 'Q1'}, {'id': 2, 'question': 'Q2'}]
    mocker.patch(
        'routes.quiz_routes.quiz_service.get_random_questions',
        return_value=(mock_questions, 200)
    )
    response = client.get('/quiz/questions', headers=auth_header)
    assert response.status_code == 200


def test_get_question_by_id(client, mocker):
    mock_question = {'id': 1, 'question': 'What is phishing?'}
    mocker.patch(
        'routes.quiz_routes.quiz_service.get_question_by_id',
        return_value=(mock_question, 200)
    )
    response = client.get('/quiz/questions/1')
    assert response.status_code == 200
    assert response.get_json()['question'] == 'What is phishing?'


def test_submit_quiz(client, mocker, auth_header):
    mock_result = {'message': 'Quiz submitted', 'score': 3, 'total': 5}
    mocker.patch(
        'routes.quiz_routes.quiz_service.submit_quiz',
        return_value=(mock_result, 200)
    )

    payload = {
        'answers': [
            {'question_id': 1, 'selected_option': 'option_a'},
            {'question_id': 2, 'selected_option': 'option_b'},
            {'question_id': 3, 'selected_option': 'option_c'}
        ]
    }
    response = client.post('/quiz/submit', headers=auth_header, json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert 'score' in data
    assert data['message'] == 'Quiz submitted'


def test_get_quiz_history(client, mocker, auth_header):
    mock_result = [
        {
            'attempt_no': 1,
            'timestamp': '2024-06-01T12:00:00',
            'score': 2,
            'total': 3,
            'questions': [
                {
                    'text': 'What is phishing?',
                    'userAnswer': 'Fake site',
                    'correctAnswer': 'Fake site'
                }
            ]
        }
    ]
    mocker.patch(
        'routes.quiz_routes.quiz_service.get_history',
        return_value=(mock_result, 200)
    )

    response = client.get('/quiz/history', headers=auth_header)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
