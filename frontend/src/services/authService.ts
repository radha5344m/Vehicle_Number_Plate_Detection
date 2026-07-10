import { postApiData, getApiData } from "@/services/api/httpClient";
import type {
  LoginRequest,
  LoginResponse,
  LogoutResponse,
  MeResponse,
} from "@/types/api/auth";

export const authService = {
  login(payload: LoginRequest): Promise<LoginResponse> {
    return postApiData<LoginResponse>("/v1/auth/login", payload);
  },

  logout(refreshToken: string): Promise<LogoutResponse> {
    return postApiData<LogoutResponse>("/v1/auth/logout", {
      refresh_token: refreshToken,
    });
  },

  me(): Promise<MeResponse> {
    return getApiData<MeResponse>("/v1/auth/me");
  },
};
