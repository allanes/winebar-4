# WineBar Backend

This is the backend repository for the WineBar application. It provides the API and database functionality for the application.

## Prerequisites

Before running the backend, make sure you have the following installed:

- Git
- Docker Compose

## Getting Started

1. Clone the repository:

    ```
    git clone https://github.com/allanes/winebar-4.git
    cd winebar-backend
    git submodule init
    git submodule update
    ```

2. Create a copy of the `.env.example` file and rename it to `.env`:

    ```
    cp .env.example .env
    ```

3. Update the `.env` file with your specific configuration values, such as database credentials and API keys.

    NOTE: use `openssl rand -hex 32` for generating new keys.

4. Build and run the Docker containers:

- For production:
  ```
  docker-compose up --build
  ```

- For local development:
  ```
  docker-compose -f docker-compose-local.yml up --build
  ```

5. Run migrations manually (See below)

## Using the app  

- Navigate to http://localhost and login using '1234' as default user. That will open the admin view.

- Navigate to http://localhost/cajerosView to open the cashier panel.

- Navigate to http://localhost/taperosView to open the tapero panel.

- The backend interactive documentation will be at http://localhost/backend/docs.

- The backend API will be accessible at http://localhost/backend/api/v1/.


