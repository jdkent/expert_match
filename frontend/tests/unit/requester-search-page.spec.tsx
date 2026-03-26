import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { Layout } from "../../src/app/router";
import { RequesterSearchPage } from "../../src/pages/RequesterSearchPage";
import { MatchResponse } from "../../src/services/matching";

const mockMatchResponse: MatchResponse = {
  match_query_id: "query-1",
  applied_match_acceptance_threshold: 0.8,
  matches: [
    {
      expert_id: "expert-1",
      full_name: "Ada Lovelace",
      email: "ada@example.org",
      short_bio: "Computing pioneer",
      aggregate_similarity_score: 0.91,
      matched_document_excerpt: "Computing methods and analysis.",
    },
  ],
};

vi.mock("../../src/features/matching/MatchQueryForm", () => ({
  MatchQueryForm: ({
    onMatches,
    compact = false,
  }: {
    onMatches: (response: MatchResponse, queryText: string) => void;
    compact?: boolean;
  }) => (
    <button onClick={() => onMatches(mockMatchResponse, "remove")}>
      {compact ? "Update results" : "Find experts"}
    </button>
  ),
}));

vi.mock("../../src/features/matching/MatchedExpertList", () => ({
  MatchedExpertList: ({ experts }: { experts: MatchResponse["matches"] }) => (
    <div>Matched experts: {experts.length}</div>
  ),
}));

vi.mock("../../src/features/outreach/OutreachComposer", () => ({
  OutreachComposer: ({ latestQuery }: { latestQuery: string }) => <div>Outreach query: {latestQuery}</div>,
}));

function renderRequesterSearchPage() {
  const client = new QueryClient();

  return render(
    <MemoryRouter initialEntries={["/"]}>
      <QueryClientProvider client={client}>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<RequesterSearchPage />} />
          </Route>
        </Routes>
      </QueryClientProvider>
    </MemoryRouter>,
  );
}

describe("RequesterSearchPage", () => {
  it("clears prior results when the brand icon is used to return to search", () => {
    renderRequesterSearchPage();

    fireEvent.click(screen.getByRole("button", { name: "Find experts" }));

    expect(screen.getByRole("heading", { name: /Results for “remove”/ })).toBeInTheDocument();
    expect(screen.getByText("Matched experts: 1")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("link", { name: "Return to main search" }));

    expect(
      screen.getByRole("heading", { name: "Find the right expert for your question." }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: /Results for “remove”/ })).not.toBeInTheDocument();
    expect(screen.queryByText("Matched experts: 1")).not.toBeInTheDocument();
  });
});
