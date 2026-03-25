import { useState } from "react";

import { ExpertEditRecoveryForm } from "../features/expert-profile/ExpertEditRecoveryForm";
import { ExpertProfileForm } from "../features/expert-profile/ExpertProfileForm";

export function ExpertProfilePage() {
  const [message, setMessage] = useState(
    "Submit a profile, save the returned expert access key, and use that key for future edits or deletion.",
  );

  return (
    <div className="expert-stack">
      <section className="panel panel-callout">
        <p className="eyebrow">For experts</p>
        <h1>Publish your profile for OHBM Bordeaux 2026.</h1>
        <p className="muted">
          Share your contact information and expertise, and get connected with
          people who have questions in your area of expertise.
        </p>
      </section>
      <ExpertEditRecoveryForm />
      <ExpertProfileForm
        onCreated={(email) =>
          setMessage(`Profile created for ${email}. Save the expert access key shown below before leaving this page.`)
        }
      />
      <section className="panel panel-tight">
        <h2>What happens next?</h2>
        <p className="muted">{message}</p>
      </section>
    </div>
  );
}
