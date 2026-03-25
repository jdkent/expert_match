import { v5 as uuidv5 } from "uuid";

export type CanonicalSlot = {
  slot_id: string;
  local_date: string;
  local_start_time: string;
};
const UUID_NAMESPACE_URL = "6ba7b811-9dad-11d1-80b4-00c04fd430c8";

export function buildCanonicalSlots(): CanonicalSlot[] {
  const slots: CanonicalSlot[] = [];
  const dates = ["2026-06-14", "2026-06-15", "2026-06-16", "2026-06-17", "2026-06-18"];
  for (const day of dates) {
    for (let hour = 8; hour < 17; hour += 1) {
      for (let minute = 0; minute < 60; minute += 15) {
        if (hour === 16 && minute > 45) {
          continue;
        }
        const hh = String(hour).padStart(2, "0");
        const mm = String(minute).padStart(2, "0");
        const key = `${day}T${hh}:${mm}:00`;
        slots.push({
          slot_id: uuidv5(`expert-match:${key}`, UUID_NAMESPACE_URL),
          local_date: day,
          local_start_time: `${hh}:${mm}:00`,
        });
      }
    }
  }
  return slots;
}

export const canonicalSlots = buildCanonicalSlots();
