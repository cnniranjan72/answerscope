# Repeated-run stability: classify-v1

Generated 2026-10-29T07:37:16+00:00 | 38 cases (final_seen, holdout2) | 1 live re-run(s) vs the recorded run | temperature 0, seed 7, `gemma4:12b`

| Label | Agree / compared | Rate | Wilson 95% |
|---|---|---|---|
| mentioned | 37/37 | 1.0 | [0.91, 1.0] |
| recommended | 36/37 | 0.973 | [0.86, 1.0] |
| negative | 37/37 | 1.0 | [0.91, 1.0] |
| entity_confusion | 37/37 | 1.0 | [0.91, 1.0] |

Status changes (recorded -> live): {'run1:failed->failed': 1}

Label flips: H2-018-aimode recommended False->True
