type Props = {
  experts: Array<{ expert_id: string; full_name: string }>;
  primaryExpertId: string;
  onChange: (expertId: string) => void;
};

export function PrimaryExpertSelector({ experts, primaryExpertId, onChange }: Props) {
  return (
    <div className="primary-selector">
      {experts.map((expert) => (
        <label key={expert.expert_id} className="primary-pill">
          <input
            type="radio"
            name="primaryExpert"
            checked={primaryExpertId === expert.expert_id}
            onChange={() => onChange(expert.expert_id)}
          />
          <span className="primary-pill-label">{expert.full_name}</span>
        </label>
      ))}
    </div>
  );
}
