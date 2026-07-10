import { useRef, useState, type FormEvent, type ReactNode } from "react";
import { Camera, CheckCircle2, UserCircle } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import {
  formatProfileDate,
  formatProfileTime,
  formatRoleLabel,
} from "@/lib/profileFormat";
import {
  getStoredProfilePhoto,
  readProfilePhoto,
  removeStoredProfilePhoto,
  saveStoredProfilePhoto,
  validateProfilePhoto,
} from "@/lib/superAdminProfile";
import type { AccountProfileData, UpdateAccountProfileInput } from "@/types/api/accountProfile";

export function ProfileSettingsCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
}) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-soft sm:p-8">
      <div className="mb-6 border-b border-slate-100 pb-5">
        <h2 className="text-lg font-semibold tracking-tight text-slate-900">{title}</h2>
        <p className="mt-1 text-sm leading-relaxed text-slate-500">{subtitle}</p>
      </div>
      {children}
    </section>
  );
}

export function InfoField({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-100 bg-slate-50/80 px-4 py-3.5">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1.5 break-all text-sm font-semibold text-slate-900">{value}</p>
    </div>
  );
}

export function SuccessBanner({ message }: { message: string }) {
  return (
    <div
      className="flex items-start gap-3 rounded-xl border border-green-200 bg-green-50 px-4 py-3.5 shadow-sm"
      role="status"
    >
      <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-green-600" aria-hidden />
      <p className="text-sm font-medium text-green-800">{message}</p>
    </div>
  );
}

export function ProfileInformationSection({
  profile,
  photoUrl,
  onPhotoChange,
  onPhotoRemove,
  onPhotoError,
}: {
  profile: AccountProfileData;
  photoUrl: string | null;
  onPhotoChange: (dataUrl: string) => void;
  onPhotoRemove: () => void;
  onPhotoError: (message: string) => void;
}) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const displayPhoto = photoUrl ?? getStoredProfilePhoto(profile.officer_id);

  return (
    <ProfileSettingsCard
      title="Profile Information"
      subtitle="Your account details and profile photo."
    >
      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)] lg:items-start">
        <div className="flex flex-col items-center text-center lg:items-start lg:text-left">
          <div className="flex h-36 w-36 items-center justify-center overflow-hidden rounded-full border-4 border-white bg-brand-soft shadow-soft ring-1 ring-slate-200">
            {displayPhoto ? (
              <img src={displayPhoto} alt="Profile" className="h-full w-full object-cover" />
            ) : (
              <UserCircle className="h-20 w-20 text-brand/60" strokeWidth={1.25} />
            )}
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (!file) return;
              const validationError = validateProfilePhoto(file);
              if (validationError) {
                onPhotoError(validationError);
                event.target.value = "";
                return;
              }
              void readProfilePhoto(file)
                .then(onPhotoChange)
                .catch((err) => {
                  onPhotoError(err instanceof Error ? err.message : "Failed to upload photo");
                })
                .finally(() => {
                  event.target.value = "";
                });
            }}
          />

          <div className="mt-5 flex w-full flex-col gap-2 sm:flex-row lg:w-auto">
            <Button type="button" className="w-full sm:w-auto" onClick={() => fileInputRef.current?.click()}>
              <Camera className="h-4 w-4" />
              Change Photo
            </Button>
            <Button
              type="button"
              variant="secondary"
              className="w-full sm:w-auto"
              disabled={!displayPhoto}
              onClick={onPhotoRemove}
            >
              Remove Photo
            </Button>
          </div>
          <p className="mt-3 text-xs leading-relaxed text-slate-500">JPG, PNG or WEBP up to 2 MB.</p>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <InfoField label="User ID" value={profile.officer_id} />
          <InfoField label="Employee ID" value={profile.employee_id} />
          <InfoField label="Role" value={formatRoleLabel(profile.role)} />
          <InfoField label="Account Created" value={formatProfileDate(profile.created_at)} />
          <InfoField label="Last Login Date" value={formatProfileDate(profile.last_login_at)} />
          <InfoField label="Last Login Time" value={formatProfileTime(profile.last_login_at)} />
        </div>
      </div>
    </ProfileSettingsCard>
  );
}

export function EditProfileSection({
  profile,
  includeEmployeeId,
  saving,
  onSubmit,
}: {
  profile: AccountProfileData;
  includeEmployeeId: boolean;
  saving: boolean;
  onSubmit: (input: UpdateAccountProfileInput) => Promise<void>;
}) {
  return (
    <ProfileSettingsCard
      title="Edit Profile"
      subtitle={
        includeEmployeeId
          ? "Update your name, email, phone number, and employee ID."
          : "Update your name, email and phone number."
      }
    >
      <form
        key={`${profile.officer_id}-${profile.full_name}-${profile.employee_id}`}
        className="space-y-5"
        onSubmit={(event: FormEvent<HTMLFormElement>) => {
          event.preventDefault();
          const form = new FormData(event.currentTarget);
          void onSubmit({
            fullName: String(form.get("full_name") ?? ""),
            email: String(form.get("email") ?? ""),
            phoneNumber: String(form.get("phone_number") ?? ""),
            employeeId: String(form.get("employee_id") ?? profile.employee_id),
          });
        }}
      >
        <Input name="full_name" label="Name *" defaultValue={profile.full_name} required />
        <Input name="email" label="Email *" type="email" defaultValue={profile.email} required />
        <Input
          name="phone_number"
          label="Phone Number *"
          defaultValue={profile.phone_number ?? ""}
          required
        />
        {includeEmployeeId && (
          <Input name="employee_id" label="Employee ID *" defaultValue={profile.employee_id} required />
        )}
        <div className="pt-1">
          <Button type="submit" className="w-full sm:w-auto" loading={saving}>
            Save Profile
          </Button>
        </div>
      </form>
    </ProfileSettingsCard>
  );
}

export function ChangePasswordSection({
  saving,
  onSubmit,
}: {
  saving: boolean;
  onSubmit: (currentPassword: string, newPassword: string, confirmPassword: string) => Promise<void>;
}) {
  return (
    <ProfileSettingsCard
      title="Change Password"
      subtitle="Use a strong password with at least 8 characters."
    >
      <form
        className="space-y-5"
        onSubmit={(event: FormEvent<HTMLFormElement>) => {
          event.preventDefault();
          const form = new FormData(event.currentTarget);
          void onSubmit(
            String(form.get("current_password") ?? ""),
            String(form.get("new_password") ?? ""),
            String(form.get("confirm_password") ?? ""),
          ).then(() => {
            event.currentTarget.reset();
          });
        }}
      >
        <Input name="current_password" label="Current Password *" type="password" required />
        <Input name="new_password" label="New Password *" type="password" required minLength={8} />
        <Input
          name="confirm_password"
          label="Confirm Password *"
          type="password"
          required
          minLength={8}
        />
        <div className="pt-1">
          <Button type="submit" className="w-full sm:w-auto" loading={saving}>
            Update Password
          </Button>
        </div>
      </form>
    </ProfileSettingsCard>
  );
}
