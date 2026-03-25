import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import { ExpertProfilePage } from "../../src/pages/ExpertProfilePage";

function renderWithProviders(component: React.ReactNode) {
  const client = new QueryClient();
  return render(
    <MemoryRouter>
      <QueryClientProvider client={client}>{component}</QueryClientProvider>
    </MemoryRouter>,
  );
}

describe("ExpertProfilePage", () => {
  it("surfaces the existing-profile path before the creation form", () => {
    renderWithProviders(<ExpertProfilePage />);

    const editHeading = screen.getByRole("heading", { name: "Edit an existing profile" });
    const profileHeading = screen.getByRole("heading", { name: "Profile Information" });

    expect(editHeading.compareDocumentPosition(profileHeading) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(screen.getByRole("link", { name: "Edit existing profile" })).toBeInTheDocument();
  });
});
