import { MatchedExpert } from "../../services/matching";

type Props = {
  experts: MatchedExpert[];
  selectedExpertId: string | null;
  onToggleExpert: (expertId: string) => void;
};

export function MatchedExpertList({ experts, selectedExpertId, onToggleExpert }: Props) {
  return (
    <section className="panel stack">
      <div>
        <h2>Matched experts</h2>
        <p className="muted">
          One expert can only occupy one result slot, even if several documents match.
          Review the shortlist first, then choose the single expert you want to draft for.
        </p>
      </div>
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
          <div className="chip-row">
            {expert.website_url ? (
              <a className="chip" href={expert.website_url} target="_blank" rel="noreferrer">
                Website
              </a>
            ) : null}
            {expert.x_handle ? <span className="chip">X: {expert.x_handle}</span> : null}
            {expert.linkedin_identifier ? (
              <span className="chip">LinkedIn: {expert.linkedin_identifier}</span>
            ) : null}
            {expert.bluesky_identifier ? (
              <span className="chip">Bluesky: {expert.bluesky_identifier}</span>
            ) : null}
            {expert.github_handle ? <span className="chip">GitHub: {expert.github_handle}</span> : null}
          </div>
        </article>
      ))}
    </section>
  );
}
