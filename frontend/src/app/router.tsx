import { NavLink, Outlet, createBrowserRouter, useLocation } from "react-router-dom";

import { ExpertProfilePage } from "../pages/ExpertProfilePage";
import { RequesterSearchPage, SEARCH_PAGE_RESET_PARAM } from "../pages/RequesterSearchPage";
import { ExpertEditPage } from "../features/expert-profile/ExpertEditPage";

function NetworkMark() {
  return (
    <svg
      className="brand-mark"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      aria-hidden="true"
      fill="none"
    >
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.1" />
      <line x1="12" y1="10.6" x2="12" y2="16.6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <line x1="12" y1="6.1" x2="10.3" y2="8.4" stroke="currentColor" strokeWidth="1" strokeLinecap="round" />
      <line x1="12" y1="6.1" x2="13.7" y2="8.4" stroke="currentColor" strokeWidth="1" strokeLinecap="round" />
      <line x1="10.3" y1="8.4" x2="13.7" y2="8.4" stroke="currentColor" strokeWidth="1" strokeLinecap="round" />
      <circle cx="12" cy="6.1" r="1.25" fill="currentColor" />
      <circle cx="10.2" cy="8.6" r="1.25" fill="currentColor" />
      <circle cx="13.8" cy="8.6" r="1.25" fill="currentColor" />
    </svg>
  );
}

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
          <NavLink
            className="brand-link"
            to={`/?${SEARCH_PAGE_RESET_PARAM}=1`}
            aria-label="Return to main search"
          >
            <NetworkMark />
          </NavLink>
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
              <NavLink
                className={`topbar-action ${onExpertRoute ? "" : "topbar-action-prominent"}`.trim()}
                to={onExpertRoute ? "/" : "/experts"}
              >
                {onExpertRoute ? "Back to search" : "Add your expertise"}
              </NavLink>
            )}
          </div>
        </header>
        <Outlet />
        <footer className="site-footer">
          <div className="site-footer-row">
            <a
              className="site-footer-brand"
              href="https://ossig.netlify.app/"
              target="_blank"
              rel="noreferrer"
              aria-label="Visit the OSSIG website"
            >
              <img
                className="site-footer-brand-logo"
                src="https://ossig.netlify.app/images/logos/ossig_logo.svg"
                alt="OSSIG"
              />
            </a>
            <p className="muted site-footer-text">
              Questions or comments? Contact{" "}
              <a className="site-footer-link" href="mailto:jamesdkent21@gmail.com">
                jamesdkent21@gmail.com
              </a>
              .
            </p>
          </div>
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
