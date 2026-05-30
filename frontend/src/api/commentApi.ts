import apiClient from "./client";

export interface Comment {
  id: number;
  photo_id: number;
  user_id: number;
  content: string;
  created_at: string;
}

export async function getComments(photoId: number): Promise<Comment[]> {
  const response = await apiClient.get<Comment[]>(`/photos/${photoId}/comments`);
  return response.data;
}

export async function createComment(
  photoId: number,
  content: string,
): Promise<Comment> {
  const response = await apiClient.post<Comment>(`/photos/${photoId}/comments`, {
    content,
  });
  return response.data;
}
