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

  const createMutation = useMutation({
    mutationFn: async () => {
      const expertise_entries = expertiseEntries.map((entry) => entry.trim()).filter(Boolean);
      return expertProfilesApi.createProfile({
        ...form,
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
      onCreated(form.email);
    },
  });

  return (
    <section className="panel stack">
      <div>
        <h2>Publish your profile</h2>
        <p className="muted">
          No account required. Add one short expertise topic per row. The same
          form and API routes work in local development and behind production ingress.
        </p>
      </div>
      <div className="form-grid">
        {[
          ["full_name", "Full name"],
          ["email", "Email"],
          ["orcid_id", "ORCID ID"],
          ["website_url", "Website"],
          ["x_handle", "X handle"],
          ["linkedin_identifier", "LinkedIn"],
          ["bluesky_identifier", "Bluesky"],
          ["github_handle", "GitHub"],
        ].map(([key, label]) => (
          <label key={key} className="field">
            <span>{label}</span>
            <input
              name={key}
              value={form[key as keyof typeof form]}
              onChange={(event) =>
                setForm((current) => ({ ...current, [key]: event.target.value }))
              }
            />
          </label>
        ))}
        <div className="field">
          <span>Expertise entries</span>
          <div className="expertise-rows">
            {expertiseEntries.map((entry, index) => (
              <div key={`expertise-entry-${index}`} className="expertise-row">
                <input
                  aria-label={`Expertise entry ${index + 1}`}
                  value={entry}
                  onChange={(event) =>
                    setExpertiseEntries((current) =>
                      current.map((candidate, candidateIndex) =>
                        candidateIndex === index ? event.target.value : candidate,
                      ),
                    )
                  }
                />
                {expertiseEntries.length > 1 ? (
                  <button
                    type="button"
                    className="button-secondary expertise-remove"
                    onClick={() =>
                      setExpertiseEntries((current) =>
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
              onClick={() => setExpertiseEntries((current) => [...current, ""])}
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
            Leave everything unchecked to use the default of all Bordeaux event slots.
          </p>
        </div>
        <AvailabilityGrid
          slots={canonicalSlots.map((slot) => ({
            ...slot,
            is_available: true,
            attendee_request_count: 0,
          }))}
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
      </div>
      <div className="button-row">
        <button className="button-primary" onClick={() => createMutation.mutate()}>
          Submit profile
        </button>
      </div>
      {createMutation.error ? <div>{String(createMutation.error)}</div> : null}
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
