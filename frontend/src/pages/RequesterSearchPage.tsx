import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { MatchQueryForm } from "../features/matching/MatchQueryForm";
import { MatchedExpertList } from "../features/matching/MatchedExpertList";
import { OutreachComposer } from "../features/outreach/OutreachComposer";
import { MatchedExpert, MatchResponse } from "../services/matching";

export const SEARCH_PAGE_RESET_PARAM = "reset";

export function RequesterSearchPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [matchResponse, setMatchResponse] = useState<MatchResponse | null>(null);
  const [latestQuery, setLatestQuery] = useState("");
  const [selectedExpertId, setSelectedExpertId] = useState<string | null>(null);
  const resetRequested = searchParams.get(SEARCH_PAGE_RESET_PARAM) === "1";

  useEffect(() => {
    if (!resetRequested) {
      return;
    }

    setMatchResponse(null);
    setLatestQuery("");
    setSelectedExpertId(null);
    navigate("/", { replace: true });
  }, [navigate, resetRequested]);

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
            Review up to five distinct experts, select the single person you want to contact,
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
