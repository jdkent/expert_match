import { NavLink } from "react-router-dom";

export function ExpertEditRecoveryForm() {
  return (
    <section className="panel stack">
      <div>
        <h2>Use your access key</h2>
        <p className="muted">
          Experts manage existing profiles with the access key returned at creation
          time. There is no recovery email or inbox-based reset flow.
        </p>
      </div>
      <div className="button-row">
        <NavLink className="button-secondary button-link" to="/experts/manage">
          Open expert access panel
        </NavLink>
      </div>
    </section>
  );
}
