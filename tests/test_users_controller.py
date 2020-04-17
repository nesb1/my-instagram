from http import HTTPStatus

from final_project.data_access_layer.users import UsersDataAccessLayer
from final_project.exceptions import UsersDALError
from final_project.messages import Message
from requests import Response
from starlette.testclient import TestClient


def test_add_user_returns_error_message_when_error_raised(
    client: TestClient, in_user, mocker
):
    mocker.patch.object(UsersDataAccessLayer, 'add_user').side_effect = UsersDALError(
        Message.USER_ALREADY_EXISTS.value
    )
    response: Response = client.post('/users/', json=dict(in_user))
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['message'] == Message.USER_ALREADY_EXISTS.value
