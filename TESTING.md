# Testing

```bash
python -m pytest -q
```

Engineering tests run on a **synthetic** fixture pack (`tests/fixtures/mini_pack`, 2 prompts, 6 answers, 7 citations, clearly marked) with the deterministic **stub** provider and fresh temporary SQLite databases. They prove mechanics: validation, permissions, state transitions, failure handling, arithmetic. They say nothing about model quality, which is measured separately in [EVALUATION.md](EVALUATION.md). The F4 property test also runs over all 150 real answers when `assignment/` is present.

## Required checks → tests

| Required by the brief | Test(s) |
|---|---|
| Invalid input | `test_invalid_records_rejected_with_reasons_valid_ones_kept` (bad engine, blank answer, missing field, orphan reference; valid record kept), `test_malformed_request_body_is_422`, `test_unknown_top_level_field_rejected` |
| Duplicate response handling | `test_duplicate_import_reused_not_duplicated`, `test_duplicate_within_one_batch`, `test_same_id_different_content_is_conflict_and_original_kept` |
| Model timeout or malformed result | `test_failures_are_explicit_and_bounded[permanent_timeout / malformed / empty / ungrounded]`, `test_transient_timeout_recovers_on_third_attempt`, `test_failed_analysis_is_not_a_zero_score` |
| Incorrect reviewer role | `test_wrong_role_denied`, `test_caller_supplied_identity_is_not_authorisation`, `test_unauthenticated`, `test_reviewer_cannot_import` |
| Rejection blocks export | `test_rejection_blocks_export` |
| Edit after approval | `test_edit_after_approval_requires_new_review`, `test_editing_submitted_version_supersedes_it` |
| End-to-end workflow | `test_end_to_end_import_analyse_edit_submit_approve_export` |
| Version immutability / integrity | `test_database_refuses_to_alter_frozen_version`, `test_tampered_approved_content_fails_export_integrity`, `test_decision_hash_must_match_reviewed_content`, `test_stale_base_version_rejected`, `test_double_submit_rejected` |
| Evidence traceability | `test_evidence_spans_point_at_source`, `test_fabricated_evidence_blocks_submission`, `test_remedy_must_follow_from_its_diagnostic`, `test_quote_not_in_answer_rejected` |
| Scoring invariants | `test_score_table`, `test_score_bounds_exhaustive`, `test_summary_denominators_exclude_failures` (the brief's 12/2/4-of-10 example), `test_empty_denominator_gives_none_not_zero`, `test_wilson_reference_values`, `test_paired_comparison_only_complete_prompts`, `test_citation_policy` |
| Fixture scenarios | transient/permanent timeout, empty, malformed, duplicate, wrong role, rejected review, review with no response (`test_no_silent_approval_without_reviewer`), change after approval |
| Regressions | `test_regression_f1…` to `test_regression_f5…` (see [evaluation/FAILURES.md](evaluation/FAILURES.md)) |
| Config safety | `test_unsafe_token_configuration_refused`, `test_identities_mapped_from_environment` |

## Latest result

See [claude-code/HANDOFF.md](claude-code/HANDOFF.md) for the most recent recorded run (command, count, date).
