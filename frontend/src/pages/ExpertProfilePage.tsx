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
        <h1>Publish your profile for Bordeaux 2026.</h1>
        <p className="muted">
          Share your expertise once, update it later with your access key, and stay visible for
          OHBM 2026 Bordeaux requests without creating an account.
        </p>
      </section>
      <ExpertProfileForm
        onCreated={(email) =>
          setMessage(`Profile created for ${email}. Save the expert access key shown below before leaving this page.`)
        }
      />
      <section className="panel panel-tight">
        <h2>What happens next?</h2>
        <p className="muted">{message}</p>
        <p className="muted">
          There is no account, inbox recovery, or emailed edit link. Possession of the
          expert access key is the only way to unlock later changes.
        </p>
      </section>
      <ExpertEditRecoveryForm />
    </div>
  );
}
