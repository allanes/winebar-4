# WineBar Backend

This is the backend repository for the WineBar application. It provides the API and database functionality for the application.

## Prerequisites

Before running the backend, make sure you have the following installed:

- Git
- Docker Compose

## Getting Started

1. Clone the repository:

    ```
    git clone --recurse-submodules https://github.com/allanes/winebar-4.git
    ```

2. Navigate to the backend directory:

    ```
    cd winebar-backend
    ```

3. Create a copy of the `.env.example` file and rename it to `.env`:

    ```
    cp .env.example .env
    ```

4. Update the `.env` file with your specific configuration values, such as database credentials and API keys.

5. Build and run the Docker containers:

- For production:
  ```
  docker-compose up --build
  ```

- For local development:
  ```
  docker-compose -f docker-compose-local.yml up --build
  ```

6.  
    a.  The backend API will be accessible at http://localhost/backend/api/v1/.

    b. The backend interactive documentation will be at http://localhost/backend/docs.

## Frontend Submodule

The frontend repository is included as a submodule in this backend repository. It is a public repository that contains the user interface for the WineBar application.

To update the frontend submodule to the latest version, run:

    git submodule update --remote winebar-4-frontend

## Password Retrieval Server

The frontend client relies on an additional local server to retrieve passwords. This server is a separate public repository located at https://github.com/allanes/winebar-4-servidor-claves.

To automatically install and mount the password retrieval server within the compose file, follow these steps:

1. Add the following service definition to your `docker-compose.yml` and `docker-compose-local.yml` files:

   ```yaml
   services:
     # ...
     password-server:
       container_name: winebar-4-servidor-claves
       image: allanes/winebar-4-servidor-claves:latest
       ports:
         - "8000:8000"
       networks:
         - winebar4-net

2. Update the frontend service in your compose files to include the password server URL as an environment variable:

    ```
    services:
    # ...
    frontend:
        # ...
        environment:
        - PASSWORD_SERVER_URL=http://password-server:8000
    ```

3. Rebuild and restart the containers:

    docker-compose up --build

    or

    docker-compose -f docker-compose-local.yml up --build

With these changes, the password retrieval server will be automatically installed and mounted within your compose file, allowing the main server to use the application.

## Database Migrations

The backend uses Alembic for database migrations. The prestart.sh script is executed before starting the FastAPI application to run the Alembic upgrades and initialize the database.

To manually run the database migrations, use the following command:

    docker-compose exec backend alembic upgrade head
