# Social App - FastAPI Backend

A simple FastAPI application for managing posts and comments.

## Features

- Create posts
- Get post details by ID
- Add comments to posts
- List all posts

## Project Structure

```
social_app/
├── models/
│   └── post.py              # Pydantic models and data
├── routers/
│   ├── __init__.py          # Package file
│   └── post.py              # Post-related endpoints  
├── main.py                  # FastAPI app entry point
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Ruff configuration
└── .venv/                  # Virtual environment
```

## Setup

1. Create and activate virtual environment:
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## API Endpoints

- `GET /` - Hello World
- `GET /posts` - List all posts
- `POST /posts` - Create a new post
  ```json
  {
    "title": "My New Post"
  }
  ```
- `GET /posts/{post_id}` - Get post by ID
- `POST /posts/{post_id}/comments` - Add comment to post
  ```json
  {
    "content": "Nice post!"
  }
  ```

## Development

The project uses:
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Ruff** - Linting and formatting