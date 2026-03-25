import { useMutation } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";

import { MatchResponse, matchingApi } from "../../services/matching";

type Props = {
  onMatches: (response: MatchResponse, queryText: string) => void;
  initialQueryText?: string;
  compact?: boolean;
};

export function MatchQueryForm({
  onMatches,
  initialQueryText = "",
  compact = false,
}: Props) {
  const [queryText, setQueryText] = useState(initialQueryText);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    setQueryText(initialQueryText);
  }, [initialQueryText]);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) {
      return;
    }

    textarea.style.overflowY = "hidden";

    if (queryText.trim().length === 0) {
      textarea.style.height = "44px";
      return;
    }

    textarea.style.height = "0px";
    const nextHeight = Math.min(textarea.scrollHeight, 88);
    textarea.style.height = `${Math.max(nextHeight, 44)}px`;
    textarea.style.overflowY = textarea.scrollHeight > 88 ? "auto" : "hidden";
  }, [queryText]);

  const mutation = useMutation({
    mutationFn: () =>
      matchingApi.createQuery({
        query_text: queryText.trim(),
      }),
    onSuccess: (data) => onMatches(data, queryText.trim()),
  });

  const submitSearch = () => {
    if (queryText.trim().length === 0 || mutation.isPending) {
      return;
    }
    mutation.mutate();
  };

  return (
    <div className={`search-shell ${compact ? "compact" : ""}`.trim()}>
      <div className="search-composer">
        <label className="search-field" htmlFor="match-query-input">
          <span className="sr-only">Your question</span>
          <textarea
            id="match-query-input"
            ref={textareaRef}
            aria-label="Your question"
            className="search-input"
            placeholder="Ask about the expertise you need."
            rows={1}
            value={queryText}
            onChange={(event) => setQueryText(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                submitSearch();
              }
            }}
          />
        </label>
        <button
          aria-label={compact ? "Update results" : "Find experts"}
          className="search-submit"
          disabled={queryText.trim().length === 0 || mutation.isPending}
          onClick={submitSearch}
        >
          <span aria-hidden="true">↑</span>
        </button>
      </div>
      {mutation.error ? <div className="token">{String(mutation.error)}</div> : null}
    </div>
  );
}
