from setuptools import setup, find_packages

setup(
    name="todo-backend",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "sqlmodel",
        "pydantic",
        "pyjwt",
        "python-dotenv",
        "psycopg-binary",
        "python-multipart",
        "sqlalchemy",
        "python-jose",
        "psycopg2-binary",
        "passlib[bcrypt]",
        "bcrypt",
        "openai",
        "cohere",
        "mcp",
    ],
    author="Todo App Developer",
    description="Todo Backend API",
    python_requires=">=3.7",
)