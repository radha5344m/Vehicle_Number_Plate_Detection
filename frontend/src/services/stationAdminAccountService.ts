import { stationAdminService } from "@/services/stationAdminService";
import { splitFullName } from "@/lib/superAdminProfile";
import { updateStoredOfficer } from "@/stores/authStore";
import type { AccountProfileData, UpdateAccountProfileInput } from "@/types/api/accountProfile";

function toAccountProfile(profile: Awaited<ReturnType<typeof stationAdminService.getProfile>>): AccountProfileData {
  return {
    officer_id: profile.officer_id,
    employee_id: profile.employee_id,
    full_name: profile.admin_name,
    email: profile.account_email,
    phone_number: profile.account_phone,
    role: profile.role,
    created_at: profile.created_at,
    last_login_at: profile.last_login_at,
  };
}

export const stationAdminAccountService = {
  async getProfile(): Promise<AccountProfileData> {
    const profile = await stationAdminService.getProfile();
    return toAccountProfile(profile);
  },

  async updateProfile(input: UpdateAccountProfileInput): Promise<AccountProfileData> {
    const { firstName, lastName } = splitFullName(input.fullName);
    const profile = await stationAdminService.updateAccountProfile({
      first_name: firstName,
      last_name: lastName,
      email: input.email.trim(),
      phone_number: input.phoneNumber.trim() || undefined,
      employee_id: input.employeeId.trim(),
    });
    updateStoredOfficer({
      first_name: firstName,
      last_name: lastName,
      email: profile.account_email,
      phone_number: profile.account_phone,
      employee_id: profile.employee_id,
    });
    return toAccountProfile(profile);
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await stationAdminService.changePassword(currentPassword, newPassword);
  },
};
