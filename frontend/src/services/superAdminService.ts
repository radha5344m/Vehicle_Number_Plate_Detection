import { authService } from "@/services/authService";
import { executiveDashboardService } from "@/services/executiveDashboardService";
import { usersService } from "@/services/usersService";
import { getStoredOfficer } from "@/stores/authStore";
import { getReadNotificationIds, splitFullName } from "@/lib/superAdminProfile";
import type { AccountProfileData, UpdateAccountProfileInput } from "@/types/api/accountProfile";
import type { ActivityFeedItem } from "@/types/api/executiveDashboard";
import type { SuperAdminNotification } from "@/types/api/superAdmin";
import type { UserItem } from "@/types/api/users";

function mapActivityToNotification(
  item: ActivityFeedItem,
  readIds: Set<string>,
): SuperAdminNotification {
  return {
    id: item.id,
    title: item.title,
    description: item.detail,
    occurred_at: item.occurred_at,
    category: item.category,
    is_read: readIds.has(item.id),
  };
}

function collectNotifications(
  feeds: ActivityFeedItem[][],
  readIds: Set<string>,
): SuperAdminNotification[] {
  const seen = new Set<string>();
  const notifications: SuperAdminNotification[] = [];

  feeds.flat().forEach((item) => {
    if (seen.has(item.id)) return;
    seen.add(item.id);
    notifications.push(mapActivityToNotification(item, readIds));
  });

  return notifications.sort(
    (left, right) => new Date(right.occurred_at).getTime() - new Date(left.occurred_at).getTime(),
  );
}

async function findCurrentUserRecord(): Promise<UserItem | null> {
  const officer = getStoredOfficer();
  if (!officer) return null;

  const bySearch = await usersService.list({ search: officer.username, page_size: 20 });
  return bySearch.items.find((item) => item.officer_id === officer.officer_id) ?? null;
}

export const superAdminService = {
  async getNotifications(): Promise<SuperAdminNotification[]> {
    const dashboard = await executiveDashboardService.getDashboard({});
    const readIds = getReadNotificationIds();
    return collectNotifications(
      [
        dashboard.recent_high_risk_alerts,
        dashboard.recent_officer_activity,
        dashboard.recent_reports_generated,
        dashboard.recent_investigations,
      ],
      readIds,
    );
  },

  async getProfile(): Promise<AccountProfileData> {
    const [me, userRecord] = await Promise.all([authService.me(), findCurrentUserRecord()]);
    const officer = me.officer;

    return {
      officer_id: officer.officer_id,
      employee_id: userRecord?.employee_id ?? officer.employee_id,
      full_name: userRecord?.full_name ?? `${officer.first_name} ${officer.last_name}`.trim(),
      email: userRecord?.email ?? officer.email,
      phone_number: userRecord?.phone_number ?? officer.phone_number,
      role: userRecord?.role ?? me.role,
      created_at: userRecord?.created_at ?? null,
      last_login_at: userRecord?.last_login_at ?? null,
    };
  },

  async updateProfile(input: UpdateAccountProfileInput & { current: AccountProfileData }): Promise<AccountProfileData> {
    const { firstName, lastName } = splitFullName(input.fullName);
    const userRecord = await findCurrentUserRecord();
    if (!userRecord) {
      throw new Error("Unable to load account record for update.");
    }

    await usersService.update(input.current.officer_id, {
      employee_id: input.employeeId.trim(),
      first_name: firstName,
      last_name: lastName,
      email: input.email.trim(),
      phone_number: input.phoneNumber.trim() || undefined,
      rank: userRecord.rank,
      role: userRecord.role,
      police_station: userRecord.police_station,
      district: userRecord.district ?? undefined,
      status: userRecord.status,
    });

    return this.getProfile();
  },

  async changePassword(input: {
    username: string;
    currentPassword: string;
    newPassword: string;
    officerId: string;
  }): Promise<void> {
    await authService.login({
      identifier: input.username,
      password: input.currentPassword,
    });
    await usersService.resetPassword(input.officerId, { new_password: input.newPassword });
  },
};
