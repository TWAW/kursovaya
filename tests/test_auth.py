"""
Базовые тесты аутентификации
"""
import pytest
from app import create_app
from app.models import Database, User
from app.config import TestingConfig


@pytest.fixture
def app():
    """Создаём тестовое приложение"""
    app = create_app('testing')
    with app.app_context():
        db = app.db
        # Создаём тестового пользователя если его нет
        if db.session.query(User).count() == 0:
            admin = User(username='test_admin', email='test@test.local', is_admin='1')
            admin.password = 'Test@123'
            db.session.add(admin)
            db.session.commit()
    yield app


@pytest.fixture
def client(app):
    """Тестовый клиент"""
    return app.test_client()


def test_login_page_loads(client):
    """Тест: страница логина доступна"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Войти' in response.data


def test_redirect_to_login_when_not_authenticated(client):
    """Тест: главная страница редиректит на логин без авторизации"""
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location


def test_login_success(client, app):
    """Тест: успешный вход (CSRF отключен в TestingConfig)"""
    with app.app_context():
        response = client.post('/login', data={
            'username': 'test_admin',
            'password': 'Test@123'
        }, follow_redirects=False)
        # После успешного логина редирект на главную
        assert response.status_code == 302
        assert '/' in response.location or 'main.index' in response.location


def test_login_failure(client):
    """Тест: неверные учётные данные"""
    response = client.post('/login', data={
        'username': 'wrong_user',
        'password': 'wrong_pass'
    }, follow_redirects=True)
    # Должен остаться на странице логина или показать ошибку
    assert response.status_code == 200
    assert b'Неверное имя пользователя' in response.data or b'login' in response.data.lower()
