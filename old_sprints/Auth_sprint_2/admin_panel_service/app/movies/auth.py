import http
import json
import jwt
import requests
import pybreaker

from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

STAFF_ROLES = ["ADMIN", "MODERATOR"]

User = get_user_model()
circuit_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)


def is_auth_service_up(url):
    try:
        response = requests.get(url)
        return response.status_code == 405
    except requests.exceptions.RequestException:
        return False


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        login_url = settings.AUTH_API_LOGIN_URL
        login_payload = {'email': username, 'password': password}
        if is_auth_service_up(login_url) or circuit_breaker.current_state == pybreaker.STATE_OPEN:
            login_response = requests.post(login_url, data=json.dumps(login_payload))
            if login_response.status_code != http.HTTPStatus.OK:
                return None
            login_response_data = login_response.json()
            access_token = login_response_data.get('access_token')
            decoded_access_token = jwt.decode(access_token, algorithms=['HS256'], options={"verify_signature": False})
            user_id = decoded_access_token.get('sub')

            users_url = settings.AUTH_API_USERS_URL
            user_info_response = requests.get(f'{users_url}/{user_id}',
                                              headers={'Authorization': f'Bearer {access_token}'})
            if user_info_response.status_code != http.HTTPStatus.OK:
                return None
            user_info = user_info_response.json()

            roles_url = settings.AUTH_API_ROLES_URL
            role_info_response = requests.get(f'{roles_url}/{user_info.get("role_id")}',
                                              headers={'Authorization': f'Bearer {access_token}'})
            if role_info_response.status_code != http.HTTPStatus.OK:
                return None
            role_info = role_info_response.json()

            try:
                user, created = User.objects.get_or_create(id=user_info['id'],)
                user.email = user_info.get('email')
                user.first_name = user_info.get('first_name')
                user.last_name = user_info.get('last_name')
                user.is_active = user_info.get('is_deleted') is False
                user.is_admin = role_info.get('name') == "ADMIN"
                user.is_staff = role_info.get('name') in STAFF_ROLES
                user.set_password(password)
                user.save()
            except User.DoesNotExist:
                return None

            return user
        else:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None
            else:
                if user.check_password(password):
                    return user
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
