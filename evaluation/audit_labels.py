"""Label audit (rubric-v2): reads labels_v1.jsonl (unchanged), applies the documented
proposed changes, computes exact raw evidence spans, recomputes first-party citation and
expected scores with the production code, and writes:

  evaluation/cases/labels_v2_proposed.jsonl   proposed revision (NOT used by default)
  evaluation/results/label_audit_table.md     generated per-case review table

  python -m evaluation.audit_labels

Exits non-zero if any evidence excerpt does not map to the source or any expected score
disagrees with vis-v1. All judgments below were drafted by the AI coding assistant and
await candidate adjudication; nothing here is independent human ground truth.
"""
from __future__ import annotations

import copy
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services import scoring  # noqa: E402
from app.services.citations import citation_features  # noqa: E402
from app.services.text import answer_body, brand_mention_offsets, locate  # noqa: E402

V1 = ROOT / "evaluation" / "cases" / "labels_v1.jsonl"
V2 = ROOT / "evaluation" / "cases" / "labels_v2_proposed.jsonl"
TABLE = ROOT / "evaluation" / "results" / "label_audit_table.md"
LABELS = ["mentioned", "recommended", "negative", "entity_confusion"]

# Answers whose text influenced classify-v1 wording during data inspection (Stage A printed
# the first Kasparro sentence of every branded answer before the prompt was written).
DESIGN_EXPOSURE = {
    "H01": "prompt example 'coding assistant' taken from this answer -> entity_confusion not independent",
    "H04": "Kaspr substitution pattern (seen in this and other answers) is a prompt example -> entity_confusion not independent",
}
BRANDED_FIRST_SENTENCE_SEEN = "first Kasparro sentence was printed during inspection before prompt design"

# Per-case audit judgments. 'changes' are proposed label edits; 'adjudicate' names the
# open question for the candidate. 'intended' = does the cited excerpt refer to the
# intended Kasparro (kasparro.com AI-visibility provider)?
AUDIT = {
    "T01": dict(intended="yes", neg_type="explicit (c): 'not a widely recognized, top-tier agency or tool'",
                rec="none", confidence="high", rationale="Direct unfavourable recognition judgment about Kasparro."),
    "T02": dict(intended="yes", neg_type="none", rec="'Kasparro is designed specifically for this use case' (asker's need)",
                confidence="high", rationale="Clear suitability for the stated need."),
    "T03": dict(intended="no (answers about Kaspr)", neg_type="n/a: criticism is of Kaspr (R-I2)", rec="none",
                confidence="high", rationale="C1 substitution; Kaspr's competitors excluded from competitors."),
    "T04": dict(intended="n/a (absent)", neg_type="none", rec="none", confidence="high",
                rationale="Unbranded list; competitors are the named tools."),
    "T05": dict(intended="yes", neg_type="comparative (b): 'I would lean toward Profound over Kasparro'",
                rec="none: 'For retail/e-commerce brands: Kasparro makes more sense' is suitability for a different audience",
                confidence="high", rationale="Excerpt omits '**' markers; now stored as exact raw span with offsets."),
    "H01": dict(intended="no: 'Kasparro (an AI coding assistant)' (C2)",
                neg_type="risk statement concerns the misidentified coding assistant -> not negative under R-I2",
                rec="none", confidence="medium",
                changes={"negative": False}, adjudicate="D-CONF-NEG",
                rationale="Under R-I2 the harm is counted once as entity_confusion; score 0 -> 20."),
    "H02": dict(intended="yes (AI visibility platform described)",
                neg_type="evidence gap framed as caution (c): 'Reasons to be cautious… very few independent reviews'",
                rec="none: 'I wouldn't label Kasparro as illegitimate' is not suitability", confidence="medium",
                ambiguous_add=["negative"], adjudicate="D-NEG",
                rationale="Kept true per classify-v1 definition; marked ambiguous because it rests only on (c)."),
    "H03": dict(intended="yes (named as a competitor of AthenaHQ)",
                neg_type="visibility gap + comparative (b/c): 'no data available… suggesting AthenaHQ is the more established'",
                rec="none", confidence="medium", ambiguous_add=["negative"], adjudicate="D-NEG",
                rationale="Comparative conclusion against Kasparro for 'who is more trustworthy'; borderline with pure low visibility."),
    "H04": dict(intended="no (answers about Kaspr cancellation)", neg_type="n/a (R-I2)", rec="none",
                confidence="high", rationale="C1 substitution."),
    "H05": dict(intended="yes", neg_type="none", rec="favourable description only; no suitability for a need",
                confidence="medium", rationale="Recommended stays false; already ambiguous."),
    "H06": dict(intended="disputed: price/description attributed to Kasparro but cited to revenuepulseai.com",
                neg_type="none", rec="none ('with Kasparro's help afterward' is not endorsement)", confidence="medium",
                changes={"entity_confusion": True}, adjudicate="D-MISATTR",
                rationale=("C3: both claims carry only an inline link to revenuepulseai.com (no kasparro.com citation); "
                           "the same prompt's AI Mode answer citing kasparro.com describes a different scope "
                           "(five surfaces, top 500 SKUs; price not listed) and the brief describes a catalog focus. "
                           "No pack evidence links RevenuePulse to Kasparro. revenuepulseai.com was NOT opened."),
                extra_evidence={"entity_confusion": ["Kasparro's 14-day AI Revenue Diagnostic starts at ₹49,999"]}),
    "H07": dict(intended="yes", neg_type="comparative (b): 'not yet as visibly global or internationally proven as Profound'",
                rec="none: capability 'yes' is not suitability over alternatives (ambiguous)", confidence="medium-high",
                rationale="Comparative positioning for the asker's need."),
    "H08": dict(intended="n/a (absent)", neg_type="none", rec="none", confidence="high",
                rationale="Unbranded list."),
    "H09": dict(intended="n/a (absent)", neg_type="none", rec="none", confidence="high",
                optional_add=["siftly.ai", "trussed.ai"],
                rationale="siftly.ai / trussed.ai appear only as citation link labels -> optional."),
    "H10": dict(intended="yes", neg_type="none", rec="sign-up availability + link only", confidence="medium",
                rationale="Recommended stays false; already ambiguous."),
    "H11": dict(intended="yes", neg_type="none", rec="neutral description", confidence="high",
                rationale="First-party cited (computed)."),
    "H12": dict(intended="yes", neg_type="none", rec="'can help an enterprise software brand increase its visibility'",
                confidence="high", rationale="Suitability for the asker's need."),
    "S01": dict(intended="synthetic", neg_type="none", rec="'a good choice for D2C catalogs'; ranked #2",
                confidence="high", rationale="Tests ranked-list position extraction and recommendation."),
    "S02": dict(intended="synthetic", neg_type="explicit evidence doubt (c)", rec="none; injected instruction must be ignored",
                confidence="high", rationale="Tests resistance to instructions embedded in untrusted answer text."),
}


def span_cell(spans: dict) -> str:
    cells = []
    for lab, items in spans.items():
        for s in items:
            quote = s["quote"].replace("|", "¦").replace("\n", " ")[:140]
            cells.append(f"{lab}: {quote} [{s['start']}:{s['end']}]")
    return "<br>".join(cells) or "-"


def load_pack():
    data = ROOT / "assignment" / "data"
    responses = {json.loads(l)["response_id"]: json.loads(l)
                 for l in (data / "responses.jsonl").read_text(encoding="utf-8").splitlines()}
    prompts = {json.loads(l)["prompt_id"]: json.loads(l)["text"]
               for l in (data / "prompts.jsonl").read_text(encoding="utf-8").splitlines()}
    cites = defaultdict(list)
    for l in (data / "citations.jsonl").read_text(encoding="utf-8").splitlines():
        c = json.loads(l)
        cites[c["response_id"]].append(c)
    return responses, prompts, cites


def main() -> int:
    responses, prompts, cites = load_pack()
    v1 = [json.loads(l) for l in V1.read_text(encoding="utf-8").splitlines() if l.strip()]
    errors, rows, out = [], [], []
    for c in v1:
        a = AUDIT[c["case_id"]]
        new = copy.deepcopy(c)
        new["label_version"] = "labels-v2-proposed"
        new["rubric_version"] = "rubric-v2"
        changes = a.get("changes", {})
        for lab, val in changes.items():
            new["expected"][lab] = val
            if not val:
                new["evidence"].pop(lab, None)
        for lab, quotes in a.get("extra_evidence", {}).items():
            new["evidence"].setdefault(lab, []).extend(quotes)
        new["ambiguous_labels"] = sorted(set(c["ambiguous_labels"]) | set(a.get("ambiguous_add", [])))
        new["competitors_optional"] = c["competitors_optional"] + a.get("optional_add", [])

        if c.get("synthetic"):
            body, question, fp = c["answer_text"], c["question"], False
        else:
            r = responses[c["response_id"]]
            body, question = answer_body(r["answer_text"]), prompts[r["prompt_id"]]
            fp = citation_features(cites[c["response_id"]])["first_party_cited"]
            if fp != c["first_party_cited"]:
                errors.append(f"{c['case_id']}: first_party_cited {c['first_party_cited']} != computed {fp}")
            if bool(brand_mention_offsets(body)) != new["expected"]["mentioned"]:
                errors.append(f"{c['case_id']}: 'mentioned' disagrees with lexical presence")
        new["first_party_cited"] = fp

        spans = {}
        for lab, quotes in new["evidence"].items():
            if not new["expected"][lab]:
                errors.append(f"{c['case_id']}: evidence for false label {lab}")
            spans[lab] = []
            for q in quotes:
                loc = locate(q, body)
                if loc is None:
                    errors.append(f"{c['case_id']} {lab}: excerpt not found: {q!r}")
                    continue
                spans[lab].append({"excerpt": q, "quote": body[loc[0]:loc[1]], "start": loc[0], "end": loc[1]})
        new["evidence_spans"] = spans

        score = scoring.score(scoring.components(new["expected"], {"first_party_cited": fp}))
        new["expected_score"] = score
        if not changes and score != c["expected_score"]:
            errors.append(f"{c['case_id']}: v1 expected_score {c['expected_score']} != vis-v1 {score}")

        status = "needs_adjudication" if a.get("adjudicate") else "proposed_keep"
        new["review"] = {"status": status, "confidence": a["confidence"], "adjudication_question": a.get("adjudicate"),
                         "rationale": a["rationale"], "refers_to_intended_entity": a["intended"],
                         "design_exposure": DESIGN_EXPOSURE.get(c["case_id"])
                         or (BRANDED_FIRST_SENTENCE_SEEN if c["split"] == "holdout" and c["prompt_id"].split(":")[-1] <= "025"
                             and new["expected"]["mentioned"] else None),
                         "labeller": "AI coding assistant (Claude Code); candidate adjudication pending"}
        out.append(new)

        fmt = lambda e: "".join(k[0].upper() if e[k] else "·" for k in LABELS)  # noqa: E731
        rows.append(
            f"| {c['case_id']} | {c['split']} | {question[:60]} | {fmt(c['expected'])} → {fmt(new['expected'])} | "
            f"{c['expected_score']} → {score} | {a['intended']} | {a['rec']} | {a['neg_type']} | "
            f"{', '.join(new['competitors']) or '-'} | {'yes' if fp else 'no'} | {new['position'] or '-'} | "
            f"{span_cell(spans)} | "
            f"{a['confidence']} | {status} |")

    if errors:
        print("AUDIT FAILED:\n" + "\n".join(errors))
        return 1
    V2.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out), encoding="utf-8")
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    TABLE.write_text(
        "# Label audit table (generated by `python -m evaluation.audit_labels`)\n\n"
        "Labels column: M=mentioned, R=recommended, N=negative, E=entity_confusion, · = false; v1 → proposed v2. "
        "Scores use vis-v1. Spans are exact raw `answer_body[start:end]`. All judgments AI-drafted, pending candidate adjudication.\n\n"
        "| Case | Split | Prompt | Labels | Score | Refers to intended Kasparro? | Recommendation evidence | Negative vs evidence gap | "
        "Competitors | 1st-party cited | Position | Evidence spans [start:end] | Confidence | Status |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n", encoding="utf-8")
    changed = sum(1 for a, b in zip(v1, out) if a["expected"] != b["expected"])
    print(f"audit OK: {len(out)} cases, {changed} with proposed label changes, "
          f"{sum(1 for x in out if x['review']['status'] == 'needs_adjudication')} need adjudication")
    print(f"wrote {V2}\nwrote {TABLE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
