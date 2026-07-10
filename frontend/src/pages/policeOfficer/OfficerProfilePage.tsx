import { useState } from "react";

import {
  EditProfileSection,
  ProfileInformationSection,
  SuccessBanner,
} from "@/components/features/profile/ProfilePageSections";
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { usePoliceOfficerAccountProfile } from "@/hooks/policeOfficer/usePoliceOfficerAccountProfile";
import { AppLayout } from "@/layouts/AppLayout";
import { removeStoredProfilePhoto, saveStoredProfilePhoto } from "@/lib/superAdminProfile";
import { policeOfficerAccountService } from "@/services/policeOfficerAccountService";
import { updateStoredOfficer } from "@/stores/authStore";

export function OfficerProfilePage() {
  const { data, loading, error, refresh } = usePoliceOfficerAccountProfile();
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [savingProfile, setSavingProfile] = useState(false);

  return (
    <AppLayout>
      <div className="mx-auto max-w-5xl space-y-6">
        <PageHeader
          badge="PROFILE"
          title="Profile & Account Settings"
          description="View your account details and update your contact information."
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
              includeEmployeeId={false}
              saving={savingProfile}
              onSubmit={async (input) => {
                setSavingProfile(true);
                setMessage(null);
                setActionError(null);
                try {
                  const updated = await policeOfficerAccountService.updateProfile({
                    ...input,
                    employeeId: data.employee_id,
                  });
                  const [firstName, ...rest] = updated.full_name.split(/\s+/);
                  updateStoredOfficer({
                    first_name: firstName,
                    last_name: rest.join(" ") || firstName,
                    email: updated.email,
                    phone_number: updated.phone_number,
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
          </div>
        )}
      </div>
    </AppLayout>
  );
}
