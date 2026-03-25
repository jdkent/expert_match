import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { AvailabilityGrid } from "../availability/AvailabilityGrid";
import { DeleteProfileDialog } from "./DeleteProfileDialog";
import { expertProfilesApi } from "../../services/expertProfiles";

export function ExpertEditPage() {
  const navigate = useNavigate();
  const [accessKey, setAccessKey] = useState("");
  const [submittedAccessKey, setSubmittedAccessKey] = useState<string | null>(null);
  const { data, error, refetch } = useQuery({
    queryKey: ["expert-edit", submittedAccessKey],
    queryFn: () => expertProfilesApi.getProfileForAccessKey(submittedAccessKey!),
    enabled: submittedAccessKey !== null,
  });
  const [draft, setDraft] = useState<Record<string, string>>({});
  const [selectedSlotIds, setSelectedSlotIds] = useState<string[]>([]);

  const slotIds = useMemo(
    () =>
      data?.availability_slots.filter((slot) => slot.is_available).map((slot) => slot.slot_id) ?? [],
    [data],
  );

  useEffect(() => {
    setSelectedSlotIds(slotIds);
  }, [slotIds]);

  const updateMutation = useMutation({
    mutationFn: async () =>
      expertProfilesApi.updateProfile(submittedAccessKey!, {
        full_name: draft.full_name ?? data?.full_name,
        orcid_id: draft.orcid_id ?? data?.orcid_id ?? null,
        website_url: draft.website_url ?? data?.website_url ?? null,
        x_handle: draft.x_handle ?? data?.x_handle ?? null,
        linkedin_identifier: draft.linkedin_identifier ?? data?.linkedin_identifier ?? null,
        bluesky_identifier: draft.bluesky_identifier ?? data?.bluesky_identifier ?? null,
        github_handle: draft.github_handle ?? data?.github_handle ?? null,
        expertise_entries: (
          draft.expertise_entries
            ? draft.expertise_entries.split("\n").map((entry) => entry.trim()).filter(Boolean)
            : data?.expertise_entries
        ) ?? [],
        available_slot_ids: selectedSlotIds,
      }),
    onSuccess: async () => {
      await refetch();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (emailConfirmation: string) =>
      expertProfilesApi.deleteProfile(submittedAccessKey!, emailConfirmation),
    onSuccess: () => navigate("/experts"),
  });

  if (!submittedAccessKey) {
    return (
      <section className="panel stack">
        <div>
          <h2>Unlock your profile</h2>
          <p className="muted">
            Paste the expert access key that was shown when you created the profile.
          </p>
        </div>
        <label className="field">
          <span>Expert access key</span>
          <input value={accessKey} onChange={(event) => setAccessKey(event.target.value)} />
        </label>
        <div className="button-row">
          <button
            className="button-primary"
            onClick={() => setSubmittedAccessKey(accessKey.trim())}
            disabled={accessKey.trim().length === 0}
          >
            Unlock profile
          </button>
        </div>
      </section>
    );
  }

  if (!data) {
    return (
      <section className="panel stack">
        <div>
          <h2>Unlock your profile</h2>
          <p className="muted">
            {error
              ? "That access key did not unlock an active profile. Check the key and try again."
              : "Loading expert profile..."}
          </p>
        </div>
        <div className="button-row">
          <button
            className="button-secondary"
            onClick={() => {
              setSubmittedAccessKey(null);
              setAccessKey("");
            }}
          >
            Use a different key
          </button>
        </div>
      </section>
    );
  }

  return (
    <div className="grid two-column">
      <section className="panel stack">
        <div>
          <h2>Edit profile</h2>
          <p className="muted">Update expertise, ORCID, public links, or availability.</p>
        </div>
        <div className="form-grid">
          {[
            ["full_name", data.full_name],
            ["orcid_id", data.orcid_id ?? ""],
            ["website_url", data.website_url ?? ""],
            ["x_handle", data.x_handle ?? ""],
            ["linkedin_identifier", data.linkedin_identifier ?? ""],
            ["bluesky_identifier", data.bluesky_identifier ?? ""],
            ["github_handle", data.github_handle ?? ""],
          ].map(([key, value]) => (
            <label key={key} className="field">
              <span>{key.replaceAll("_", " ")}</span>
              <input
                defaultValue={value}
                onChange={(event) =>
                  setDraft((current) => ({ ...current, [key]: event.target.value }))
                }
              />
            </label>
          ))}
          <label className="field">
            <span>Expertise entries</span>
            <textarea
              defaultValue={data.expertise_entries.join("\n")}
              onChange={(event) =>
                setDraft((current) => ({ ...current, expertise_entries: event.target.value }))
              }
            />
          </label>
        </div>
        <AvailabilityGrid
          slots={data.availability_slots}
          selectedSlotIds={selectedSlotIds}
          onSetSlotSelection={(slotId, isSelected) =>
            setSelectedSlotIds((current) =>
              isSelected
                ? current.includes(slotId)
                  ? current
                  : [...current, slotId]
                : current.filter((candidate) => candidate !== slotId),
            )
          }
        />
        <button className="button-primary" onClick={() => updateMutation.mutate()}>
          Save profile changes
        </button>
      </section>
      <DeleteProfileDialog
        expectedEmail={data.email}
        onConfirm={async (emailConfirmation) => {
          await deleteMutation.mutateAsync(emailConfirmation);
        }}
      />
    </div>
  );
}
