# Tagged Pictures Map

Tagged Pictures Map is a full-stack MVP for uploading geotagged photos and
displaying them on an interactive map. Users can register, log in, upload an
image, extract EXIF GPS coordinates, browse photos in the visible map area,
generate AI descriptions, add comments, and delete their own photos.

## Current Technology Stack

The following technologies are implemented in the repository today.

| Area | Technology | Purpose |
| --- | --- | --- |
| Frontend | React 19, TypeScript | Typed UI components |
| Build tooling | Vite 8 | Development server and production build |
| Routing | React Router DOM | Login, registration, upload, and map routes |
| HTTP client | Axios | REST API requests and JWT injection |
| Map | Leaflet, React Leaflet, OpenStreetMap tiles | Interactive map, markers, and popups |
| Browser image metadata | exifr | Extract GPS coordinates from EXIF metadata |
| Styling | CSS | Page and map popup styles |
| Backend | FastAPI, Uvicorn | REST API and local static file serving |
| ORM | SQLModel | Database models and queries |
| Database | SQLite | Local MVP persistence |
| Image processing | Pillow | Server-side EXIF GPS extraction |
| Image storage | Local `backend/uploads` directory | Local MVP image storage |
| Authentication | JWT bearer tokens, PBKDF2-HMAC-SHA256 | API authorization and password hashing |
| AI descriptions | OpenAI Responses API with `gpt-5.4-mini` | Generate a short caption after upload |
| Backend tests | pytest, HTTPX | API and service tests |
| Frontend checks | ESLint, TypeScript | Static analysis and type checking |

## MVP Architecture

```text
React client
  |-- JWT REST calls ----------------------> FastAPI API
  |                                           |-- SQLite
  |-- multipart photo upload -------------->  |-- backend/uploads
                                              |-- OpenAI Responses API

OpenStreetMap tiles ------------------------> Leaflet map
```

The API stores users, photo metadata, comments, permissions, and AI
descriptions. Uploaded image files are stored locally for development.

## Implemented Features

- Register and log in with JWT authentication.
- Upload JPEG, PNG, or WebP images.
- Extract GPS coordinates in the browser with `exifr`.
- Fall back to server-side EXIF extraction with Pillow.
- Enter coordinates manually when an image has no GPS metadata.
- Generate a concise AI photo description when an OpenAI API key is configured.
- Show an explicit AI quota message when the OpenAI API quota is insufficient.
- Query only photos inside the current map viewport.
- Display photo markers, image popups, AI descriptions, and comments.
- Allow authenticated users to delete their own photos and associated comments.

## Core Data Models

- `User`: `id`, `email`, `username`, `password_hash`, `created_at`
- `Photo`: `id`, `user_id`, `image_url`, `latitude`, `longitude`,
  `description`, `ai_description`, `created_at`
- `Comment`: `id`, `photo_id`, `user_id`, `content`, `created_at`

## Run Locally

### Backend

```powershell
cd backend

# First-time setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# Start the API
python -m uvicorn main:app --reload
```

The API documentation is available at `http://127.0.0.1:8000/docs`.

### AI Photo Descriptions

Create a local environment file and add an OpenAI API key:

```powershell
cd backend
Copy-Item .env.example .env
```

Edit `backend/.env`:

```env
SECRET_KEY=replace-with-a-long-random-value
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-5.4-mini
```

`backend/.env` is ignored by Git. Do not commit real API keys. If the AI
service is unavailable, the photo upload still succeeds.

### Frontend

```powershell
cd frontend

# First-time setup
npm install

# Start the development server
npm run dev
```

Open `http://localhost:5173`.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/auth/register` | Register a user |
| `POST` | `/auth/login` | Get a JWT access token |
| `POST` | `/photos/upload` | Upload an image and coordinates |
| `POST` | `/photos` | Register an existing image URL |
| `GET` | `/photos` | Query markers, optionally by bounding box |
| `DELETE` | `/photos/{photo_id}` | Delete the current user's photo and comments |
| `POST` | `/photos/{photo_id}/comments` | Add a comment |
| `GET` | `/photos/{photo_id}/comments` | List comments |

## Verification

Run the backend tests:

```powershell
cd backend
python -m pytest -q
```

Check the frontend:

```powershell
cd frontend
npm run lint
npm run build
```

On Windows systems that block PowerShell scripts, use `npm.cmd`:

```powershell
npm.cmd run lint
npm.cmd run build
```

## Production Plan

The following technologies are recommended for production but are not yet
implemented in this repository.

| Area | Recommended technology | Reason |
| --- | --- | --- |
| Database | PostgreSQL with PostGIS | Spatial indexes and efficient bounding-box queries |
| Database migrations | Alembic | Versioned schema changes |
| Image storage | S3-compatible storage or MinIO | Durable object storage and direct uploads |
| Image delivery | CDN and generated thumbnails | Faster image loading and lower API traffic |
| Map scaling | Marker clustering or server-side geohash buckets | Avoid rendering thousands of individual markers |
| AI processing | Background job queue and worker | Keep uploads responsive while captions are generated |
| Authentication | Short-lived access tokens and refresh-token sessions | Better session revocation |
| Deployment | Docker Compose locally and managed cloud services | Repeatable local setup and scalable production hosting |

### Image Storage Trade-offs

Storing image bytes in PostgreSQL makes transactions straightforward, but
increases database size, backup time, and serving cost. Storing files on the
application server is convenient for this MVP, but does not work well across
multiple API replicas. Production deployments should keep metadata in the
database and store image files in S3-compatible object storage behind a CDN.

### Performance for 10k+ Photos

- Query only the visible map bounding box instead of loading every photo.
- Add a PostGIS `geography(Point, 4326)` column and a GiST spatial index.
- Return lightweight marker DTOs and fetch full details after marker clicks.
- Cluster markers by zoom level with Leaflet clustering or server-side buckets.
- Cap results and paginate when a viewport contains too many photos.
- Generate small WebP thumbnails asynchronously and serve them through a CDN.
- Debounce viewport requests and cancel stale requests when the map moves.
- Cache popular bounding-box responses when traffic grows.
