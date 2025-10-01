creates minimal application framework with Next, Django, Docker, Terraform, Git

# Create project
template <project_name> <django_app_name>

# Start containers
docker-compose up --build

# Run Django migrations
docker-compose exec backend python3 manage.py migrate
