import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { canonicalSlots } from "../availability/canonicalSlots";
import { AvailabilityGrid } from "../availability/AvailabilityGrid";
import { expertProfilesApi } from "../../services/expertProfiles";

type Props = {
  onCreated: (email: string) => void;
};

const emptyForm = {
  full_name: "",
  email: "",
  short_bio: "",
  orcid_id: "",
  website_url: "",
  x_handle: "",
  linkedin_identifier: "",
  bluesky_identifier: "",
  github_handle: "",
};

async function copyText(value: string) {
  await navigator.clipboard.writeText(value);
}

function formatMutationError(error: unknown, fallback: string) {
  if (!(error instanceof Error) || !error.message) {
    return fallback;
  }

  try {
    const parsed = JSON.parse(error.message) as { detail?: string };
    if (typeof parsed.detail === "string" && parsed.detail.trim().length > 0) {
      return parsed.detail;
    }
  } catch {
    // Fall through to the raw message when the response is not JSON.
  }

  return error.message;
}

const profileFields: Array<{
  key: keyof typeof emptyForm;
  label: string;
  type?: "email" | "url" | "text";
  placeholder?: string;
  hint?: string;
  multiline?: boolean;
}> = [
  {
    key: "full_name",
    label: "Full name",
    placeholder: "Ada Lovelace",
  },
  {
    key: "email",
    label: "Email",
    type: "email",
    placeholder: "ada@example.org",
  },
  {
    key: "short_bio",
    label: "Short bio",
    placeholder: "Cognitive neuroscientist focused on reproducible neuroimaging methods.",
    hint: "Optional. One or two sentences that help requesters understand your background.",
    multiline: true,
  },
  {
    key: "orcid_id",
    label: "ORCID ID",
    placeholder: "0000-0002-1825-0097",
    hint: "Optional. Paste the ORCID iD only; the full URL is not required.",
  },
  {
    key: "website_url",
    label: "Website",
    type: "url",
    placeholder: "https://yourlab.org",
  },
  {
    key: "x_handle",
    label: "X handle",
    placeholder: "@yourhandle or https://x.com/yourhandle",
    hint: "Handles and full profile URLs both work.",
  },
  {
    key: "linkedin_identifier",
    label: "LinkedIn",
    placeholder: "your-name or linkedin.com/in/your-name",
    hint: "Use your LinkedIn slug or the full profile URL.",
  },
  {
    key: "bluesky_identifier",
    label: "Bluesky",
    placeholder: "yourname.bsky.social",
  },
  {
    key: "github_handle",
    label: "GitHub",
    placeholder: "yourhandle or github.com/yourhandle",
  },
];

export function ExpertProfileForm({ onCreated }: Props) {
  const navigate = useNavigate();
  const [form, setForm] = useState(emptyForm);
  const [expertiseEntries, setExpertiseEntries] = useState([""]);
  const [selectedSlotIds, setSelectedSlotIds] = useState<string[]>(
    canonicalSlots.map((slot) => slot.slot_id),
  );
  const [createdProfile, setCreatedProfile] = useState<{
    email: string;
    accessKey: string;
  } | null>(null);
  const [copyState, setCopyState] = useState("");
  const [formError, setFormError] = useState("");

  const createMutation = useMutation({
    mutationFn: async () => {
      const expertise_entries = expertiseEntries.map((entry) => entry.trim()).filter(Boolean);
      if (expertise_entries.length === 0) {
        throw new Error("Add at least one expertise entry before submitting your profile.");
      }
      return expertProfilesApi.createProfile({
        ...form,
        short_bio: form.short_bio || null,
        orcid_id: form.orcid_id || null,
        website_url: form.website_url || null,
        x_handle: form.x_handle || null,
        linkedin_identifier: form.linkedin_identifier || null,
        bluesky_identifier: form.bluesky_identifier || null,
        github_handle: form.github_handle || null,
        expertise_entries,
        available_slot_ids: selectedSlotIds,
      });
    },
    onSuccess: (data) => {
      setCreatedProfile({ email: form.email, accessKey: data.access_key });
      setCopyState("");
      setFormError("");
      onCreated(form.email);
    },
    onError: (error) => {
      setFormError(formatMutationError(error, "Could not submit profile. Check the form and try again."));
    },
  });

  return (
    <section className="panel stack">
      <div>
        <h2>Profile Information</h2>
        <p className="muted">
          No account required. Add in as many areas of expertise and contact links as you'd like,
          then save the expert access key shown after submission to unlock future edits.
        </p>
        <p className="muted">
          For social profiles, you can paste either a handle or a full profile URL.
        </p>
      </div>
      <div className="form-grid">
        {profileFields.map(({ key, label, placeholder, type = "text", hint, multiline }) => (
          <label key={key} className="field">
            <span>{label}</span>
            {multiline ? (
              <textarea
                name={key}
                aria-label={label}
                placeholder={placeholder}
                maxLength={500}
                value={form[key as keyof typeof form]}
                onChange={(event) => {
                  setFormError("");
                  setForm((current) => ({ ...current, [key]: event.target.value }));
                }}
              />
            ) : (
              <input
                name={key}
                aria-label={label}
                type={type}
                placeholder={placeholder}
                value={form[key as keyof typeof form]}
                onChange={(event) => {
                  setFormError("");
                  setForm((current) => ({ ...current, [key]: event.target.value }));
                }}
              />
            )}
            {hint ? <span className="field-hint">{hint}</span> : null}
          </label>
        ))}
        <div className="field">
          <span>Expertise entries</span>
          <span className="field-hint">
            Please list areas of expertise that you are comfortable being contacted about. You can be both specific and broad here.
            For example, "cognitive neuroscience methods" is a broad category and "fMRI denoising techniques" is a more specific one, and you can include both as separate entries.
            You are encouraged to add multiple entries to increase the chances of good matches.
          </span>
          <div className="expertise-rows">
            {expertiseEntries.map((entry, index) => (
              <div key={`expertise-entry-${index}`} className="expertise-row">
                <input
                  aria-label={`Expertise entry ${index + 1}`}
                  placeholder="Cognitive neuroscience methods"
                  value={entry}
                  onChange={(event) => {
                    setFormError("");
                    setExpertiseEntries((current) =>
                      current.map((candidate, candidateIndex) =>
                        candidateIndex === index ? event.target.value : candidate,
                      ),
                    );
                  }}
                />
                {expertiseEntries.length > 1 ? (
                  <button
                    type="button"
                    className="button-secondary expertise-remove"
                    onClick={() => {
                      setFormError("");
                      setExpertiseEntries((current) =>
                        current.filter((_, candidateIndex) => candidateIndex !== index),
                      );
                    }}
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
              onClick={() => {
                setFormError("");
                setExpertiseEntries((current) => [...current, ""]);
              }}
            >
              Add another expertise
            </button>
          </div>
        </div>
      </div>
      <div className="stack">
        <div>
          <h3>Optional event availability</h3>
          <p className="muted">
            By default all time slots are available.
          </p>
        </div>
        <AvailabilityGrid
          slots={canonicalSlots.map((slot) => ({
            ...slot,
            is_available: true,
            attendee_request_count: 0,
          }))}
          selectedSlotIds={selectedSlotIds}
          onSelectAll={() => setSelectedSlotIds(canonicalSlots.map((slot) => slot.slot_id))}
          onClearAll={() => setSelectedSlotIds([])}
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
      </div>
      <div className="button-row">
        <button
          className="button-primary"
          onClick={() => createMutation.mutate()}
          disabled={createMutation.isPending}
        >
          {createMutation.isPending ? "Submitting..." : "Submit profile"}
        </button>
      </div>
      {formError ? <div className="token">{formError}</div> : null}
      {createdProfile ? (
        <div className="dialog-backdrop" role="presentation">
          <div
            className="dialog-card stack"
            role="dialog"
            aria-modal="true"
            aria-labelledby="expert-access-key-title"
          >
            <div className="stack">
              <h2 id="expert-access-key-title">Save your expert access key</h2>
              <p className="muted">
                This is the only key that can unlock updates for{" "}
                <span className="email-inline">{createdProfile.email}</span>. If you lose it,
                you will not be able to edit or delete this profile later.
              </p>
            </div>
            <div className="access-key-display">{createdProfile.accessKey}</div>
            <div className="button-row">
              <button
                className="button-secondary"
                onClick={async () => {
                  await copyText(createdProfile.accessKey);
                  setCopyState("Copied access key");
                }}
              >
                Copy access key
              </button>
              <button
                className="button-primary"
                onClick={() =>
                  navigate("/experts/manage", { state: { accessKey: createdProfile.accessKey } })
                }
              >
                Edit profile now
              </button>
              <button
                className="button-secondary"
                onClick={() => navigate("/")}
              >
                Return to search
              </button>
            </div>
            <div className="muted">
              Store it somewhere safe before leaving this dialog. The app will not email it back to you.
            </div>
            {copyState ? <div className="muted">{copyState}</div> : null}
          </div>
        </div>
      ) : null}
    </section>
  );
}
