import { api } from "./api";

export type ExpertProfilePayload = {
  full_name: string;
  email: string;
  short_bio?: string | null;
  orcid_id?: string | null;
  website_url?: string | null;
  x_handle?: string | null;
  linkedin_identifier?: string | null;
  bluesky_identifier?: string | null;
  github_handle?: string | null;
  expertise_entries: string[];
  available_slot_ids?: string[];
};

export type EditableExpertProfile = {
  expert_id: string;
  full_name: string;
  email: string;
  short_bio?: string | null;
  orcid_id?: string | null;
  website_url?: string | null;
  x_handle?: string | null;
  linkedin_identifier?: string | null;
  bluesky_identifier?: string | null;
  github_handle?: string | null;
  expertise_entries: string[];
  availability_slots: Array<{
    slot_id: string;
    local_date: string;
    local_start_time: string;
    is_available: boolean;
    attendee_request_count: number;
  }>;
};

export const expertProfilesApi = {
  createProfile: (payload: ExpertProfilePayload) =>
    api.post<{ profile_id: string; access_key: string }>("/api/v1/experts", payload),
  getProfileForAccessKey: (access_key: string) =>
    api.post<EditableExpertProfile>("/api/v1/expert-access/profile", { access_key }),
  updateProfile: (access_key: string, payload: Partial<ExpertProfilePayload>) =>
    api.patch("/api/v1/expert-access/profile", { access_key, ...payload }),
  deleteProfile: (access_key: string, email_confirmation: string) =>
    api.delete("/api/v1/expert-access/profile", { access_key, email_confirmation }),
  getAvailability: (expertId: string) =>
    api.get<EditableExpertProfile["availability_slots"]>(`/api/v1/experts/${expertId}/availability`),
};
