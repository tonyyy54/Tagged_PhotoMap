import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import L from "leaflet";
import { MapContainer, Marker, Popup, TileLayer, useMapEvents } from "react-leaflet";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import "leaflet/dist/leaflet.css";
import "./MapPage.css";

import { createComment, getComments, type Comment } from "../api/commentApi";
import { deletePhoto, getPhotoImageUrl, getPhotos, type Photo, type PhotoBounds } from "../api/photoApi";
import { clearAccessToken, getCurrentUserId } from "../auth";

delete (L.Icon.Default.prototype as { _getIconUrl?: unknown })._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

function getMapBounds(map: L.Map): PhotoBounds {
  const bounds = map.getBounds();
  return {
    min_lat: bounds.getSouth(),
    max_lat: bounds.getNorth(),
    min_lng: bounds.getWest(),
    max_lng: bounds.getEast(),
  };
}

function ViewportLoader({ onBoundsChange }: { onBoundsChange: (bounds: PhotoBounds) => void }) {
  const map = useMapEvents({
    moveend: () => onBoundsChange(getMapBounds(map)),
  });

  useEffect(() => {
    onBoundsChange(getMapBounds(map));
  }, [map, onBoundsChange]);

  return null;
}

function PhotoPopup({ photo, onDeleted }: { photo: Photo; onDeleted: (photoId: number) => void }) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState("");
  const isOwner = getCurrentUserId() === photo.user_id;

  useEffect(() => {
    let active = true;
    getComments(photo.id)
      .then((data) => active && setComments(data))
      .catch(() => active && setError("Could not load comments."))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [photo.id]);

  async function submitComment(event: React.FormEvent) {
    event.preventDefault();
    const content = comment.trim();
    if (!content) return;

    setSending(true);
    setError("");
    try {
      const created = await createComment(photo.id, content);
      setComments((current) => [...current, created]);
      setComment("");
    } catch {
      setError("Log in again before adding a comment.");
    } finally {
      setSending(false);
    }
  }

  async function handleDelete() {
    if (!window.confirm("Delete this photo and its comments?")) return;

    setDeleting(true);
    setError("");
    try {
      await deletePhoto(photo.id);
      onDeleted(photo.id);
    } catch {
      setError("Could not delete this photo.");
      setDeleting(false);
    }
  }

  return (
    <article className="photo-popup">
      <img src={getPhotoImageUrl(photo)} alt={photo.description || "Uploaded location"} />
      <div className="photo-popup__body">
        <h2>{photo.description || "Tagged photo"}</h2>
        {photo.ai_description && (
          <p className="photo-popup__ai">
            <strong>AI description:</strong> {photo.ai_description}
          </p>
        )}
        <p className="photo-popup__coordinates">
          {photo.latitude.toFixed(4)}, {photo.longitude.toFixed(4)}
        </p>
        {isOwner && (
          <button className="delete-photo" disabled={deleting} onClick={handleDelete} type="button">
            {deleting ? "Deleting..." : "Delete photo"}
          </button>
        )}

        <section className="comments">
          <h3>Comments</h3>
          {loading && <p className="muted">Loading...</p>}
          {!loading && comments.length === 0 && <p className="muted">No comments yet.</p>}
          {comments.map((item) => (
            <p className="comment" key={item.id}>{item.content}</p>
          ))}
          {error && <p className="error">{error}</p>}
          <form onSubmit={submitComment}>
            <input
              aria-label="New comment"
              placeholder="Add a comment"
              value={comment}
              onChange={(event) => setComment(event.target.value)}
            />
            <button disabled={sending} type="submit">
              {sending ? "Sending..." : "Add"}
            </button>
          </form>
        </section>
      </div>
    </article>
  );
}

function MapPage() {
  const navigate = useNavigate();
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadPhotos = useCallback(async (bounds: PhotoBounds) => {
    setLoading(true);
    setError("");
    try {
      setPhotos(await getPhotos(bounds));
    } catch {
      setError("Could not load photos. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, []);

  const removePhoto = useCallback((photoId: number) => {
    setPhotos((current) => current.filter((photo) => photo.id !== photoId));
  }, []);

  function logout() {
    clearAccessToken();
    navigate("/login");
  }

  return (
    <main className="map-page">
      <header className="map-toolbar">
        <div>
          <strong>Tagged Photos</strong>
          <span>{loading ? "Loading..." : `${photos.length} visible photo${photos.length === 1 ? "" : "s"}`}</span>
        </div>
        <nav>
          <button onClick={() => navigate("/upload")} type="button">Upload</button>
          <button className="secondary" onClick={logout} type="button">Log out</button>
        </nav>
      </header>

      {error && <div className="map-error">{error}</div>}

      <MapContainer center={[46.7, 2.5]} zoom={6} className="photo-map">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ViewportLoader onBoundsChange={loadPhotos} />
        {photos.map((photo) => (
          <Marker key={photo.id} position={[photo.latitude, photo.longitude]}>
            <Popup maxWidth={320} minWidth={280}>
              <PhotoPopup photo={photo} onDeleted={removePhoto} />
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </main>
  );
}

export default MapPage;
