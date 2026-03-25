from __future__ import annotations

import argparse
from collections.abc import Sequence

import httpx

from app.seed_data import METHODS_NEUROSCIENTIST_EXPERTS, SeedExpertProfile


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Seed a running Expert Match backend with methods-focused neuroscientists.",
    )
    parser.add_argument(
        "--api-base-url",
        default="http://localhost:8000",
        help="Base URL for the running backend API.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=len(METHODS_NEUROSCIENTIST_EXPERTS),
        help="Optional number of seed experts to ingest from the curated list.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=300.0,
        help="Read timeout for each request. First-time enrichment can take a few minutes.",
    )
    return parser


def ingest_expert(client: httpx.Client, expert: SeedExpertProfile) -> tuple[str, str]:
    create_response = client.post(
        "/api/v1/experts",
        json={
            "full_name": expert.full_name,
            "email": expert.email,
            "orcid_id": expert.orcid_id,
            "website_url": expert.website_url,
            "x_handle": expert.x_handle,
            "linkedin_identifier": expert.linkedin_identifier,
            "bluesky_identifier": expert.bluesky_identifier,
            "github_handle": expert.github_handle,
            "expertise_entries": list(expert.expertise_entries),
            "available_slot_ids": None,
        },
    )
    create_response.raise_for_status()
    created_payload = create_response.json()
    access_key = created_payload.get("access_key")
    if not access_key:
        raise RuntimeError(f"{expert.full_name} did not return an access key")
    return created_payload["profile_id"], access_key


def run(api_base_url: str, *, limit: int, timeout_seconds: float) -> int:
    selected_experts = METHODS_NEUROSCIENTIST_EXPERTS[:limit]
    if not selected_experts:
        raise ValueError("At least one expert must be selected for ingestion")
    timeout = httpx.Timeout(connect=10.0, read=timeout_seconds, write=60.0, pool=60.0)
    with httpx.Client(base_url=api_base_url.rstrip("/"), timeout=timeout) as client:
        for expert in selected_experts:
            profile_id, access_key = ingest_expert(client, expert)
            print(
                f"seeded {expert.full_name} <{expert.email}> "
                f"orcid={expert.orcid_id} profile_id={profile_id} access_key={access_key}"
            )
    print(f"completed ingestion for {len(selected_experts)} experts")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args.api_base_url, limit=args.limit, timeout_seconds=args.timeout_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
