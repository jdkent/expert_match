import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";

import { MatchedExpertList } from "../../src/features/matching/MatchedExpertList";

function renderWithProviders(component: React.ReactNode) {
  const client = new QueryClient();
  return render(<QueryClientProvider client={client}>{component}</QueryClientProvider>);
}

describe("MatchedExpertList", () => {
  it("renders matched expert details", () => {
    renderWithProviders(
      <MatchedExpertList
        experts={[
          {
            expert_id: "11111111-1111-1111-1111-111111111111",
            full_name: "Ada Lovelace",
            email: "ada@example.org",
            aggregate_similarity_score: 0.91,
            matched_document_excerpt: "Metadata workflows",
          },
        ]}
        selectedExpertId="11111111-1111-1111-1111-111111111111"
        onToggleExpert={() => undefined}
      />,
    );

    expect(screen.getByText("Ada Lovelace")).toBeInTheDocument();
    expect(screen.getByText("Selected")).toBeInTheDocument();
  });
});
