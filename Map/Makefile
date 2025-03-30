# Run the Loyalty application
run:
	@echo "Starting Loyalty application..."
	python manage.py runserver

# Apply migrations
migrate:
	@echo "Applying database migrations..."
	python manage.py makemigrations mmm
	python manage.py migrate mmm
	python manage.py migrate

# Make migrations
make:
	@echo "Creating database migrations..."
	python manage.py makemigrations

collect:
	@echo "Collecting static files..."
	python manage.py collectstatic --noinput
