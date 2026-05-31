import apiClient, { API_BASE_URL } from "./client";

export interface Photo {
  id: number;
  user_id: number;
  image_url: string;
  latitude: number;
  longitude: number;
  description?: string;
  ai_description?: string;
  created_at: string;
}

export interface PhotoBounds {
  min_lat: number;
  max_lat: number;
  min_lng: number;
  max_lng: number;
}

export async function getPhotos(bounds?: PhotoBounds): Promise<Photo[]> {
  const response = await apiClient.get("/photos", {
    params: bounds,
  });
  return response.data;
}

export async function deletePhoto(photoId: number): Promise<void> {
  await apiClient.delete(`/photos/${photoId}`);
}

export function getPhotoImageUrl(photo: Photo): string {
  return photo.image_url.startsWith("http")
    ? photo.image_url
    : `${API_BASE_URL}${photo.image_url}`;
}
