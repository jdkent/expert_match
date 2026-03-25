import { useEffect, useMemo, useRef, useState } from "react";

export type AvailabilitySlot = {
  slot_id: string;
  local_date: string;
  local_start_time: string;
  is_available: boolean;
  attendee_request_count: number;
};

type Props = {
  slots: AvailabilitySlot[];
  selectedSlotIds?: string[];
  onSetSlotSelection?: (slotId: string, isSelected: boolean) => void;
};

function formatDayLabel(date: string) {
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${date}T00:00:00Z`));
}

function formatTimeLabel(time: string) {
  return time.slice(0, 5);
}

export function AvailabilityGrid({
  slots,
  selectedSlotIds = [],
  onSetSlotSelection,
}: Props) {
  const [isDragging, setIsDragging] = useState(false);
  const dragValueRef = useRef<boolean | null>(null);
  const visitedSlotIdsRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    if (!onSetSlotSelection) {
      return;
    }

    function stopDragging() {
      setIsDragging(false);
      dragValueRef.current = null;
      visitedSlotIdsRef.current.clear();
    }

    window.addEventListener("pointerup", stopDragging);
    return () => window.removeEventListener("pointerup", stopDragging);
  }, [onSetSlotSelection]);

  const selectedSlotIdSet = useMemo(() => new Set(selectedSlotIds), [selectedSlotIds]);

  const dates = useMemo(
    () =>
      Array.from(new Set(slots.map((slot) => slot.local_date))).sort((left, right) =>
        left.localeCompare(right),
      ),
    [slots],
  );

  const times = useMemo(
    () =>
      Array.from(new Set(slots.map((slot) => slot.local_start_time))).sort((left, right) =>
        left.localeCompare(right),
      ),
    [slots],
  );

  const slotLookup = useMemo(() => {
    const entries = new Map<string, AvailabilitySlot>();
    for (const slot of slots) {
      entries.set(`${slot.local_date}-${slot.local_start_time}`, slot);
    }
    return entries;
  }, [slots]);

  const selectedCount = selectedSlotIds.length;

  function applySlotSelection(slot: AvailabilitySlot) {
    if (!onSetSlotSelection || visitedSlotIdsRef.current.has(slot.slot_id)) {
      return;
    }
    visitedSlotIdsRef.current.add(slot.slot_id);
    onSetSlotSelection(slot.slot_id, dragValueRef.current ?? !selectedSlotIdSet.has(slot.slot_id));
  }

  function handlePointerDown(slot: AvailabilitySlot) {
    if (!onSetSlotSelection || !slot.is_available) {
      return;
    }
    const nextValue = !selectedSlotIdSet.has(slot.slot_id);
    dragValueRef.current = nextValue;
    visitedSlotIdsRef.current = new Set();
    setIsDragging(true);
    applySlotSelection(slot);
  }

  function handlePointerEnter(slot: AvailabilitySlot) {
    if (!isDragging || !onSetSlotSelection || !slot.is_available) {
      return;
    }
    applySlotSelection(slot);
  }

  if (slots.length === 0) {
    return <p className="muted">No preset availability is published for this expert.</p>;
  }

  return (
    <section className="availability-board stack">
      <div className="availability-board-header">
        <div>
          <h3>{onSetSlotSelection ? "Paint your availability" : "Availability calendar"}</h3>
          <p className="muted">
            {onSetSlotSelection
              ? "Click and drag across the timetable to add or remove 15-minute slots."
              : "Read the OHBM 2026 Bordeaux timetable by day and time."}
          </p>
        </div>
        <div className="chip-row">
          <span className="chip">
            {selectedCount} {selectedCount === 1 ? "slot selected" : "slots selected"}
          </span>
          {onSetSlotSelection ? <span className="chip">Drag to paint</span> : null}
        </div>
      </div>
      <div className="availability-scroll">
        <div
          className={`availability-table ${onSetSlotSelection ? "editable" : "readonly"}`.trim()}
        >
          <div className="availability-corner" />
          {dates.map((date) => (
            <div key={date} className="availability-day">
              {formatDayLabel(date)}
            </div>
          ))}
          {times.map((time) => (
            <FragmentRow
              key={time}
              time={time}
              dates={dates}
              slotLookup={slotLookup}
              selectedSlotIdSet={selectedSlotIdSet}
              onSetSlotSelection={onSetSlotSelection}
              onPointerDown={handlePointerDown}
              onPointerEnter={handlePointerEnter}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

type FragmentRowProps = {
  time: string;
  dates: string[];
  slotLookup: Map<string, AvailabilitySlot>;
  selectedSlotIdSet: Set<string>;
  onSetSlotSelection?: (slotId: string, isSelected: boolean) => void;
  onPointerDown: (slot: AvailabilitySlot) => void;
  onPointerEnter: (slot: AvailabilitySlot) => void;
};

function FragmentRow({
  time,
  dates,
  slotLookup,
  selectedSlotIdSet,
  onSetSlotSelection,
  onPointerDown,
  onPointerEnter,
}: FragmentRowProps) {
  return (
    <>
      <div className="availability-time">{formatTimeLabel(time)}</div>
      {dates.map((date) => {
        const slot = slotLookup.get(`${date}-${time}`);

        if (!slot) {
          return <div key={`${date}-${time}`} className="availability-cell empty" />;
        }

        const isSelected = selectedSlotIdSet.has(slot.slot_id);
        const className = [
          "availability-cell",
          slot.is_available ? "open" : "blocked",
          isSelected ? "selected" : "",
          onSetSlotSelection ? "interactive" : "",
        ]
          .filter(Boolean)
          .join(" ");

        const label = `${formatDayLabel(slot.local_date)} ${formatTimeLabel(slot.local_start_time)}`;

        return onSetSlotSelection ? (
          <button
            key={slot.slot_id}
            type="button"
            aria-label={label}
            aria-pressed={isSelected}
            className={className}
            disabled={!slot.is_available}
            onPointerDown={() => onPointerDown(slot)}
            onPointerEnter={() => onPointerEnter(slot)}
          >
            <div className="availability-cell-label">
              <span className="availability-cell-time">{formatTimeLabel(slot.local_start_time)}</span>
            </div>
          </button>
        ) : (
          <div key={slot.slot_id} aria-label={label} className={className}>
            <div className="availability-cell-label">
              <span className="availability-cell-time">{formatTimeLabel(slot.local_start_time)}</span>
            </div>
          </div>
        );
      })}
    </>
  );
}
