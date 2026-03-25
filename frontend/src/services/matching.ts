import { api } from "./api";

export type MatchRequest = {
  query_text: string;
};

export type MatchedExpert = {
  expert_id: string;
  full_name: string;
  email: string;
  short_bio?: string;
  aggregate_similarity_score: number;
  matched_document_excerpt: string;
  website_url?: string;
  x_handle?: string;
  linkedin_identifier?: string;
  bluesky_identifier?: string;
  github_handle?: string;
};

export type MatchResponse = {
  match_query_id: string;
  applied_match_acceptance_threshold: number;
  matches: MatchedExpert[];
};

export const matchingApi = {
  createQuery: (payload: MatchRequest) => api.post<MatchResponse>("/api/v1/match-queries", payload),
};
