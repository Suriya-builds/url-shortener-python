# URL Shortener with Click Analytics

A URL Shortener built using Python and FastAPI that converts long URLs into short links and tracks click activity.

This project also demonstrates how to use Docker, Docker Compose, automated testing, and CircleCI to build and publish a Docker image.

## 📌 Project Overview

Long URLs can be difficult to share and remember. This application allows users to create short links that redirect to their original URLs.

For example:

**Original URL**

`https://www.google.com/`

**Short URL**

`http://localhost:8080/6`

When someone opens the short URL, the application redirects them to the original website and records the click.

## 🎯 Project Objectives

- Create short links from long URLs.
- Redirect users to the original URLs.
- Record clicks and provide link statistics.
- Store link information in PostgreSQL.
- Use Redis to cache link mappings for faster redirects.
- Containerize the application using Docker.
- Run the application and its dependencies using Docker Compose.
- Automate code checks, testing, and image publishing using CircleCI.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | Builds the web API |
| Uvicorn | Runs the FastAPI application |
| PostgreSQL | Stores links and click records |
| Redis | Caches link mappings |
| Docker | Packages the application into an image |
| Docker Compose | Runs and connects multiple services |
| Pytest | Runs automated tests |
| Ruff | Checks Python code quality |
| Gitleaks | Scans for exposed secrets |
| CircleCI | Automates testing and image building |
| Git and GitHub | Version control and source-code hosting |
| Docker Hub | Stores and distributes the Docker image |

## 🏗️ How the Application Works

The application has the following flow:

1. A user sends a long URL to the FastAPI application.
2. The application validates and normalizes the URL.
3. A short code is generated, or a custom code is validated.
4. The link is stored in PostgreSQL.
5. When someone opens the short link, the application checks Redis for a cached mapping.
6. If the mapping is not cached, the application retrieves it from PostgreSQL and caches it.
7. The application records the click and redirects the user to the original URL.
8. Users can retrieve link lists and click statistics through the API.

### Main Components

- **FastAPI:** Handles requests, URL validation, link creation, redirects, and statistics.
- **PostgreSQL:** Permanently stores link information and click records.
- **Redis:** Caches link mappings to reduce repeated database lookups.
- **Uvicorn:** Serves the FastAPI application.
- **Docker Compose:** Starts the application, database, Redis, and database migration service.

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks PostgreSQL and Redis connectivity |
| POST | `/shorten` | Creates a short link |
| GET | `/{code}` | Redirects to the original URL and records a click |
| GET | `/api/links` | Lists stored links and click counts |
| GET | `/api/links/{code}/stats` | Returns click statistics for a short code |

### Example: Create a Short Link

Request:

```http
POST /shorten
Content-Type: application/json
```

Request body:

```json
{
  "url": "https://www.google.com"
}
```

Example response:

```json
{
  "code": "6",
  "url": "https://www.google.com/",
  "short": "/6"
}
```

The returned short code is used in the redirect endpoint.

## 🐳 Docker Implementation

A Dockerfile was created to package the application.

The Dockerfile:

- Uses a pinned Python 3.12 slim base image.
- Installs dependencies from `requirements.txt`.
- Copies the application and migration files into the image.
- Runs the application as a non-root user.
- Starts the FastAPI application using Uvicorn on port 8080.

### Build the Image

```bash
docker build -t url-shortener-python:1.0 .
```

### Run Using Docker Compose

Docker Compose defines the following services:

- `app`: FastAPI application.
- `postgres`: PostgreSQL database.
- `redis`: Redis cache.
- `migrate`: Applies the SQL migration files.

Start the services:

```bash
docker compose up --build
```

Check their status:

```bash
docker compose ps
```

The application is available at:

`http://localhost:8080`

Check application health:

`http://localhost:8080/health`

The application requires PostgreSQL and Redis to be available. Docker Compose configures their connections and waits for the database migrations to complete before starting the application.

## 🧪 Testing

Automated tests were created using Pytest.

### Unit Tests

Unit tests cover the utility functions in `app/codes.py`, including:

- Short-code encoding and decoding.
- Custom-code validation.
- URL normalization.
- Invalid URL handling.
- Unsafe host rejection.

Run the unit tests:

```bash
python -m pytest tests/test_codes.py -v
```

### Integration Tests

Integration tests verify that the application works with PostgreSQL and Redis, including:

- Health checks.
- Short-link creation and redirection.
- Click recording and statistics.
- Custom-code creation and duplicate-code rejection.
- Handling unknown short codes.

The integration tests require working PostgreSQL and Redis connections and the database migrations to be applied.

Run the integration tests:

```bash
python -m pytest tests/test_integration.py -v
```

### Test Results

- 36 unit tests passed.
- 4 integration tests passed.
- 100% statement coverage for `app/codes.py`.
- Ruff lint checks passed.

The coverage result applies to `app/codes.py`, not the entire application.

## ⚙️ CI/CD with CircleCI

CircleCI is configured through `.circleci/config.yml`.

Whenever code is pushed to the GitHub repository, the pipeline runs five jobs:

1. **Lint:** Checks Python code using Ruff.
2. **Unit Tests:** Runs unit tests and checks the minimum coverage requirement.
3. **Integration Tests:** Runs integration tests using PostgreSQL and Redis service containers.
4. **Secret Scan:** Uses Gitleaks to check for exposed secrets.
5. **Build Image:** Builds the Docker image and pushes it to Docker Hub.

The Docker image build job runs only after the four validation jobs succeed.

Docker Hub credentials are stored as CircleCI environment variables:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

This avoids hardcoding the publishing credentials in the repository.

## 📦 Docker Hub Image

The Docker image is published on Docker Hub.

**Repository:** [suriyaofficial1/url-shortener-python](https://hub.docker.com/r/suriyaofficial1/url-shortener-python)

**Tag:** `1.0`

Pull the image:

```bash
docker pull suriyaofficial1/url-shortener-python:1.0
```

The image can be downloaded to another machine. To run the application successfully, its PostgreSQL and Redis dependencies must also be configured and available.

## 📁 Project Structure

```text
url-shortener-python/
├── app/
│   ├── main.py
│   ├── codes.py
│   ├── db.py
│   └── cache.py
├── migrations/
│   ├── 001_schema.sql
│   └── 002_seed.sql
├── tests/
│   ├── test_codes.py
│   └── test_integration.py
├── .circleci/
│   └── config.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 📚 What I Learned

Through this project, I learned how to:

- Build an API using Python and FastAPI.
- Work with PostgreSQL and Redis.
- Write unit and integration tests using Pytest.
- Measure code coverage.
- Package an application using Docker.
- Manage multiple services using Docker Compose.
- Use Git and GitHub for version control.
- Automate linting, testing, secret scanning, and image building using CircleCI.
- Publish and pull Docker images using Docker Hub.

## ✅ Project Status

The application was tested locally, the automated test and lint jobs passed, and the CircleCI pipeline completed successfully.

The Docker image was published to Docker Hub and successfully pulled using the `1.0` tag.





(# URL Shortener with Click Analytics

**Language:** Python (FastAPI) &nbsp;|&nbsp; **Needs:** Postgres + Redis

This is a **starter**. The application already works. Your job is everything
that gets it building, tested and running in CI.

---

## You do not need Python installed

You will build this into a container, and the container brings its own
Python 3.12. You are not being asked to extend the app — you are being asked
to ship it.

---

## 1. What this app needs

| | |
|---|---|
| **Runtime** | Python 3.12 |
| **Install dependencies** | `pip install -r requirements.txt` |
| **Start the app** | `uvicorn app.main:app --host 0.0.0.0 --port 8080` |
| **Listens on** | port 8080, bound to `0.0.0.0` |
| **Environment variables** | `DATABASE_URL`, `REDIS_URL` |
| **Needs running first** | Postgres, Redis, and the migrations applied |

### What it does

Paste a long URL, get a short code back. Visiting the code redirects and records the click. The stats endpoint shows clicks per day and the top referrers.

### Endpoints

```
GET  /health                 is it alive, and are Postgres and Redis reachable
POST /shorten                {"url": "https://example.com/very/long", "custom": "optional"}
GET  /{code}                 302 redirect, and records the click
GET  /api/links              every link with its click count
GET  /api/links/{code}/stats clicks per day and top referrers
```

`/health` reports Postgres and Redis **separately**. If it says
`postgres: false` the app started fine and your compose wiring is wrong —
do not go looking in the application code.

### Migrations

`migrations/` holds `.sql` files applied **in filename order** before the app
starts. They create the tables and insert sample data. A container running
`psql` over them in order is enough; you do not need a migration tool.

---

## 2. What you must write

| File | What it has to do |
|---|---|
| `Dockerfile` | Install dependencies **before** copying source, pin the base image, do not run as root. |
| `docker-compose.yml` | App + Postgres + Redis + a migration step, one `docker compose up`. |
| `.circleci/config.yml` | lint → unit tests → integration tests → secret scan → image build |
| Unit tests | For `app/codes.py`. No database, no network. |
| Integration tests | Against a real Postgres and Redis as CircleCI service containers. |

Then push your image to **your own Docker Hub account**, tagged `:1.0`.

### When it works

```bash
docker compose up --build
curl localhost:8080/health
```

```json
{"status":"ok","postgres":true,"redis":true}
```

---

## Where the marks are

`app/codes.py` is **pure logic** — plain functions over plain data, no
database and no HTTP. Start your tests there. Use pytest:
`pytest --cov=app --cov-report=term-missing`. Minimum 70%.

There are 60+ cases worth testing in `codes.py` alone: length, alphabet, reserved words, normalisation of equivalent URLs.

## Why Redis is here

Hot links are cached so a redirect never touches Postgres, and click counts are incremented in Redis then flushed to Postgres in batches. A redirect is the most frequent operation in the whole app.

## The hard part

Two people shortening the same URL at the same moment must not get the same code. Decide whether identical URLs share a code or get separate ones, and make the collision impossible either way.

Write your answer in your README. It is worth more marks than the feature.

---

## Getting unstuck

| Symptom | Almost always |
|---|---|
| `/health` says `postgres: false` | Wrong hostname. In compose the host is the **service name**, not `localhost`. |
| Page will not load, logs fine | No `ports:` mapping, or bound to `127.0.0.1` not `0.0.0.0`. |
| `relation "..." does not exist` | Migrations did not run, or the app started before they finished. |
| Build takes minutes each time | `COPY . .` is above your dependency install. |
| CI cannot reach the database | In CircleCI service containers the host **is** `localhost` — opposite of compose. |)