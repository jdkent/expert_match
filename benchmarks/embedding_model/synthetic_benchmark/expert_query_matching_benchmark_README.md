# Expert Query Matching Benchmark

Synthetic benchmark for matching a user query to an expert's stated area of expertise.

## Size
- Total examples: 100
- Positive examples: 50
- Negative examples: 50

## Domains
- computer_science
- statistics
- biology
- neuroscience

## Fields
- `id`: unique example id
- `query`: user query text
- `expert_text`: expert expertise text
- `label`: `1` for match, `0` for non-match
- `domain_pairing`: `within_domain` or `cross_domain_hard_negative`
- `query_domain`: domain implied by the query
- `expert_domain`: domain implied by the expert text
- `query_type`: one of `single_word`, `short_phrase`, `full_question`, `multi_sentence_question`
- `expert_text_type`: one of `single_word`, `short_phrase`, `abstract_sentence`, `long_sentence`
- `split`: simple suggested split field (`train`/`test`)

## Hugging Face loading example

```python
from datasets import load_dataset

dataset = load_dataset("json", data_files="expert_query_matching_benchmark.jsonl")["train"]
print(dataset[0])
```

## Notes
This is a **synthetic** benchmark intended for retrieval and reranking experiments.
It includes deliberately hard negatives from adjacent scientific areas.
