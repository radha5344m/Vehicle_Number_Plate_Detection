/** Authentication API types. */

export interface OfficerSummary {
  officer_id: string;
  employee_id: string;
  badge_number: string;
  username: string;
  email: string;
  phone_number: string | null;
  first_name: string;
  last_name: string;
  rank: string;
  station_id: string;
  station_code: string;
  station_name: string;
  district: string | null;
  roles: string[];
}

export interface StationSummary {
  station_id: string;
  station_code: string;
  station_name: string;
}

export interface TokenBundle {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthSession {
  officer: OfficerSummary;
  role: string;
  permissions: string[];
  station: StationSummary;
}

export interface LoginRequest {
  identifier: string;
  password: string;
  station_code?: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  officer: OfficerSummary;
  user: OfficerSummary;
  role: string;
  permissions: string[];
  station: StationSummary;
  token: TokenBundle;
}

export interface LogoutResponse {
  message: string;
}

export interface MeResponse {
  officer: OfficerSummary;
  user: OfficerSummary;
  role: string;
  permissions: string[];
  station: StationSummary;
  session_id: string;
}

export interface ApiErrorBody {
  code: string;
  message: string;
  details?: Array<{ field?: string; code?: string; message?: string }>;
}

export interface ApiErrorEnvelope {
  success: false;
  error: ApiErrorBody;
}
