# Backend Database Migrations

This folder contains Alembic migration scaffolding for the Telegraph Messenger backend.

## Getting started

1. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Generate a new revision after updating models:
   ```bash
   cd backend
   alembic -c alembic.ini revision --autogenerate -m "describe changes"
   ```

3. Apply migrations:
   ```bash
   cd backend
   alembic -c alembic.ini upgrade head
   ```

## Configuration

The migration environment respects the `SQLALCHEMY_DATABASE_URI` environment variable.
If not set, it defaults to `sqlite:///telegraph_messenger.db`.
