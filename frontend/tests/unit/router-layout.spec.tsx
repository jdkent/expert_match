import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { Layout } from "../../src/app/router";

function renderLayout(initialEntry: string) {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<div>Search page</div>} />
          <Route path="experts" element={<div>Expert page</div>} />
          <Route path="experts/manage" element={<div>Manage page</div>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe("Layout", () => {
  it("shows the shared feedback contact on every page", () => {
    renderLayout("/");

    expect(screen.getByRole("link", { name: "jamesdkent21@gmail.com" })).toHaveAttribute(
      "href",
      "mailto:jamesdkent21@gmail.com",
    );
    expect(screen.getByText(/Questions or comments\?/i)).toBeInTheDocument();
  });

  it("shows both back links on the expert manage page", () => {
    renderLayout("/experts/manage");

    expect(screen.getByRole("link", { name: "Back to expert page" })).toHaveAttribute("href", "/experts");
    expect(screen.getByRole("link", { name: "Back to search" })).toHaveAttribute("href", "/");
  });

  it("keeps the single search link on the expert profile page", () => {
    renderLayout("/experts");

    expect(screen.getByRole("link", { name: "Back to search" })).toHaveAttribute("href", "/");
    expect(screen.queryByRole("link", { name: "Back to expert page" })).not.toBeInTheDocument();
  });
});
