import { NavLink, Outlet, createBrowserRouter, useLocation } from "react-router-dom";

import { ExpertProfilePage } from "../pages/ExpertProfilePage";
import { RequesterSearchPage } from "../pages/RequesterSearchPage";
import { ExpertEditPage } from "../features/expert-profile/ExpertEditPage";

export function Layout() {
  const location = useLocation();
  const onExpertRoute = location.pathname.startsWith("/experts");
  const onExpertManageRoute = location.pathname.startsWith("/experts/manage");

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
          <div className="topbar-actions">
            {onExpertManageRoute ? (
              <>
                <NavLink className="topbar-action" to="/experts">
                  Back to expert page
                </NavLink>
                <NavLink className="topbar-action" to="/">
                  Back to search
                </NavLink>
              </>
            ) : (
              <NavLink className="topbar-action" to={onExpertRoute ? "/" : "/experts"}>
                {onExpertRoute ? "Back to search" : "Experts: add yourself"}
              </NavLink>
            )}
          </div>
        </header>
        <Outlet />
        <footer className="site-footer">
          <p className="muted site-footer-text">
            Questions or feedback? Contact{" "}
            <a className="site-footer-link" href="mailto:jamesdkent21@gmail.com">
              jamesdkent21@gmail.com
            </a>
            .
          </p>
        </footer>
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
