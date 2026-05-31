# Tagged Pictures Map

This repository contains a working FastAPI backend MVP for a map-based photo
application. Users can register, log in, upload a geotagged image, query visible
map photos, and add comments.

## Production Plan

### Technology choices

| Area | Choice | Reason |
| --- | --- | --- |
| Frontend | React, TypeScript, Vite, Tailwind CSS | Fast UI iteration with typed API calls |
| Backend | FastAPI, SQLModel, Alembic | Typed REST API and migrations |
| Database | PostgreSQL with PostGIS | Spatial indexes and bounding-box queries |
| Image storage | S3 in cloud, MinIO locally | Durable object storage with presigned uploads |
| Authentication | Short-lived JWT access tokens, refresh token cookie | Stateless API authorization with revocation support |
| Map | MapLibre GL with marker clustering | Good performance and no mandatory vendor lock-in |
| AI | OpenAI vision model through an async worker | Generate captions without blocking upload |
| Deployment | Docker Compose locally; managed PostgreSQL, S3, container platform, CDN in cloud | Simple local setup and scalable production services |

### Architecture

```text
React client
  |-- JWT REST calls ----------------------> FastAPI API
  |                                           |-- PostgreSQL + PostGIS
  |-- presigned upload ---------------------> |-- S3 / MinIO
                                              |-- job queue --> AI caption worker

CDN <----------------------------------------- S3 / MinIO
```

The API owns users, photo metadata, comments, permissions, and storage
credentials. Image binaries live in object storage rather than the database.
The MVP stores uploads locally so it can run without cloud credentials.

### Core data models

- `User`: `id`, `email`, `username`, `password_hash`, `created_at`
- `Photo`: `id`, `user_id`, `image_url`, `latitude`, `longitude`,
  `description`, `ai_description`, `created_at`
- `Comment`: `id`, `photo_id`, `user_id`, `content`, `created_at`

For production, add a PostGIS `geography(Point, 4326)` column and a GiST index.
Store refresh-token sessions separately so users can log out individual devices.

### Upload-to-map data flow

1. The user registers or logs in and receives an access token.
2. In production, the client requests a presigned object-storage URL.
3. The client uploads the file directly to S3 or MinIO.
4. The client sends the object key and coordinates to the API.
5. The API validates the metadata, stores the `Photo`, and enqueues AI captioning.
6. The map requests photos inside its current bounding box and zoom level.
7. The API uses a PostGIS spatial index and returns markers or clusters.
8. Clicking a marker loads the image URL and its comments.

The included MVP combines steps 2-4 in `POST /photos/upload` and writes the
uploaded file to `backend/uploads`.

### Image storage trade-offs

Storing image bytes in PostgreSQL makes transactions simple, but increases
database size, backup time, and serving cost. Files on the application server
are convenient for a demo but do not work well across multiple API replicas.
Object storage is the production choice: it is durable, cheap, CDN-friendly,
and supports direct browser uploads.

### Performance for 10k+ photos

- Query only the visible map bounding box, not the whole table.
- Add a PostGIS GiST index and return compact marker DTOs.
- Cluster markers by zoom level with MapLibre or server-side geohash buckets.
- Paginate or cap results and fetch photo details only after marker clicks.
- Serve thumbnails through a CDN; generate multiple image sizes asynchronously.
- Cache popular map tiles or bounding-box responses when traffic grows.

### Deployment

For local production-like development, use Docker Compose with frontend,
FastAPI, PostgreSQL/PostGIS, and MinIO services. In cloud deployment, use a
managed PostgreSQL instance, S3-compatible storage, a CDN, secret management,
container replicas behind a load balancer, and CI checks for tests and
migrations.

### Realistic implementation estimate

| Work item | Estimate |
| --- | --- |
| Repository setup, Docker, CI skeleton | 4-6h |
| Database schema, migrations, storage integration | 6-8h |
| Authentication and authorization | 4-6h |
| Photo upload, EXIF GPS extraction, thumbnail worker | 6-10h |
| Frontend login, upload, image details, comments | 8-12h |
| Map integration, viewport query, clustering | 6-10h |
| AI caption worker and retry handling | 3-5h |
| Tests, observability, security pass | 8-12h |
| Deployment and runbook | 4-6h |

A four-hour exercise can reasonably deliver the included backend MVP and a
minimal frontend, but not the complete production hardening described above.

## Backend MVP

### Run locally

```powershell
cd backend
python -m venv .venv (only the firt time to create the env)
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt (only the firt time to download the requirements)
python -m uvicorn main:app --reload (start the AI below firstly)
```

The API documentation is available at `http://127.0.0.1:8000/docs`.
SQLite and local file uploads are used by default.


### Enable AI photo descriptions

Copy `backend/.env.example` to `backend/.env`, then set `OPENAI_API_KEY`.
Uploaded photos will receive a short AI-generated description when the key is
configured. Uploads still succeed if the AI service is unavailable.

```powershell
Copy-Item .env.example .env
# Edit .env and replace OPENAI_API_KEY with your key.
python -m uvicorn main:app --reload
```

The default vision-capable model is `gpt-5.4-mini`. Override `OPENAI_MODEL` in
`.env` when needed.

### API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/auth/register` | Register a user |
| `POST` | `/auth/login` | Get a JWT |
| `POST` | `/photos/upload` | Upload a local image and coordinates |
| `POST` | `/photos` | Register an existing image URL |
| `GET` | `/photos` | Query markers, optionally by bounding box |
| `POST` | `/photos/{photo_id}/comments` | Add a comment |
| `GET` | `/photos/{photo_id}/comments` | List comments |

### Test the backend

```powershell
cd backend
python -m pytest -q
```

The example in `backend/tests/test_api.py` exercises the complete backend flow:
register, log in, upload an image, query the map viewport, add a comment, and
read comments.


### Test the frontend

1. Go to the frontend directory

```powershell
cd frontend
```

2. Install dependencies

```powershell
npm install
```

3. Start the development server

```powershell
npm run dev
```

4. Open the application

```text
http://localhost:5173
```

5. Test the main features

- Register a new user
- Login with existing credentials
- Upload a geotagged photo
- View photos on the map
```
