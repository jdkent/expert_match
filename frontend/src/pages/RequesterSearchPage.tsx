import { useMemo, useState } from "react";

import { MatchQueryForm } from "../features/matching/MatchQueryForm";
import { MatchedExpertList } from "../features/matching/MatchedExpertList";
import { OutreachComposer } from "../features/outreach/OutreachComposer";
import { MatchedExpert, MatchResponse } from "../services/matching";

export function RequesterSearchPage() {
  const [matchResponse, setMatchResponse] = useState<MatchResponse | null>(null);
  const [latestQuery, setLatestQuery] = useState("");
  const [selectedExpertId, setSelectedExpertId] = useState<string | null>(null);

  const selectedExperts = useMemo<MatchedExpert[]>(
    () => matchResponse?.matches.filter((match) => match.expert_id === selectedExpertId) ?? [],
    [matchResponse, selectedExpertId],
  );

  if (!matchResponse) {
    return (
      <section className="landing-hero">
        <div className="hero-lockup">
          <div className="hero-orbit" aria-hidden="true">
            <span className="hero-orbit-ring hero-orbit-ring-one" />
            <span className="hero-orbit-ring hero-orbit-ring-two" />
            <span className="hero-orbit-core" />
          </div>
          <h1 className="landing-title">Find the right expert for your question.</h1>
        </div>
        <MatchQueryForm
          onMatches={(response, queryText) => {
            setMatchResponse(response);
            setLatestQuery(queryText);
            setSelectedExpertId(response.matches[0]?.expert_id ?? null);
          }}
        />
      </section>
    );
  }

  return (
    <div className="page-stack">
      <section className="panel search-summary">
        <div>
          <p className="eyebrow">Search results</p>
          <h2>Results for “{latestQuery}”</h2>
          <p className="muted">
            Review up to five distinct experts, select the people you want to contact,
            and then generate a draft you can paste into your own email client.
          </p>
        </div>
        <div className="button-row">
          <button
            className="button-secondary"
            onClick={() => {
              setMatchResponse(null);
              setLatestQuery("");
              setSelectedExpertId(null);
            }}
          >
            Start a new search
          </button>
        </div>
      </section>
      <section className="panel panel-tight">
        <MatchQueryForm
          compact
          initialQueryText={latestQuery}
          onMatches={(response, queryText) => {
            setMatchResponse(response);
            setLatestQuery(queryText);
            setSelectedExpertId(response.matches[0]?.expert_id ?? null);
          }}
        />
      </section>
      <MatchedExpertList
        experts={matchResponse.matches}
        selectedExpertId={selectedExpertId}
        onToggleExpert={(expertId) =>
          setSelectedExpertId((current) => (current === expertId ? null : expertId))
        }
      />
      <OutreachComposer
        latestQuery={latestQuery}
        selectedExperts={selectedExperts}
      />
    </div>
  );
}
