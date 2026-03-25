type SocialLinkKind = "website" | "x" | "linkedin" | "bluesky" | "github";

export type SocialLink = {
  kind: SocialLinkKind;
  href: string;
  label: string;
};

function normalizeUrl(value: string) {
  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }
  try {
    return new URL(trimmed.includes("://") ? trimmed : `https://${trimmed}`);
  } catch {
    return null;
  }
}

function withoutLeadingAt(value: string) {
  return value.trim().replace(/^@+/, "");
}

function normalizeExplicitUrl(value: string, explicitPrefixes: string[]) {
  const trimmed = withoutLeadingAt(value);
  if (!trimmed) {
    return null;
  }
  const lower = trimmed.toLowerCase();
  const looksExplicit =
    trimmed.includes("://") || explicitPrefixes.some((prefix) => lower.startsWith(prefix));
  if (!looksExplicit) {
    return null;
  }
  try {
    return new URL(trimmed.includes("://") ? trimmed : `https://${trimmed}`);
  } catch {
    return null;
  }
}

function parsedLabel(parsed: URL) {
  const pathParts = parsed.pathname.split("/").filter(Boolean);
  return pathParts.at(-1) ?? parsed.hostname.replace(/^www\./, "");
}

function normalizeHandleUrl(value: string, host: string) {
  const trimmed = withoutLeadingAt(value);
  const parsed = normalizeExplicitUrl(value, [host, `www.${host}`]);
  if (parsed) {
    return parsed.toString();
  }
  return `https://${host}/${trimmed}`;
}

function normalizeLinkedInUrl(value: string) {
  const trimmed = withoutLeadingAt(value);
  const parsed = normalizeExplicitUrl(value, ["linkedin.com/", "www.linkedin.com/"]);
  if (parsed) {
    return parsed.toString();
  }
  return `https://www.linkedin.com/in/${trimmed}`;
}

function websiteLabel(value: string) {
  const parsed = normalizeUrl(value);
  return parsed?.hostname.replace(/^www\./, "") ?? value.trim();
}

function socialLabel(value: string) {
  const parsed = normalizeUrl(value);
  if (parsed) {
    return parsedLabel(parsed);
  }
  return withoutLeadingAt(value);
}

export function buildSocialLinks(input: {
  websiteUrl?: string | null;
  xHandle?: string | null;
  linkedinIdentifier?: string | null;
  blueskyIdentifier?: string | null;
  githubHandle?: string | null;
}) {
  const links: SocialLink[] = [];

  if (input.websiteUrl?.trim()) {
    const parsed = normalizeUrl(input.websiteUrl);
    if (parsed) {
      links.push({
        kind: "website",
        href: parsed.toString(),
        label: websiteLabel(input.websiteUrl),
      });
    }
  }

  if (input.xHandle?.trim()) {
    links.push({
      kind: "x",
      href: normalizeHandleUrl(input.xHandle, "x.com"),
      label: socialLabel(input.xHandle),
    });
  }

  if (input.linkedinIdentifier?.trim()) {
    links.push({
      kind: "linkedin",
      href: normalizeLinkedInUrl(input.linkedinIdentifier),
      label: socialLabel(input.linkedinIdentifier),
    });
  }

  if (input.blueskyIdentifier?.trim()) {
    links.push({
      kind: "bluesky",
      href: normalizeHandleUrl(input.blueskyIdentifier, "bsky.app/profile"),
      label: socialLabel(input.blueskyIdentifier),
    });
  }

  if (input.githubHandle?.trim()) {
    links.push({
      kind: "github",
      href: normalizeHandleUrl(input.githubHandle, "github.com"),
      label: socialLabel(input.githubHandle),
    });
  }

  return links;
}
