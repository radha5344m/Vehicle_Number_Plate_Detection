export type UserRole = "SUPER_ADMIN" | "STATION_ADMIN" | "POLICE_OFFICER";
export type UserStatus = "active" | "inactive" | "suspended";

export interface UserItem {
  officer_id: string;
  user_id: string;
  employee_id: string;
  full_name: string;
  username: string;
  email: string;
  phone_number: string | null;
  badge_number: string;
  rank: string;
  role: UserRole;
  police_station: string;
  district: string | null;
  status: UserStatus;
  created_at: string;
  last_login_at: string | null;
}

export interface UsersPagination {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface UsersList {
  items: UserItem[];
  pagination: UsersPagination;
  summary: UsersSummary;
}

export interface UsersSummary {
  total_users: number;
  super_admins: number;
  station_admins: number;
  police_officers: number;
}

export interface UserFilters {
  search?: string;
  role?: UserRole;
  station?: string;
  status?: UserStatus;
  created_from?: string;
  created_to?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_desc?: boolean;
}

export interface CreateUserRequest {
  first_name: string;
  last_name: string;
  username?: string;
  email: string;
  phone_number?: string;
  badge_number?: string;
  rank?: string;
  role: UserRole;
  police_station?: string;
  district?: string;
  status: UserStatus;
}

export interface UpdateUserRequest {
  employee_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone_number?: string;
  rank: string;
  role?: UserRole;
  police_station?: string;
  district?: string;
  status: UserStatus;
}

export interface ResetPasswordRequest {
  new_password?: string;
}

export interface UserMutationResult {
  user: UserItem;
  temporary_password?: string | null;
  password_change_required?: boolean;
}

export interface ActionMessage {
  message: string;
}
