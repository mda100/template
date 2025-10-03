creates minimal boilerplate for application with Next, Django, Docker, Terraform, Git

# Create project
template <project_name> <django_app_name>

# Start containers
docker-compose up --build

# Run Django migrations
docker-compose exec backend python3 manage.py migrate


# Build/Rebuild .whl
pip3 install build

rm -rf dist build *.egg-info

python3 -m build

pip3 install --force-reinstall dist/template-0.1.0-py3-none-any.whl

