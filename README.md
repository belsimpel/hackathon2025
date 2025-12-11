# Hackathon 2025 – Backend & Frontend Setup Guide

Welcome to the Hackathon!  
This repository contains boilerplate applications in **PHP**, **Python**, and multiple **frontend frameworks**.  
Participants can choose any combination and run everything through **Docker**, without installing programming languages locally.

## Table of Contents

1. Repository Structure  
2. Prerequisites  
3. Choosing Your Backend  
   - PHP Backend  
   - Python Backend  
4. Database (MySQL)  
5. Using a Frontend in Docker Compose  
6. Troubleshooting

## Repository Structure

```
hackathon2025/
  boilerplate/
    php/
    python/
    frontend/
      react/
      vue/
  docker-compose_php.yml
  docker-compose_python.yml
  README.md
```

## Prerequisites

- Docker Desktop or Docker Engine  
- Docker Compose v2+  

## Choosing Your Backend

Choose one backend:

- PHP → `docker-compose_php.yml`  
- Python → `docker-compose_python.yml`  

Each backend includes:

- Backend service  
- MySQL database  
- Persistent storage  

Run only the compose file for your chosen backend.

## PHP Backend

### Start

```bash
docker compose -f docker-compose_php.yml up --build
```

Starts:

- PHP backend  
- MySQL database  

Access backend:

```
http://localhost:8000
```

### Live Editing

```
boilerplate/php/index.php
boilerplate/php/Controllers/
boilerplate/php/Models/
boilerplate/php/Services/
boilerplate/php/Repositories/
```

## Python Backend

### Start

```bash
docker compose -f docker-compose_python.yml up --build
```

Starts FastAPI backend at:

```
http://localhost:8001
```

Live edits reload automatically.

## Database (MySQL)

Connection details:

| Setting   | Value       |
|-----------|-------------|
| Host      | db          |
| DB        | hackathon   |
| User      | hackathon   |
| Password  | hackathon   |
| Root Pass | root        |

### PHP Example

```php
$pdo = new PDO(
    'mysql:host=db;dbname=hackathon;charset=utf8mb4',
    'hackathon',
    'hackathon'
);
```

### Python Example

```python
import pymysql
conn = pymysql.connect(
    host="db",
    user="hackathon",
    password="hackathon",
    database="hackathon"
)
```

## Using a Frontend in Docker Compose

Frontends live in:

```
boilerplate/frontend/react/
boilerplate/frontend/vue/
```

### Step 1 — Add a Dockerfile (React example)

`boilerplate/frontend/react/Dockerfile`:

```dockerfile
FROM node:20
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
```

### Step 2 — Add frontend service to compose file

PHP:

```yaml
frontend:
  build:
    context: ./boilerplate/frontend/react
    dockerfile: Dockerfile
  volumes:
    - ./boilerplate/frontend/react:/app
  ports:
    - "5173:5173"
  depends_on:
    - php-backend
```

Python:

```yaml
frontend:
  build:
    context: ./boilerplate/frontend/react
    dockerfile: Dockerfile
  volumes:
    - ./boilerplate/frontend/react:/app
  ports:
    - "5173:5173"
  depends_on:
    - python-backend
```

### Step 3 — Start full stack

```bash
docker compose -f docker-compose_php.yml up --build
```

or

```bash
docker compose -f docker-compose_python.yml up --build
```

Frontend runs at:

```
http://localhost:5173
```

## Troubleshooting

### Port conflicts

Change ports in compose file.

### MySQL not ready

```bash
docker compose logs db
```

### PHP autoload issues

Ensure vendor directory remains inside container.

### Python import errors

Ensure `app.py` exists in:

```
boilerplate/python/
```
