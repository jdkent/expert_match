import { MatchedExpert } from "../../services/matching";
import { SocialLinkChips } from "./SocialLinkChips";

type Props = {
  experts: MatchedExpert[];
  selectedExpertId: string | null;
  onToggleExpert: (expertId: string) => void;
};

export function MatchedExpertList({ experts, selectedExpertId, onToggleExpert }: Props) {
  return (
    <section className="panel stack matched-expert-panel">
      <div>
        <h2>Matched experts</h2>
        <p className="muted">
          One expert can only occupy one result slot, even if several documents match.
          Review the shortlist first, then choose the single expert you want to draft for.
        </p>
      </div>
      <div className="matched-expert-scroll">
        {experts.length === 0 ? (
          <div className="result-card">
            <h3>No experts cleared the threshold</h3>
            <p className="muted">
              Try a broader question, fewer acronyms, or a different description of the
              expertise you need.
            </p>
          </div>
        ) : null}
        {experts.map((expert) => (
          <article key={expert.expert_id} className="result-card">
            <div className="button-row">
              <label className="chip select-chip">
                <input
                  type="radio"
                  name="selectedExpert"
                  checked={selectedExpertId === expert.expert_id}
                  onChange={() => onToggleExpert(expert.expert_id)}
                />
                {selectedExpertId === expert.expert_id ? "Selected" : "Select"}
              </label>
              <span className="chip">Score {expert.aggregate_similarity_score.toFixed(3)}</span>
            </div>
            <h3>{expert.full_name}</h3>
            <p>{expert.matched_document_excerpt}</p>
            <SocialLinkChips
              websiteUrl={expert.website_url}
              xHandle={expert.x_handle}
              linkedinIdentifier={expert.linkedin_identifier}
              blueskyIdentifier={expert.bluesky_identifier}
              githubHandle={expert.github_handle}
            />
          </article>
        ))}
      </div>
    </section>
  );
}
