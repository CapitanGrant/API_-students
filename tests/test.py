import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from jose import jwt
from unittest.mock import patch, MagicMock
from app.users.models import User
from app.users.schemas import SUserAuth
from app.users.router import router


SECRET_KEY = 'gV64m9aIzFG4qpgVphvQbPQrtAO0nM-7YwwOvu0XPt5KJOjAy4AfgLkqJXYEt'

url = 'http://127.0.0.1:8000/auth/register/'
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}


# Моковые DAO
class MockUsersDAO:
    async def find_one_or_none(self, **kwargs):
        if kwargs.get('email') == 'test@example.com':
            return User(id=1, email='test@example.com', password='hashed_password', first_name='Перфвафы',
                        last_name='Ивановка', phone_number='+79491234567', code=None)
        return None

    async def add(self, **kwargs):
        return User(**kwargs)

    async def find_all(self):
        return [
            User(id=1, email='test@example.com', password='hashed_password'),
            User(id=2, phone_number='+79991234567', password='hashed_password')
        ]


class MockReferralCodeDAO:
    async def find_code(self, code: str):
        if code == 'test_code':
            return 'test_code'
        return None

    async def add(self, **kwargs):
        return True


class MockReferralDAO:
    async def add(self, **kwargs):
        return True


# Тестовый клиент
client = TestClient(router)


@pytest.fixture
def mock_users_dao():
    return MockUsersDAO()


@pytest.fixture
def mock_referral_code_dao():
    return MockReferralCodeDAO()


@pytest.fixture
def mock_referral_dao():
    return MockReferralDAO()


@pytest.fixture
def mock_get_current_user(mock_users_dao):
    return User(id=1, email='test@example.com', password='hashed_password')


@pytest.fixture
def mock_get_current_admin_user(mock_users_dao):
    return User(id=1, email='admin@example.com', password='hashed_password', is_admin=True)


class TestAuthRouter:

    @pytest.mark.asyncio
    async def test_register_user_success(self, mock_users_dao, mock_referral_code_dao, mock_referral_dao):
        user_data = {'email': 'test@example.com',
                     'password': 'passw23aras123',
                     'first_name': 'Петр',
                     'last_name': 'Иванов',
                     'phone_number': '+795922343456',
                     'code': None}
        with patch('app.users.dao.UsersDAO', mock_users_dao), \
                patch('app.referal.dao.ReferralCodeDAO', mock_referral_code_dao), \
                patch('app.referal.dao.ReferralDAO', mock_referral_dao):
            response = client.post(url, headers=headers, json=user_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['message'] == 'Вы успешно зарегистрированы!'

    @pytest.mark.asyncio
    async def test_register_user_email_exists(self, mock_users_dao, mock_referral_code_dao, mock_referral_dao):
        user_data = {'email': 'test@example.com',
                     'password': 'passw23aras123',
                     'first_name': 'Петр',
                     'last_name': 'Иванов',
                     'phone_number': '+795922343456',
                     'code': None}

        # Мокируем метод find_one_or_none, чтобы он возвращал существующего пользователя
        with patch('app.users.dao.UsersDAO') as mock_users_dao_patch:
            mock_users_dao_patch.return_value.find_one_or_none.side_effect = lambda **kwargs: User(**user_data)

            with patch('app.referal.dao.ReferralCodeDAO', mock_referral_code_dao), \
                    patch('app.referal.dao.ReferralDAO', mock_referral_dao):
                try:
                    client.post(url, headers=headers, json=user_data)
                except HTTPException as e:
                    # Проверяем, что выбрасывается HTTPException с ожидаемым статусом и сообщением
                    assert e.status_code == 409
                    assert e.detail == 'Пользователь уже существует'
                finally:
                    mock_users_dao_patch.reset_mock()

    @pytest.mark.asyncio
    async def test_register_user_email_exists_two(self, mock_users_dao, mock_referral_code_dao, mock_referral_dao):
        user_data = {'email': 'test@example.com',
                     'password': 'passw23aras123',
                     'first_name': 'Петр',
                     'last_name': 'Иванов',
                     'phone_number': '+795922343456',
                     'code': None}
        with patch('app.users.dao.UsersDAO', mock_users_dao), \
                patch('app.referal.dao.ReferralCodeDAO', mock_referral_code_dao), \
                patch('app.referal.dao.ReferralDAO', mock_referral_dao):
            try:
                client.post(url, headers=headers, json=user_data)
            except HTTPException as e:
                assert e.status_code == 409
                assert e.detail == 'Пользователь с таким номером телефона уже существует'

    @pytest.mark.asyncio
    async def test_register_user_invalid_referral_code(self, mock_users_dao, mock_referral_code_dao, mock_referral_dao):
        user_data = {'email': 'test@example.com',
                     'password': 'passw23aras123',
                     'first_name': 'Петр',
                     'last_name': 'Иванов',
                     'phone_number': '+795922343456',
                     'code': '124578'}
        with patch('app.users.dao.UsersDAO', mock_users_dao), \
                patch('app.referal.dao.ReferralCodeDAO', mock_referral_code_dao), \
                patch('app.referal.dao.ReferralDAO', mock_referral_dao):
            try:
                client.post(url, headers=headers, json=user_data)
            except HTTPException as e:
                assert e.status_code == 404
                assert e.detail == 'Реферальный код который вы ввели не существует'

    @pytest.mark.asyncio
    async def test_auth_user_success(self, mock_users_dao):
        user_data = SUserAuth(email='test@example.com', password='passw23aras123')
        with patch('app.users.dao.UsersDAO', mock_users_dao), \
                patch('app.users.auth.authenticate_user',
                      MagicMock(return_value=User(id=1, email='test@example.com', password='passw23aras123'))), \
                patch('app.users.auth.create_access_token', MagicMock(return_value='test_token')):
            response = client.post('/auth/login/', json=user_data.dict())
        decoded_token = jwt.decode(token=response.json()['access_token'], key=SECRET_KEY, algorithms=['HS256'])
        assert response.status_code == status.HTTP_200_OK
        assert decoded_token['sub'] == '28'
        assert response.json()['refresh_token'] is None


    @pytest.mark.asyncio
    async def test_auth_user_failed(self, mock_users_dao):
        user_data = SUserAuth(email='test@example.com', password='wrong_password')
        with patch('app.users.dao.UsersDAO', mock_users_dao), \
                patch('app.users.auth.authenticate_user', MagicMock(return_value=None)):
            try:
                response = client.post('/auth/login/', json=user_data.dict())
            except HTTPException as e:
                assert e.status_code == status.HTTP_401_UNAUTHORIZED
                assert e.detail == 'Неверная почта или пароль'

    @pytest.mark.asyncio
    async def test_auth_user_failed_mail(self, mock_users_dao):
        user_data = SUserAuth(email='test_wrong@example.com', password='passw23aras123')
        with patch('app.users.dao.UsersDAO', mock_users_dao), \
                patch('app.users.auth.authenticate_user', MagicMock(return_value=None)):
            try:
                response = client.post('/auth/login/', json=user_data.dict())
            except HTTPException as e:
                assert e.status_code == status.HTTP_401_UNAUTHORIZED
                assert e.detail == 'Неверная почта или пароль'

    @pytest.mark.asyncio
    async def test_get_me(mock_users_dao, mock_get_current_user):
        user_data = SUserAuth(email='test@example.com', password='passw23aras123')
        with patch('app.users.dao.UsersDAO', mock_users_dao), \
                patch('app.users.auth.create_access_token', return_value='test_token'), \
                patch('app.users.auth.authenticate_user',
                      MagicMock(return_value=User(id=1, email='test@example.com', password='passw23aras123'))), \
                patch('app.users.auth.create_access_token', return_value='test_token'), \
                patch('app.users.dependencies.get_current_user', return_value=mock_get_current_user):
            response = client.get('/auth/me/')
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data['id'] == 1
            assert data['email'] == 'test@example.com'
#
# @pytest.mark.asyncio
# async def test_logout_user(self, mock_get_current_user):
#     with patch('app.users.dependencies.get_current_user', MagicMock(return_value=mock_get_current_user)):
#         response = client.post('/auth/logout/')
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json()['message'] == 'Пользователь успешно вышел из системы'
#     assert response.cookies.get('users_access_token') is None
#
# @pytest.mark.asyncio
# async def test_get_all_users(self, mock_users_dao, mock_get_current_admin_user):
#     with patch('app.users.dao.UsersDAO', mock_users_dao), \
#             patch('app.users.dependencies.get_current_admin_user',
#                   MagicMock(return_value=mock_get_current_admin_user)):
#         response = client.get('/auth/all_users/')
#     assert response.status_code == status.HTTP_200_OK
#     assert len(response.json()) == 2
#     assert response.json()[0]['id'] == 1
#     assert response.json()[0]['email'] == 'test@example.com'
#     assert response.json()[1]['id'] == 2
#     assert response.json()[1]['phone_number'] == '+79991234567'
