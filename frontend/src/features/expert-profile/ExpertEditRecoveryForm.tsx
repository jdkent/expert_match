import { NavLink } from "react-router-dom";

export function ExpertEditRecoveryForm() {
  return (
    <section className="panel expert-access-card">
      <div className="stack">
        <p className="eyebrow">Already published?</p>
        <h2>Edit an existing profile</h2>
        <p className="muted">
          Use the one-time expert access key returned at creation time to update or delete
          your profile.
        </p>
      </div>
      <div className="expert-access-actions">
        <NavLink className="button-secondary button-link expert-access-button" to="/experts/manage">
          Edit existing profile
        </NavLink>
        <p className="muted expert-access-note">
          No recovery email or inbox-based reset flow is available, so you will need that key.
        </p>
      </div>
    </section>
  );
}
