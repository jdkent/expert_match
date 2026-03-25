import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import { ExpertProfileForm } from "../../src/features/expert-profile/ExpertProfileForm";

function renderWithProviders(component: React.ReactNode) {
  const client = new QueryClient();
  return render(
    <MemoryRouter>
      <QueryClientProvider client={client}>{component}</QueryClientProvider>
    </MemoryRouter>,
  );
}

describe("ExpertProfileForm", () => {
  it("shows the one-time access key after submission", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 202,
      json: async () => ({ profile_id: "123", access_key: "expert-access-key" }),
    });
    global.fetch = fetchMock as unknown as typeof fetch;

    renderWithProviders(<ExpertProfileForm onCreated={() => undefined} />);
    fireEvent.change(screen.getByLabelText("Full name"), { target: { value: "Ada Lovelace" } });
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "ada@example.org" } });
    fireEvent.change(screen.getByLabelText("Expertise entry 1"), {
      target: { value: "Metadata workflows" },
    });
    fireEvent.click(screen.getByText("Submit profile"));

    await waitFor(() => {
      expect(screen.getByText(/Save your expert access key/i)).toBeInTheDocument();
    });
    expect(screen.getByText("expert-access-key")).toBeInTheDocument();
    expect(screen.getByText("Copy access key")).toBeInTheDocument();
    expect(screen.getByText("Edit profile now")).toBeInTheDocument();
    expect(screen.getByText("Return to search")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/experts",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("lets experts add more than one expertise row", () => {
    renderWithProviders(<ExpertProfileForm onCreated={() => undefined} />);

    fireEvent.click(screen.getByText("Add another expertise"));

    expect(screen.getByLabelText("Expertise entry 1")).toBeInTheDocument();
    expect(screen.getByLabelText("Expertise entry 2")).toBeInTheDocument();
  });

  it("shows a clear validation message when all expertise entries are blank", async () => {
    renderWithProviders(<ExpertProfileForm onCreated={() => undefined} />);

    fireEvent.change(screen.getByLabelText("Full name"), { target: { value: "Ada Lovelace" } });
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "ada@example.org" } });
    fireEvent.click(screen.getByText("Submit profile"));

    await waitFor(() => {
      expect(
        screen.getByText("Add at least one expertise entry before submitting your profile."),
      ).toBeInTheDocument();
    });
  });
});
