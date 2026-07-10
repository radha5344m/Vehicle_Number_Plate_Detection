import { policeOfficerService } from "@/services/policeOfficerService";
import { splitFullName } from "@/lib/superAdminProfile";
import { updateStoredOfficer } from "@/stores/authStore";
import type { AccountProfileData, UpdateAccountProfileInput } from "@/types/api/accountProfile";

function toAccountProfile(profile: Awaited<ReturnType<typeof policeOfficerService.getProfile>>): AccountProfileData {
  return {
    officer_id: profile.officer_id,
    employee_id: profile.employee_id,
    full_name: profile.officer_name,
    email: profile.email,
    phone_number: profile.phone_number,
    role: profile.role,
    created_at: profile.created_at,
    last_login_at: profile.last_login_at,
  };
}

export const policeOfficerAccountService = {
  async getProfile(): Promise<AccountProfileData> {
    const profile = await policeOfficerService.getProfile();
    return toAccountProfile(profile);
  },

  async updateProfile(input: UpdateAccountProfileInput): Promise<AccountProfileData> {
    const { firstName, lastName } = splitFullName(input.fullName);
    const profile = await policeOfficerService.updateProfile({
      first_name: firstName,
      last_name: lastName,
      email: input.email.trim(),
      phone_number: input.phoneNumber.trim() || undefined,
      employee_id: input.employeeId.trim(),
    });
    updateStoredOfficer({
      first_name: firstName,
      last_name: lastName,
      email: profile.email,
      phone_number: profile.phone_number,
      employee_id: profile.employee_id,
    });
    return toAccountProfile(profile);
  },
};
