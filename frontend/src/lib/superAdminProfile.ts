const READ_NOTIFICATIONS_KEY = "sentinel_super_admin_read_notifications";
const PROFILE_PHOTO_KEY_PREFIX = "sentinel_super_admin_profile_photo_";

const ACCEPTED_PHOTO_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);
const MAX_PHOTO_BYTES = 2 * 1024 * 1024;

export function getReadNotificationIds(): Set<string> {
  const raw = localStorage.getItem(READ_NOTIFICATIONS_KEY);
  if (!raw) return new Set();
  try {
    return new Set(JSON.parse(raw) as string[]);
  } catch {
    return new Set();
  }
}

export function markNotificationRead(notificationId: string): void {
  const ids = getReadNotificationIds();
  ids.add(notificationId);
  localStorage.setItem(READ_NOTIFICATIONS_KEY, JSON.stringify([...ids]));
}

export function markAllNotificationsRead(notificationIds: string[]): void {
  const ids = getReadNotificationIds();
  notificationIds.forEach((id) => ids.add(id));
  localStorage.setItem(READ_NOTIFICATIONS_KEY, JSON.stringify([...ids]));
}

export function getStoredProfilePhoto(officerId: string): string | null {
  return localStorage.getItem(`${PROFILE_PHOTO_KEY_PREFIX}${officerId}`);
}

export function saveStoredProfilePhoto(officerId: string, dataUrl: string): void {
  localStorage.setItem(`${PROFILE_PHOTO_KEY_PREFIX}${officerId}`, dataUrl);
}

export function removeStoredProfilePhoto(officerId: string): void {
  localStorage.removeItem(`${PROFILE_PHOTO_KEY_PREFIX}${officerId}`);
}

export function validateProfilePhoto(file: File): string | null {
  if (!ACCEPTED_PHOTO_TYPES.has(file.type)) {
    return "Only JPG, PNG, and WEBP images are supported.";
  }
  if (file.size > MAX_PHOTO_BYTES) {
    return "Image must be 2 MB or smaller.";
  }
  return null;
}

export function readProfilePhoto(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === "string") {
        resolve(reader.result);
        return;
      }
      reject(new Error("Failed to read image file."));
    };
    reader.onerror = () => reject(new Error("Failed to read image file."));
    reader.readAsDataURL(file);
  });
}

export function splitFullName(fullName: string): { firstName: string; lastName: string } {
  const trimmed = fullName.trim();
  if (!trimmed) {
    return { firstName: "", lastName: "" };
  }
  const parts = trimmed.split(/\s+/);
  if (parts.length === 1) {
    return { firstName: parts[0], lastName: parts[0] };
  }
  return {
    firstName: parts[0],
    lastName: parts.slice(1).join(" "),
  };
}

export function formatRoleLabel(role: string): string {
  return role.replaceAll("_", " ");
}
