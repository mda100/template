import os
import subprocess
import sys


def run_cmd(cmd, cwd=None):
    print(f"\n>>> Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)


def create_next_app(project_name):
  run_cmd(f"npx create-next-app@latest {project_name} --typescript --eslint --tailwind --src-dir --app")


def create_django_app(project_name, app_name):
    os.makedirs(project_name, exist_ok=True)
    run_cmd(f"django-admin startproject {project_name} .", cwd=project_name)
    run_cmd(f"python3 manage.py startapp {app_name}", cwd=project_name)
    # requirements.txt for Django
    with open(os.path.join(project_name, "requirements.txt"), "w") as f:
        f.write("Django>=4.2\npython-dotenv\npsycopg2-binary\npytest\n") #TODO: there should be a configuration file for default dependencies 


def create_docker_files(project_name, project_dir):
    dockerfile_backend = """# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
"""

    dockerfile_frontend = f"""# Frontend Dockerfile
FROM node:18 AS deps
WORKDIR /app
COPY {project_name}/package*.json ./
RUN npm install

FROM node:18 AS dev
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY {project_name}/ ./

# Expose port
EXPOSE 3000

# Start Next.js dev server
CMD ["npm", "run", "dev"]
"""

    compose = f"""version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: {project_name}
    ports:
      - "5432:5432"

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    volumes:
      - ./{project_name}:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
    command: npm run dev
"""

    with open(os.path.join(project_dir, "Dockerfile.backend"), "w") as f:
        f.write(dockerfile_backend)
    with open(os.path.join(project_dir, "Dockerfile.frontend"), "w") as f:
        f.write(dockerfile_frontend)
    with open(os.path.join(project_dir, "docker-compose.yml"), "w") as f:
        f.write(compose)


def create_env_files(project_name, project_dir):
    env_content =f"""
DEBUG=True
DATABASE_URL=postgres://postgres:postgres@db:5432/{project_name}
"""
    with open(os.path.join(project_dir, ".env"), "w") as f:
        f.write(env_content)


def init_terraform(project_dir):
    tf_main = """terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
provider "aws" {
  region = "us-east-1"
}
"""
    with open(os.path.join(project_dir, "main.tf"), "w") as f:
        f.write(tf_main)
    run_cmd("terraform init", cwd=project_dir)


def create_readme(project_name, project_dir):
    readme = f"""# {project_name}

## Overview

project template

## Quickstart

# Start containers
docker-compose up --build

# Run Django migrations
docker-compose exec backend python3 manage.py migrate

## Services
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Database: postgres://postgres:postgres@localhost:5432/{project_name}
"""
    with open(os.path.join(project_dir, "README.md"), "w") as f:
        f.write(readme)


def init_git(project_dir):
    run_cmd("git init", cwd=project_dir)
    with open(os.path.join(project_dir, ".gitignore"), "w") as f:
        f.write("node_modules/\n__pycache__/\n.env\n*.pyc\n*.sqlite3\n") #TODO: there should be a configuration file for default gitignore 
    run_cmd("git add .", cwd=project_dir)
    run_cmd("git commit -m 'init'", cwd=project_dir)


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 setup.py <project_name> <django_app_name>")
        sys.exit(1)

    project_name = sys.argv[1]
    django_app_name = sys.argv[2]

    os.makedirs(project_name, exist_ok=True)
    os.chdir(project_name)

    # React
    create_next_app(project_name)

    # Django
    create_django_app("backend", django_app_name)

    # Docker
    create_docker_files(project_name, os.getcwd())

    # Env files
    create_env_files(project_name, os.getcwd())

    # Terraform
    init_terraform(os.getcwd())

    # README
    create_readme(project_name, os.getcwd())

    # Git
    init_git(os.getcwd())

    print("project setup complete")


if __name__ == "__main__":
    main()


#TODO: global variable for db name
#TODO: make idempotent



