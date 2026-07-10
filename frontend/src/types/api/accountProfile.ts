export interface AccountProfileData {
  officer_id: string;
  employee_id: string;
  full_name: string;
  email: string;
  phone_number: string | null;
  role: string;
  created_at: string | null;
  last_login_at: string | null;
}

export interface UpdateAccountProfileInput {
  fullName: string;
  email: string;
  phoneNumber: string;
  employeeId: string;
}
