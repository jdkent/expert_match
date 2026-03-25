import { api } from "./api";

export type OutreachRecipient = {
  expert_id: string;
  availability_slot_ids: string[];
};

export type OutreachRequestPayload = {
  match_query_id: string;
  primary_expert_id: string;
  requester: {
    full_name: string;
    email: string;
    organization?: string;
  };
  recipients: OutreachRecipient[];
  message_body: string;
};

export const outreachApi = {
  createOutreach: (payload: OutreachRequestPayload) =>
    api.post<{ outreach_request_id: string; overall_status: string; message_subject: string }>(
      "/api/v1/outreach-requests",
      payload,
    ),
};
