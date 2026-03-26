import { useQueries } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";

import { expertProfilesApi } from "../../services/expertProfiles";
import { MatchedExpert } from "../../services/matching";
import { AvailabilityGrid } from "../availability/AvailabilityGrid";

type Props = {
  latestQuery: string;
  selectedExperts: MatchedExpert[];
};

function formatSelectedSlots(
  slots: Array<{
    slot_id: string;
    local_date: string;
    local_start_time: string;
  }>,
) {
  if (slots.length === 0) {
    return "I did not pick a specific time yet, but I would still like to connect during OHBM 2026 if it makes sense.";
  }

  return slots
    .map((slot) => `- ${slot.local_date} at ${slot.local_start_time} Europe/Paris`)
    .join("\n");
}

async function copyText(value: string) {
  await navigator.clipboard.writeText(value);
}

function formatExpertSalutation(fullName: string) {
  const parts = fullName
    .trim()
    .split(/\s+/)
    .filter(Boolean);

  if (parts.length === 0) {
    return "Dr.";
  }

  return `Dr. ${parts[parts.length - 1]}`;
}

export function OutreachComposer({ latestQuery, selectedExperts }: Props) {
  const [messageBody, setMessageBody] = useState("");
  const [selectedSlotsByExpert, setSelectedSlotsByExpert] = useState<Record<string, string[]>>({});
  const [copyState, setCopyState] = useState<string>("");
  const [scheduleExpanded, setScheduleExpanded] = useState(false);

  useEffect(() => {
    setScheduleExpanded(false);
  }, [selectedExperts]);

  const availabilityQueries = useQueries({
    queries: selectedExperts.map((expert) => ({
      queryKey: ["outreach-availability", expert.expert_id],
      queryFn: () => expertProfilesApi.getAvailability(expert.expert_id),
    })),
  });

  const primaryExpert = selectedExperts[0] ?? null;
  const primaryExpertId = primaryExpert?.expert_id ?? "";
  const primaryAvailability = primaryExpert ? availabilityQueries[0].data ?? [] : [];
  const selectedPrimarySlots = primaryAvailability.filter((slot) =>
    (selectedSlotsByExpert[primaryExpertId] ?? []).includes(slot.slot_id),
  );

  const draftSubject = useMemo(() => {
    if (!primaryExpert) {
      return "";
    }
    return `Question about ${latestQuery || "your expertise"} during OHBM Bordeaux 2026`;
  }, [latestQuery, primaryExpert]);

  const draftBody = useMemo(() => {
    if (!primaryExpert) {
      return "";
    }

    const intro = messageBody.trim().length
      ? messageBody.trim()
      : `I found your profile through ohbmatchmaker.org and I think your background may be a strong fit for my question about "${latestQuery}".`;

    return [
      `Hello ${formatExpertSalutation(primaryExpert.full_name)},`,
      "",
      intro,
      "",
      `My question: ${latestQuery}`,
      "",
      "Times that looked good to me:",
      formatSelectedSlots(
        selectedPrimarySlots.map((slot) => ({
          slot_id: slot.slot_id,
          local_date: slot.local_date,
          local_start_time: slot.local_start_time,
        })),
      ),
      "",
      "Best,",
      "[Your name]",
    ].join("\n");
  }, [latestQuery, messageBody, primaryExpert, selectedPrimarySlots]);

  const fullDraft = useMemo(() => {
    if (!primaryExpert) {
      return "";
    }
    return [`To: ${primaryExpert.email}`, `Subject: ${draftSubject}`, "", draftBody].join("\n");
  }, [draftBody, draftSubject, primaryExpert]);

  const mailtoHref = primaryExpert
    ? `mailto:${encodeURIComponent(primaryExpert.email)}?subject=${encodeURIComponent(draftSubject)}&body=${encodeURIComponent(draftBody)}`
    : "#";

  return (
    <section className="panel stack">
      <div>
        <h2>Email draft</h2>
        <p className="muted">
          Pick your preferred expert, adjust the note if needed, then copy the draft into
          your own email client (or open the draft directly into your email client).
        </p>
      </div>
      {selectedExperts.length > 0 ? (
        <>
          <div className="stack">
            <div>
              <h3>Selected expert</h3>
              <p className="muted">
                The draft below is generated for the single expert you selected.
              </p>
            </div>
            {primaryExpert ? (
              <div className="draft-value">{primaryExpert.full_name}</div>
            ) : null}
          </div>
          <label className="field">
            <span>Your note</span>
            <textarea
              placeholder="Optional: add a short note about what you want help with."
              value={messageBody}
              onChange={(event) => setMessageBody(event.target.value)}
            />
          </label>
          {primaryExpert ? (
            <details
              className="schedule-accordion"
              open={scheduleExpanded}
              onToggle={(event) => setScheduleExpanded((event.currentTarget as HTMLDetailsElement).open)}
            >
              <summary>
                {scheduleExpanded ? "Hide time selection" : "Choose possible times"}
              </summary>
              <div className="schedule-accordion-body stack">
                <p className="muted">
                  Pick zero or more times that work for you. They will be inserted into the draft.
                </p>
                {primaryAvailability.length > 0 ? (
                  <AvailabilityGrid
                    slots={primaryAvailability}
                    selectedSlotIds={selectedSlotsByExpert[primaryExpert.expert_id] ?? []}
                    onSetSlotSelection={(slotId, isSelected) =>
                      setSelectedSlotsByExpert((current) => {
                        const currentSlots = current[primaryExpert.expert_id] ?? [];
                        return {
                          ...current,
                          [primaryExpert.expert_id]: isSelected
                            ? currentSlots.includes(slotId)
                              ? currentSlots
                              : [...currentSlots, slotId]
                            : currentSlots.filter((candidate) => candidate !== slotId),
                        };
                      })
                    }
                  />
                ) : (
                  <div className="muted">
                    No current availability is shown. You can still draft an email without proposing a time.
                  </div>
                )}
              </div>
            </details>
          ) : null}
          {primaryExpert ? (
            <div className="draft-card stack">
              <div className="draft-meta">
                <div>
                  <span className="draft-label">To</span>
                  <div className="draft-value">{primaryExpert.email}</div>
                </div>
                <div>
                  <span className="draft-label">Subject</span>
                  <div className="draft-value">{draftSubject}</div>
                </div>
              </div>
              <label className="field">
                <span>Email body</span>
                <textarea className="draft-textarea" readOnly value={draftBody} />
              </label>
              <div className="button-row">
                <button
                  className="button-primary"
                  onClick={async () => {
                    await copyText(fullDraft);
                    setCopyState("Copied full draft");
                  }}
                >
                  Copy full email
                </button>
                <button
                  className="button-secondary"
                  onClick={async () => {
                    await copyText(draftBody);
                    setCopyState("Copied body");
                  }}
                >
                  Copy body only
                </button>
                <a className="button-secondary button-link" href={mailtoHref}>
                  Open in email app
                </a>
              </div>
              {copyState ? <div className="muted">{copyState}</div> : null}
            </div>
          ) : null}
        </>
      ) : (
        <div className="result-card">
          <p className="muted">
            Select an expert to see the email draft.
          </p>
        </div>
      )}
    </section>
  );
}
