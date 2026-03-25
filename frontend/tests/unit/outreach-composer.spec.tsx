import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";

import { OutreachComposer } from "../../src/features/outreach/OutreachComposer";

function renderWithProviders(component: React.ReactNode) {
  const client = new QueryClient();
  return render(<QueryClientProvider client={client}>{component}</QueryClientProvider>);
}

describe("OutreachComposer", () => {
  it("shows empty state when no experts are selected", () => {
    renderWithProviders(
      <OutreachComposer
        latestQuery="metadata workflows"
        selectedExperts={[]}
      />,
    );

    expect(screen.getByText("Select one expert to unlock the draft.")).toBeInTheDocument();
  });

  it("loads availability and shows a copy-ready draft for the selected expert", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [],
    });
    global.fetch = fetchMock as unknown as typeof fetch;

    renderWithProviders(
      <OutreachComposer
        latestQuery="metadata workflows"
        selectedExperts={[
          {
            expert_id: "11111111-1111-1111-1111-111111111111",
            full_name: "Ada Lovelace",
            email: "ada@example.org",
            aggregate_similarity_score: 0.95,
            matched_document_excerpt: "Metadata workflows",
          },
        ]}
      />,
    );

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/v1/experts/11111111-1111-1111-1111-111111111111/availability",
        expect.any(Object),
      );
    });
    expect(screen.getByText("ada@example.org")).toBeInTheDocument();
    expect(screen.getByText("Copy full email")).toBeInTheDocument();
    expect(screen.getByText("Choose possible times")).toBeInTheDocument();
    expect(screen.getByDisplayValue(/Hello Dr\. Lovelace,/)).toBeInTheDocument();
  });
});
