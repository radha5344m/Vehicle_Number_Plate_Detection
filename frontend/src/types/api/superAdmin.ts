export interface SuperAdminNotification {
  id: string;
  title: string;
  description: string;
  occurred_at: string;
  category: string;
  is_read: boolean;
}

export interface SuperAdminProfileData {
  officer_id: string;
  employee_id: string;
  username: string;
  email: string;
  phone_number: string | null;
  full_name: string;
  rank: string;
  role: string;
  police_station: string;
  district: string | null;
  status: string;
  created_at: string;
  last_login_at: string | null;
  session_id: string;
}

export interface SuperAdminSignInActivity {
  id: string;
  label: string;
  occurred_at: string;
  detail: string;
}
