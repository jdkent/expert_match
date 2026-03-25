import { useState } from "react";

type Props = {
  onConfirm: (emailConfirmation: string) => Promise<void>;
  expectedEmail: string;
};

export function DeleteProfileDialog({ onConfirm, expectedEmail }: Props) {
  const [emailConfirmation, setEmailConfirmation] = useState("");

  return (
    <section className="panel stack">
      <div>
        <h3>Delete profile</h3>
        <p className="muted">
          This is irreversible. Re-enter <strong>{expectedEmail}</strong> to confirm.
        </p>
      </div>
      <label className="field">
        <span>Email confirmation</span>
        <input
          value={emailConfirmation}
          onChange={(event) => setEmailConfirmation(event.target.value)}
        />
      </label>
      <button
        className="button-danger"
        onClick={() => onConfirm(emailConfirmation)}
        disabled={emailConfirmation.length === 0}
      >
        Delete permanently
      </button>
    </section>
  );
}
