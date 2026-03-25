import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { ExpertEditPage } from "../../src/features/expert-profile/ExpertEditPage";

function renderWithProviders(component: React.ReactNode) {
  const client = new QueryClient();
  return render(
    <MemoryRouter
      initialEntries={[
        {
          pathname: "/experts/manage",
          state: { accessKey: "expert-access-key" },
        } as never,
      ]}
    >
      <QueryClientProvider client={client}>
        <Routes>
          <Route path="/experts/manage" element={component} />
        </Routes>
      </QueryClientProvider>
    </MemoryRouter>,
  );
}

describe("ExpertEditPage", () => {
  it("uses a preloaded access key to unlock the profile immediately", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        expert_id: "11111111-1111-1111-1111-111111111111",
        full_name: "Ada Lovelace",
        email: "ada@example.org",
        short_bio: "Mathematician and scientific computing pioneer.",
        orcid_id: null,
        website_url: null,
        x_handle: null,
        linkedin_identifier: null,
        bluesky_identifier: null,
        github_handle: null,
        expertise_entries: ["Metadata workflows"],
        availability_slots: [],
      }),
    });
    global.fetch = fetchMock as unknown as typeof fetch;

    renderWithProviders(<ExpertEditPage />);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/v1/expert-access/profile",
        expect.objectContaining({ method: "POST" }),
      );
    });
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Edit profile" })).toBeInTheDocument();
    });
    expect(screen.getByDisplayValue("Ada Lovelace")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Mathematician and scientific computing pioneer.")).toBeInTheDocument();
  });
});
