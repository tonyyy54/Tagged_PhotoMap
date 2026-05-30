import apiClient from "./client";

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export async function register(data: RegisterRequest) {
  const response = await apiClient.post(
    "/auth/register",
    data
  );

  return response.data;
}

export async function login(
  data: LoginRequest
): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>(
    "/auth/login",
    data
  );

  return response.data;
}