import pytest
from django.contrib.auth import authenticate


@pytest.mark.django_db
def test_success_register_user(api_client):
    response = api_client.post(
        "/register/",
        {
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "father_name": "James",
            "email": "admin@admin.com",
            "password": "Test1user",
            "password_confirm": "Test1user"
        }
    )

    assert response.status_code == 200
    assert response.data["user"]["last_name"] == "Ivanov"


@pytest.mark.django_db
def test_not_valid_serializer_register_user(api_client):
    response = api_client.post(
        "/register/",
        {
            "first_name": "Ivan",
            "email": "admin@admin.com",
            "password": "Test1user",
            "password_confirm": "Test1user"
        }
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_fail_register_user_with_exists_email(api_client, register_user):
    register_user(first_name="Sergey", last_name="Ivanov",
                  father_name="Serge", email="admin@admin.com", password="123")
    response = api_client.post(
        "/register/",
        {
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "father_name": "James",
            "email": "admin@admin.com",
            "password": "Test1user",
            "password_confirm": "Test1user"
        }
    )

    assert response.status_code == 400
    assert response.data["message"] == "Пользователь с таким email уже зарегистрирован!"


@pytest.mark.django_db
def test_fail_register_user_password_dismatch(api_client):
    response = api_client.post(
        "/register/",
        {
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "father_name": "James",
            "email": "admin@admin.com",
            "password": "Test1user",
            "password_confirm": "Test1user1"
        }
    )

    assert response.status_code == 400
    assert response.data["message"] == "Пароли не совпадают!"


@pytest.mark.django_db
def test_success_auth(api_client, register_user, add_token):

    token = add_token()
    api_client.force_authenticate(token=token, user=token.user)

    assert token.user.is_authenticated


@pytest.mark.django_db
def test_fail_auth_user_invalid_serializer(api_client):
    response = api_client.post(
        "/signin/",
        {
            "email": "v3dok94",
            "password": "Password"
        }
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_fail_auth_user_invalid_user_data(api_client, register_user):

    register_user(first_name="Ivan", last_name="Ivanov", father_name="James",
                  email="admin@admin.com", password="Password")

    response = api_client.post(
        "/signin/",
        {
            "email": "admin@admin.com",
            "password": "password"
        }
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_fail_send_mail_password_reset(api_client):
    response = api_client.post(
        "/send-mail-password-reset/",
        {
            "email": "james@bond.com"
        }
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_success_password_refresh(api_client, add_token):
    token = add_token()
    api_client.force_authenticate(token=token, user=token.user)

    response = api_client.post(
        "/password-refresh/",
        {
            "password": "NewPassword123",
            "password_confirm": "NewPassword123"
        }
    )

    assert response.status_code == 200
    assert response.data["detail"] == "Пароль успешно изменен"


@pytest.mark.django_db
def test_fail_password_refresh_password_dismatch(api_client, add_token):
    token = add_token()
    api_client.force_authenticate(token=token, user=token.user)

    response = api_client.post(
        "/password-refresh/",
        {
            "password": "NewPassword123",
            "password_confirm": "NewPassword12"
        }
    )

    assert response.status_code == 400
    assert response.data["detail"] == "Пароли не совпадают!"


@pytest.mark.django_db
def test_set_short_password_in_refresh_password_url(api_client, add_token):
    token = add_token()
    api_client.force_authenticate(token=token, user=token.user)

    response = api_client.post(
        "/password-refresh/",
        {
            "password": "123",
            "password_confirm": "123"
        }
    )

    assert response.status_code == 400
    assert response.data["detail"] == "Пароль должен состоять из минимум 8 символов"


@pytest.mark.django_db
def test_fail_password_reset(api_client):
    response = api_client.post(
        "/password-reset/",
        {
            "user_id": "1",
            "timestamp": "123421421344",
            "signature": "AbcD1234",
            "password": "NewPassword"
        }
    )

    assert response.status_code == 400
    assert response.data["detail"] == "Неверные данные"


@pytest.mark.django_db
def test_get_profile(api_client, add_token):
    token = add_token()
    api_client.force_authenticate(token=token, user=token.user)

    response = api_client.get("/profile/")

    assert response.status_code == 200
    assert response.data["email"] == token.user.email


@pytest.mark.django_db
def test_success_update_user_profile(api_client, add_token):
    token = add_token()
    api_client.force_authenticate(token=token, user=token.user)

    response = api_client.put(
        "/profile/",
        {
            "email": "admin@admin.com",
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "father_name": "James",
            "subdivision": "Administration",
            "position": "Developer"
        }
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_fail_update_user_profile_invalid_serializer(api_client, add_token):
    token = add_token()
    api_client.force_authenticate(token=token, user=token.user)

    response = api_client.put(
        "/profile/",
        {
            "email": "admin"
        }
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_fail_update_user_profile_cause_email_exists(api_client, add_token, register_user):
    token = add_token()
    api_client.force_authenticate(token=token, user=token.user)
    register_user(first_name="Ivan", last_name="Ivanov", father_name="James",
                  email="admin@admin.com", password="Password")

    response = api_client.put(
        "/profile/",
        {
            "email": "admin@admin.com"
        }
    )
    
    assert response.status_code == 400
    assert response.data["detail"] == "Данный email зарегистрирован на другого пользователя"
