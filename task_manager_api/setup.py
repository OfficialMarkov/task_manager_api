"""
Альтернативный способ установки (если pyproject.toml не работает).
Используйте: pip install -e .
"""
from setuptools import setup, find_packages

setup(
    name="task-manager-api",
    version="1.0.0",
    packages=find_packages(exclude=["alembic", "alembic.*", "tests", "tests.*"]),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "sqlalchemy[asyncio]>=2.0.0",
        "asyncpg>=0.29.0",
        "alembic>=1.12.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.6",
        "psycopg2-binary>=2.9.9",
    ],
)
