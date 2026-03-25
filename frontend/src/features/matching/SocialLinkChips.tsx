import { buildSocialLinks, type SocialLink } from "../../utils/socialLinks";

type Props = {
  websiteUrl?: string | null;
  xHandle?: string | null;
  linkedinIdentifier?: string | null;
  blueskyIdentifier?: string | null;
  githubHandle?: string | null;
};

function SocialIcon({ kind }: { kind: SocialLink["kind"] }) {
  switch (kind) {
    case "website":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.8" />
          <path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
        </svg>
      );
    case "x":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M5 4h3.8l4.1 5.6L17.5 4H20l-5.9 6.8L20 20h-3.8L12 14.3 6.9 20H4.4l6.2-7.1z" fill="currentColor" />
        </svg>
      );
    case "linkedin":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M6.2 8.3A1.8 1.8 0 1 0 6.2 4.7a1.8 1.8 0 0 0 0 3.6M4.7 9.9h3v9.4h-3zm4.9 0h2.9v1.3h.1c.4-.8 1.4-1.7 3-1.7 3.1 0 3.7 2 3.7 4.7v5.1h-3v-4.5c0-1.1 0-2.4-1.5-2.4s-1.7 1.1-1.7 2.3v4.6h-3z" fill="currentColor" />
        </svg>
      );
    case "bluesky":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 10.7c1.6-3 4.4-5.7 6.8-7.2 1.7-1 3.1-.8 3.1 1.2 0 2-1 6.5-1.6 8.9-.8 3.1-2.6 3.8-4.2 3.5 2.8.5 3.5 2 1.9 3.6-3.1 3-4.5-.8-4.9-1.8-.1-.2-.1-.3-.2-.2 0 0 0 .1-.2.2-.4 1-1.8 4.8-4.9 1.8-1.6-1.6-.9-3.1 1.9-3.6-1.6.3-3.4-.4-4.2-3.5C3 11.2 2 6.8 2 4.7c0-2 1.4-2.2 3.1-1.2 2.4 1.5 5.2 4.2 6.9 7.2" fill="currentColor" />
        </svg>
      );
    case "github":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 2.5a9.5 9.5 0 0 0-3 18.5c.5.1.7-.2.7-.5v-1.8c-2.9.6-3.5-1.2-3.5-1.2-.5-1.2-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 .1 1.6 1 1.6 1 .9 1.5 2.4 1.1 3 .8.1-.6.4-1.1.7-1.4-2.3-.3-4.7-1.1-4.7-5a4 4 0 0 1 1.1-2.8c-.1-.3-.5-1.3.1-2.7 0 0 .9-.3 3 .9a10 10 0 0 1 5.4 0c2.1-1.2 3-.9 3-.9.6 1.4.2 2.4.1 2.7a4 4 0 0 1 1.1 2.8c0 3.9-2.4 4.7-4.8 5 .4.3.8 1 .8 2v3c0 .3.2.6.7.5A9.5 9.5 0 0 0 12 2.5" fill="currentColor" />
        </svg>
      );
  }
}

export function SocialLinkChips(props: Props) {
  const links = buildSocialLinks(props);

  if (links.length === 0) {
    return null;
  }

  return (
    <div className="chip-row social-chip-row">
      {links.map((link) => (
        <a
          key={`${link.kind}:${link.href}`}
          className="chip social-chip"
          href={link.href}
          target="_blank"
          rel="noreferrer"
          title={link.href}
        >
          <span className="social-chip-icon">
            <SocialIcon kind={link.kind} />
          </span>
          <span className="social-chip-label">{link.label}</span>
        </a>
      ))}
    </div>
  );
}
