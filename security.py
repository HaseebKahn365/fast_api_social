from database import database, user_table # type: ignore
import logging

logger = logging.getLogger(__name__)

async def get_user(email: str):
    logger.debug(f"Fetching user with email: {email}")
    query = user_table.select().where(user_table.c.email == email)
    user = await database.fetch_one(query)
    if user:
        logger.info(f"User found: {user}")
    else:
        logger.warning(f"No user found with email: {email}")
    return user