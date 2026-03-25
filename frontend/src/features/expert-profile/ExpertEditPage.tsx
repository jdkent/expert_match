import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { AvailabilityGrid } from "../availability/AvailabilityGrid";
import { DeleteProfileDialog } from "./DeleteProfileDialog";
import { expertProfilesApi } from "../../services/expertProfiles";

export function ExpertEditPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const preloadedAccessKey =
    typeof location.state === "object" &&
    location.state !== null &&
    "accessKey" in location.state &&
    typeof location.state.accessKey === "string"
      ? location.state.accessKey.trim()
      : "";
  const [accessKey, setAccessKey] = useState(preloadedAccessKey);
  const [submittedAccessKey, setSubmittedAccessKey] = useState<string | null>(
    preloadedAccessKey || null,
  );
  const { data, error, refetch } = useQuery({
    queryKey: ["expert-edit", submittedAccessKey],
    queryFn: () => expertProfilesApi.getProfileForAccessKey(submittedAccessKey!),
    enabled: submittedAccessKey !== null,
  });
  const [draft, setDraft] = useState<Record<string, string>>({});
  const [expertiseEntriesDraft, setExpertiseEntriesDraft] = useState<string[]>([]);
  const [selectedSlotIds, setSelectedSlotIds] = useState<string[]>([]);
  const [saveState, setSaveState] = useState("");

  const slotIds = useMemo(
    () =>
      data?.availability_slots.filter((slot) => slot.is_available).map((slot) => slot.slot_id) ?? [],
    [data],
  );

  useEffect(() => {
    setSelectedSlotIds(slotIds);
  }, [slotIds]);

  useEffect(() => {
    setExpertiseEntriesDraft(data?.expertise_entries.length ? data.expertise_entries : [""]);
  }, [data]);

  useEffect(() => {
    if (!data) {
      setDraft({});
      setSaveState("");
      return;
    }
    setDraft({
      full_name: data.full_name,
      orcid_id: data.orcid_id ?? "",
      website_url: data.website_url ?? "",
      x_handle: data.x_handle ?? "",
      linkedin_identifier: data.linkedin_identifier ?? "",
      bluesky_identifier: data.bluesky_identifier ?? "",
      github_handle: data.github_handle ?? "",
    });
    setSaveState("");
  }, [data]);

  const updateMutation = useMutation({
    mutationFn: async () =>
      expertProfilesApi.updateProfile(submittedAccessKey!, {
        full_name: draft.full_name,
        orcid_id: draft.orcid_id || null,
        website_url: draft.website_url || null,
        x_handle: draft.x_handle || null,
        linkedin_identifier: draft.linkedin_identifier || null,
        bluesky_identifier: draft.bluesky_identifier || null,
        github_handle: draft.github_handle || null,
        expertise_entries: expertiseEntriesDraft.map((entry) => entry.trim()).filter(Boolean),
        available_slot_ids: selectedSlotIds,
      }),
    onMutate: () => {
      setSaveState("Saving changes...");
    },
    onSuccess: async () => {
      await refetch();
      setSaveState("Profile changes saved.");
    },
    onError: (error) => {
      setSaveState(error instanceof Error ? error.message : "Could not save profile changes.");
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
        <div className="button-row">
          <button
            className="button-primary"
            onClick={() => updateMutation.mutate()}
            disabled={updateMutation.isPending}
          >
            {updateMutation.isPending ? "Saving..." : "Save profile changes"}
          </button>
        </div>
        {saveState ? <div className="muted">{saveState}</div> : null}
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
                value={draft[key] ?? value}
                onChange={(event) =>
                  {
                    setSaveState("");
                    setDraft((current) => ({ ...current, [key]: event.target.value }));
                  }
                }
              />
            </label>
          ))}
          <div className="field">
            <span>Expertise entries</span>
            <div className="expertise-rows">
              {expertiseEntriesDraft.map((entry, index) => (
                <div key={`expertise-entry-${index}`} className="expertise-row">
                  <input
                    aria-label={`Expertise entry ${index + 1}`}
                    value={entry}
                    onChange={(event) =>
                      {
                        setSaveState("");
                        setExpertiseEntriesDraft((current) =>
                          current.map((candidate, candidateIndex) =>
                            candidateIndex === index ? event.target.value : candidate,
                          ),
                        );
                      }
                    }
                  />
                  {expertiseEntriesDraft.length > 1 ? (
                    <button
                      type="button"
                      className="button-secondary expertise-remove"
                      onClick={() =>
                        setExpertiseEntriesDraft((current) =>
                          current.filter((_, candidateIndex) => candidateIndex !== index),
                        )
                      }
                    >
                      Remove
                    </button>
                  ) : null}
                </div>
              ))}
            </div>
            <div className="button-row">
              <button
                type="button"
                className="button-secondary"
                onClick={() => setExpertiseEntriesDraft((current) => [...current, ""])}
              >
                Add another expertise
              </button>
            </div>
          </div>
        </div>
        <AvailabilityGrid
          slots={data.availability_slots}
          selectedSlotIds={selectedSlotIds}
          onSelectAll={() => {
            setSaveState("");
            setSelectedSlotIds(
              data.availability_slots
                .filter((slot) => slot.is_available)
                .map((slot) => slot.slot_id),
            );
          }}
          onClearAll={() => {
            setSaveState("");
            setSelectedSlotIds([]);
          }}
          onSetSlotSelection={(slotId, isSelected) =>
            {
              setSaveState("");
              setSelectedSlotIds((current) =>
                isSelected
                  ? current.includes(slotId)
                    ? current
                    : [...current, slotId]
                  : current.filter((candidate) => candidate !== slotId),
              );
            }
          }
        />
        <button
          className="button-primary"
          onClick={() => updateMutation.mutate()}
          disabled={updateMutation.isPending}
        >
          {updateMutation.isPending ? "Saving..." : "Save profile changes"}
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
