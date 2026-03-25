import { NavLink, Outlet, createBrowserRouter, useLocation } from "react-router-dom";

import { ExpertProfilePage } from "../pages/ExpertProfilePage";
import { RequesterSearchPage } from "../pages/RequesterSearchPage";
import { ExpertEditPage } from "../features/expert-profile/ExpertEditPage";

function Layout() {
  const location = useLocation();
  const onExpertRoute = location.pathname.startsWith("/experts");

  return (
    <main className="layout">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />
      <div className="shell">
        <header className="topbar">
          <a
            className="brand-link"
            href="https://ossig.netlify.app/"
            target="_blank"
            rel="noreferrer"
            aria-label="Visit the OSSIG website"
          >
            <img
              className="brand-logo"
              src="https://ossig.netlify.app/images/logos/ossig_logo.svg"
              alt="OSSIG"
            />
          </a>
          <NavLink className="topbar-action" to={onExpertRoute ? "/" : "/experts"}>
            {onExpertRoute ? "Back to search" : "Experts: add yourself"}
          </NavLink>
        </header>
        <Outlet />
      </div>
    </main>
  );
}

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        index: true,
        element: <RequesterSearchPage />,
      },
      {
        path: "experts",
        element: <ExpertProfilePage />,
      },
      {
        path: "experts/manage",
        element: <ExpertEditPage />,
      },
    ],
  },
]);
