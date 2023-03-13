from enum import IntEnum


# NOTE: Можно было бы воспользоваться `rest_farmework.status`, но в
#   таком случае наша подсистема зависела бы от этого фреймворка, что
#   нелогично.
class HTTPStatus(IntEnum):
    """Коды HTTP-ответа"""

    HTTP_200_OK = 200
    HTTP_202_ACCEPTED = 202
    HTTP_204_NO_CONTENT = 204

    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_422_UNPROCESSABLE_ENTITY = 422
