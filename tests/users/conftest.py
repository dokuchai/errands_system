import pytest
from users.models import CustomUser


@pytest.fixture(scope="function")
def register_user():
    def _register_user(first_name:str, last_name:str, father_name:str, email:str, password:str):
        register_user = CustomUser.objects.create(
            first_name=first_name, last_name=last_name, father_name=father_name, email=email, password=password)
        return register_user
    return _register_user
