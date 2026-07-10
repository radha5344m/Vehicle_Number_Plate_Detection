import { useState } from "react";

import {
  ChangePasswordSection,
  EditProfileSection,
  ProfileInformationSection,
  SuccessBanner,
} from "@/components/features/profile/ProfilePageSections";
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { useStationAdminAccountProfile } from "@/hooks/stationAdmin/useStationAdminAccountProfile";
import { AppLayout } from "@/layouts/AppLayout";
import { removeStoredProfilePhoto, saveStoredProfilePhoto } from "@/lib/superAdminProfile";
import { stationAdminAccountService } from "@/services/stationAdminAccountService";
import { updateStoredOfficer } from "@/stores/authStore";

export function StationProfilePage() {
  const { data, loading, error, refresh } = useStationAdminAccountProfile();
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);

  return (
    <AppLayout>
      <div className="mx-auto max-w-5xl space-y-6">
        <PageHeader
          badge="ADMINISTRATION"
          title="Profile & Account Settings"
          description="View and manage your account details, security settings, and profile photo."
        />

        {message && <SuccessBanner message={message} />}

        {actionError && (
          <Alert variant="error" title="Update Failed">
            {actionError}
          </Alert>
        )}

        {loading && <LoadingState label="Loading profile..." fullHeight />}

        {error && !loading && (
          <Alert variant="warning" title="Profile Unavailable">
            {error}
          </Alert>
        )}

        {data && !loading && (
          <div className="space-y-6">
            <ProfileInformationSection
              profile={data}
              photoUrl={photoUrl}
              onPhotoChange={(dataUrl) => {
                saveStoredProfilePhoto(data.officer_id, dataUrl);
                setPhotoUrl(dataUrl);
                setMessage("Profile photo updated successfully.");
                setActionError(null);
              }}
              onPhotoRemove={() => {
                removeStoredProfilePhoto(data.officer_id);
                setPhotoUrl(null);
                setMessage("Profile photo removed successfully.");
                setActionError(null);
              }}
              onPhotoError={(photoError) => {
                setActionError(photoError);
                setMessage(null);
              }}
            />

            <EditProfileSection
              profile={data}
              includeEmployeeId
              saving={savingProfile}
              onSubmit={async (input) => {
                setSavingProfile(true);
                setMessage(null);
                setActionError(null);
                try {
                  const updated = await stationAdminAccountService.updateProfile(input);
                  const [firstName, ...rest] = updated.full_name.split(/\s+/);
                  updateStoredOfficer({
                    first_name: firstName,
                    last_name: rest.join(" ") || firstName,
                    email: updated.email,
                    phone_number: updated.phone_number,
                    employee_id: updated.employee_id,
                  });
                  setMessage("Profile saved successfully.");
                  refresh();
                } catch (err) {
                  setActionError(err instanceof Error ? err.message : "Failed to save profile");
                } finally {
                  setSavingProfile(false);
                }
              }}
            />

            <ChangePasswordSection
              saving={savingPassword}
              onSubmit={async (currentPassword, newPassword, confirmPassword) => {
                if (newPassword !== confirmPassword) {
                  setActionError("New password and confirmation do not match.");
                  setMessage(null);
                  throw new Error("Password mismatch");
                }
                setSavingPassword(true);
                setMessage(null);
                setActionError(null);
                try {
                  await stationAdminAccountService.changePassword(currentPassword, newPassword);
                  setMessage("Password updated successfully.");
                } catch (err) {
                  setActionError(err instanceof Error ? err.message : "Failed to update password");
                  throw err;
                } finally {
                  setSavingPassword(false);
                }
              }}
            />
          </div>
        )}
      </div>
    </AppLayout>
  );
}
