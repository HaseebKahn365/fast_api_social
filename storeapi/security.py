import datetime
from jose import jwt
from security import *  # noqa: F401,F403
from security import SECRET_KEY, ALGORITHM

# Wrappers so tests patching storeapi.security.* affect underlying behavior

def access_token_expire_minutes() -> int:  # type: ignore[override]
	from security import access_token_expire_minutes as _a
	return _a()


def confirm_token_expire_minutes() -> int:  # type: ignore[override]
	from security import confirm_token_expire_minutes as _c
	return _c()


def create_access_token(email: str):  # type: ignore[override]
	expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
		minutes=access_token_expire_minutes()
	)
	jwt_data = {"sub": email, "exp": expire, "type": "access"}
	return jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)


def create_confirmation_token(email: str):  # type: ignore[override]
	expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
		minutes=confirm_token_expire_minutes()
	)
	jwt_data = {"sub": email, "exp": expire, "type": "confirmation"}
	return jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)


