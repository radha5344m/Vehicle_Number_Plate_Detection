import { deleteApiData, getApiData, patchApiData, postApiData } from "@/services/api/httpClient";
import { sanitizeUserFilters } from "@/lib/userFilters";
import type {
  ActionMessage,
  CreateUserRequest,
  ResetPasswordRequest,
  ResetStationAdminPasswordRequest,
  UpdateUserRequest,
  UserFilters,
  UserMutationResult,
  UsersList,
} from "@/types/api/users";

function toQueryString(filters: UserFilters): string {
  const params = new URLSearchParams();
  if (filters.search) params.set("search", filters.search);
  if (filters.role) params.set("role", filters.role);
  if (filters.station) params.set("station", filters.station);
  if (filters.status) params.set("status", filters.status);
  if (filters.created_from) params.set("created_from", filters.created_from);
  if (filters.created_to) params.set("created_to", filters.created_to);
  if (filters.page) params.set("page", String(filters.page));
  if (filters.page_size) params.set("page_size", String(filters.page_size));
  if (filters.sort_by) params.set("sort_by", filters.sort_by);
  if (filters.sort_desc != null) params.set("sort_desc", String(filters.sort_desc));
  const query = params.toString();
  return query ? `?${query}` : "";
}

export const usersService = {
  list(filters: UserFilters = {}): Promise<UsersList> {
    const sanitized = sanitizeUserFilters(filters);
    return getApiData<UsersList>(`/v1/users${toQueryString(sanitized)}`);
  },

  create(body: CreateUserRequest): Promise<UserMutationResult> {
    return postApiData<UserMutationResult>("/v1/users", body);
  },

  update(officerId: string, body: UpdateUserRequest): Promise<UserMutationResult> {
    return patchApiData<UserMutationResult>(`/v1/users/${officerId}`, body);
  },

  activate(officerId: string): Promise<UserMutationResult> {
    return postApiData<UserMutationResult>(`/v1/users/${officerId}/activate`, {});
  },

  deactivate(officerId: string): Promise<UserMutationResult> {
    return postApiData<UserMutationResult>(`/v1/users/${officerId}/deactivate`, {});
  },

  resetPassword(officerId: string, body: ResetPasswordRequest = {}): Promise<UserMutationResult> {
    return postApiData<UserMutationResult>(`/v1/users/${officerId}/reset-password`, body);
  },

  resetStationAdminPassword(
    officerId: string,
    body: ResetStationAdminPasswordRequest,
  ): Promise<UserMutationResult> {
    return postApiData<UserMutationResult>(`/v1/users/station-admins/${officerId}/reset-password`, body);
  },

  delete(officerId: string): Promise<ActionMessage> {
    return deleteApiData<ActionMessage>(`/v1/users/${officerId}`);
  },
};
