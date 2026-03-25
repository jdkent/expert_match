import { buildSocialLinks } from "../../src/utils/socialLinks";

describe("buildSocialLinks", () => {
  it("builds canonical social URLs from bare identifiers", () => {
    expect(
      buildSocialLinks({
        xHandle: "@russellpoldrack_methods",
        linkedinIdentifier: "russell-poldrack",
        blueskyIdentifier: "russellpoldrack.seeded-experts.dev",
        githubHandle: "russellpoldrack-lab",
      }),
    ).toEqual([
      {
        kind: "x",
        href: "https://x.com/russellpoldrack_methods",
        label: "russellpoldrack_methods",
      },
      {
        kind: "linkedin",
        href: "https://www.linkedin.com/in/russell-poldrack",
        label: "russell-poldrack",
      },
      {
        kind: "bluesky",
        href: "https://bsky.app/profile/russellpoldrack.seeded-experts.dev",
        label: "russellpoldrack.seeded-experts.dev",
      },
      {
        kind: "github",
        href: "https://github.com/russellpoldrack-lab",
        label: "russellpoldrack-lab",
      },
    ]);
  });

  it("preserves explicit platform URLs", () => {
    expect(
      buildSocialLinks({
        xHandle: "https://x.com/russellpoldrack_methods",
        linkedinIdentifier: "linkedin.com/in/russell-poldrack",
        blueskyIdentifier: "bsky.app/profile/russellpoldrack.seeded-experts.dev",
        githubHandle: "github.com/russellpoldrack-lab",
      }),
    ).toEqual([
      {
        kind: "x",
        href: "https://x.com/russellpoldrack_methods",
        label: "russellpoldrack_methods",
      },
      {
        kind: "linkedin",
        href: "https://linkedin.com/in/russell-poldrack",
        label: "russell-poldrack",
      },
      {
        kind: "bluesky",
        href: "https://bsky.app/profile/russellpoldrack.seeded-experts.dev",
        label: "russellpoldrack.seeded-experts.dev",
      },
      {
        kind: "github",
        href: "https://github.com/russellpoldrack-lab",
        label: "russellpoldrack-lab",
      },
    ]);
  });
});
