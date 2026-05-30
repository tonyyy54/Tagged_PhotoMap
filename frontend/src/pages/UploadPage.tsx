import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { gps } from "exifr";
import apiClient from "../api/client";

function UploadPage() {
  const navigate = useNavigate();
  const [file, setFile] =useState<File | null>(null);
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [description, setDescription] = useState("");
  const [gpsStatus, setGpsStatus] = useState("");

  async function handleFileChange(selectedFile: File | null) {
    setFile(selectedFile);
    if (!selectedFile) {
      setGpsStatus("");
      return;
    }

    setGpsStatus("Reading GPS metadata...");
    try {
      const coordinates = await gps(selectedFile);
      if (coordinates?.latitude != null && coordinates?.longitude != null) {
        setLatitude(coordinates.latitude.toFixed(6));
        setLongitude(coordinates.longitude.toFixed(6));
        setGpsStatus("GPS coordinates extracted from the image.");
      } else {
        setGpsStatus("No EXIF GPS data found. Enter coordinates manually.");
      }
    } catch {
      setGpsStatus("Could not read GPS metadata. Enter coordinates manually.");
    }
  }

  async function handleUpload() {
    if (!file) {
      alert("Select a file");
      return;
    }
    if (!latitude || !longitude) {
      alert("Enter coordinates or select an image containing EXIF GPS data.");
      return;
    }

    const formData = new FormData();

    formData.append("image", file);
    formData.append("latitude", latitude);
    formData.append("longitude", longitude);

    if (description) {
      formData.append("description", description);
    }

    try {
      await apiClient.post(
        "/photos/upload",
        formData,
        {
          headers: {
            "Content-Type":
              "multipart/form-data",
          },
        }
      );

      alert("Upload success");
      navigate("/map");
    } catch (error) {
      console.error(error);
      const message = axios.isAxiosError(error)
        ? error.response?.data?.detail ?? "Cannot connect to backend"
        : "Upload failed";
      alert(message);
    }
  }

  return (
    <div>
      <h1>Upload Photo</h1>

      <input
        type="file"
        accept="image/*"
        onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
      />

      {gpsStatus && <p>{gpsStatus}</p>}

      <input
        type="number"
        placeholder="Latitude"
        value={latitude}
        onChange={(e) => setLatitude(e.target.value)}
      />

      <input
        type="number"
        placeholder="Longitude"
        value={longitude}
        onChange={(e) => setLongitude(e.target.value)}
      />
      
      <textarea
        placeholder="Description optional"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      
      <button onClick={handleUpload}>
        Upload
      </button>

      <button onClick={() => navigate("/map")}>
        View map
      </button>
    </div>
  );
}

export default UploadPage;
