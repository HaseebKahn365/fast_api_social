# Re-export tasks under storeapi namespace
import tasks as _orig
from tasks import (
	APIResponseError,
	_generate_cute_creature_api,
	send_simple_email,
)
from databases import Database
from storeapi.database import post_table, database as _db

# Expose httpx for tests that patch 'storeapi.tasks.httpx.AsyncClient'
httpx = _orig.httpx

__all__ = [
	"APIResponseError",
	"_generate_cute_creature_api",
	"generate_and_add_to_post",
	"send_simple_email",
	"httpx",
]


async def generate_and_add_to_post(
	email: str,
	post_id: int,
	post_url: str,
	database: Database,
	prompt: str = "A blue british shorthair cat is sitting on a couch",
):
	try:
		response = await _generate_cute_creature_api(prompt)
	except APIResponseError:
		return await send_simple_email(
			email,
			"Error generating image",
			(
				f"Hi {email}! Unfortunately there was an error generating an image"
				"for your post."
			),
		)

	query = (
		post_table.update()
		.where(post_table.c.id == post_id)
		.values(image_url=response["output_url"])
	)
	await database.execute(query)
	await send_simple_email(
		email,
		"Image generation completed",
		(
			f"Hi {email}! Your image has been generated and added to your post."
			f" Please click on the following link to view it: {post_url}"
		),
	)
	return response


