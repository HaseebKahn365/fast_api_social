import logging

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
import logging
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

from database import user_table, database
from models.user import UserIn
from storeapi.security import (
	authenticate_user,
	create_access_token,
	create_confirmation_token,
	get_password_hash,
	get_user,
	get_subject_for_token_type,
)
from tasks import send_user_registration_email

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", status_code=201)
async def register(user: UserIn, background_tasks: BackgroundTasks, request: Request):
	if await get_user(user.email):
		raise HTTPException(status_code=400, detail="Email already exists")

	hashed_password = get_password_hash(user.password)
	query = user_table.insert().values(email=user.email, password=hashed_password, confirmed=False)
	last_record_id = await database.execute(query)

	# send confirmation email
	token = create_confirmation_token(user.email)
	confirm_url = str(request.base_url) + f"confirm/{token}"
	background_tasks.add_task(send_user_registration_email, user.email, confirmation_url=confirm_url)
	
	logger.debug(f"User registered with ID: {last_record_id}")
	return {"detail": "User created. Please confirm your email."}


@router.post("/token")
async def login(user: UserIn):
	user = await authenticate_user(user.email, user.password)
	access_token = create_access_token(user.email)
	return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token-form")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
	user = await authenticate_user(form_data.username, form_data.password)
	access_token = create_access_token(form_data.username)
	return {"access_token": access_token, "token_type": "bearer"}


@router.post("/confirm")
async def confirm_email(token: str):
	email = get_subject_for_token_type(token, "confirmation")
	query = user_table.update().where(user_table.c.email == email).values(confirmed=True)
	await database.execute(query)
	return {"detail": "User confirmed"}


@router.get("/confirm/{token}")
async def confirm_email_path(token: str):
	email = get_subject_for_token_type(token, "confirmation")
	query = user_table.update().where(user_table.c.email == email).values(confirmed=True)
	await database.execute(query)
	return {"detail": "User confirmed"}
