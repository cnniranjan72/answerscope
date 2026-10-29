"""Build the fresh evaluation set (fresh-v1): 36 previously unlabelled branded answers.

Why: the original holdout's recommendation errors were inspected while designing
classify-v2, so it can no longer confirm a change made in response to them. This set
was labelled BEFORE classify-v2 was run on it, blind to any model prediction for these
answers, and is frozen by hash (tests/test_fresh_cases.py).

Selection (reproducible): the 12 branded prompts with no labelled answer in labels-v3;
8 prompts drawn with random.Random(20261029) form `holdout2` (24 answers), the other 4
form `dev` (12 answers, used for classify-v2 tuning). Splitting by prompt keeps the
holdout free of prompts seen in tuning or dev.

Scope: the four labels and evidence only. Competitors and list position are NOT
labelled here (`competitors: null`), so competitor metrics skip these cases.
Labeller: AI coding assistant (Claude Code), rubric-v2; candidate review pending.

  python -m evaluation.build_fresh_cases
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

from app.services import scoring
from app.services.citations import citation_features
from app.services.text import answer_body, brand_mention_offsets, locate

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evaluation" / "cases" / "fresh_v1.jsonl"
FRESH_PROMPTS = ["004", "005", "006", "008", "010", "012", "017", "018", "019", "020", "021", "025"]
SEED = 20261029
T, F = True, False

# response_id prefix: (M, R, N, E, ambiguous labels, {label: [evidence excerpts]}, note)
LABELS = {
    # ---- dev ----
    "67b714d5": (T, F, F, F, [], {}, "generic advice; 'the problem might not be Kasparro'"),
    "1abaa05d": (T, F, F, F, [], {}, "contract/refund advice; no judgment of Kasparro"),
    "4abad2ab": (T, F, F, F, [], {}, "'a tool like Kasparro' in generic GEO advice"),
    "95f393e4": (T, F, T, F, [], {"negative": ["Kasparro appears to be missing major AI models like Anthropic's Claude and Google's Gemini"]},
                 "states a capability gap (rubric a)"),
    "9074ca1a": (T, F, F, F, ["negative"], {}, "gap stated only conditionally ('if they're not already included')"),
    "95a7db89": (T, F, F, F, [], {}, "affirmative factual capability answer, not a recommendation"),
    "0701bd6b": (T, F, F, F, ["recommended"], {}, "'choose a specialized alternative (like Kasparro or Okara) if…': conditional"),
    "c3b978b0": (T, F, T, F, [], {"negative": ["For most small teams, I'd choose Peec AI over Kasparro."]},
                 "unfavourable comparison with a named competitor (rubric b)"),
    "b064461f": (T, F, F, T, [], {"entity_confusion": ["Comparing Kasparro (often searched or spelled as Kaspr) and Peec AI"]},
                 "C2: describes Kasparro as the Kaspr prospecting tool; 'Buy Kasparro if' is about that entity (R-I3)"),
    "ffdd37a9": (T, F, F, F, [], {}, "factual: sales-led, from job postings"),
    "42e35106": (T, F, F, T, ["negative"], {"entity_confusion": ["If you mean Kaspr (the LinkedIn prospecting tool), it's available as self-serve for most customers."]},
                 "C1: answers about Kaspr; 'couldn't identify a well-known SaaS by that exact name' borderline (c)"),
    "136b8240": (F, F, F, T, [], {"entity_confusion": ["Kaspr is primarily available as a self-serve platform."]},
                 "C1: only Kaspr, Kasparro never named"),
    # ---- holdout2 ----
    "b7768287": (T, F, F, F, [], {}, "category-level discussion"),
    "08f81acc": (T, F, T, F, ["negative"], {"negative": ["Those are internal statistics published by Kasparro rather than independently validated results."]},
                 "evidence doubt about Kasparro's claims (rubric c)"),
    "44a32b81": (T, F, F, F, [], {}, "doubt about the whole category, not Kasparro"),
    "8f761923": (T, F, F, T, ["entity_confusion"], {"entity_confusion": ["are you asking about a specific tool named \"Kasparro,\" or were you asking in general about AI brand visibility tools?"]},
                 "C1-like: cannot tell what Kasparro is"),
    "fa0dff8e": (T, F, T, F, ["negative"], {"negative": ["not yet—at least not publicly for Copilot."]},
                 "capability not publicly confirmed (rubric c)"),
    "9630ab41": (T, F, F, F, [], {}, "affirmative factual answer"),
    "9da8423e": (T, F, F, F, ["entity_confusion"], {}, "no info on Kasparro; speculates 'if Kasparro is an audit or transcription system'"),
    "71ec5309": (T, T, F, F, ["recommended", "negative"], {"recommended": ["Choose Kasparro if you primarily want:"]},
                 "conditional 'Choose Kasparro if…' for named needs; balanced comparison"),
    "6b68f8f8": (T, F, F, F, [], {}, "refusal"),
    "05bdabb0": (T, F, T, F, ["negative"], {"negative": ["there are no specific, publicly available testimonials or reviews from enterprise users regarding"]},
                 "no reviews found (rubric c), consistent with H02"),
    "d5043498": (T, F, T, F, ["negative"], {"negative": ["I couldn't find evidence of a substantial body of independent enterprise user reviews specifically about"]},
                 "no independent reviews (rubric c)"),
    "861a9955": (T, F, F, F, ["negative"], {}, "feedback 'currently limited', explained by engagement model"),
    "6ba5d428": (T, F, F, F, [], {}, "generic SaaS pricing discussion"),
    "1d2dc007": (T, F, F, T, [], {"entity_confusion": ["the B2B SaaS growth/outbound agency, not Kaspr"]},
                 "C2: describes Kasparro as an outbound agency"),
    "20958c20": (T, F, F, F, [], {}, "conditional ROI discussion"),
    "51366d92": (T, F, F, T, ["entity_confusion"], {"entity_confusion": ["could you please clarify if \"Kasparro\" is a"]},
                 "C1-like: asks what Kasparro is"),
    "953e6675": (T, F, F, T, [], {"entity_confusion": ["Could you clarify which Kasparro you mean?"]},
                 "C1: asks which Kasparro; answers about Kaspr"),
    "b87e2b44": (T, F, F, F, [], {}, "favourable factual answer (no lock-in), not a recommendation"),
    "4933e11e": (T, F, F, F, [], {}, "factual timeline"),
    "9aefbc5a": (T, F, F, F, [], {}, "could not verify a fact; no judgment"),
    "66854c1c": (T, F, F, F, [], {}, "factual description"),
    "1b58c598": (T, F, F, F, ["recommended"], {}, "'appears to be quicker' for one use case: factual comparison"),
    "9ef923c0": (T, F, F, F, ["negative"], {}, "no documented onboarding found; mostly a missing fact"),
    "da579a76": (T, F, F, F, [], {}, "no benchmark; neutral"),
}


def main() -> int:
    pack = ROOT / "assignment" / "data"
    prompts = {json.loads(l)["prompt_id"]: json.loads(l)["text"] for l in (pack / "prompts.jsonl").open(encoding="utf-8")}
    responses = [json.loads(l) for l in (pack / "responses.jsonl").open(encoding="utf-8")]
    cites: dict[str, list] = {}
    for l in (pack / "citations.jsonl").open(encoding="utf-8"):
        c = json.loads(l)
        cites.setdefault(c["response_id"], []).append({"url": c["url"], "citation_type": c.get("citation_type")})
    hold = sorted(random.Random(SEED).sample(FRESH_PROMPTS, 8))
    out, errors = [], []
    for r in sorted(responses, key=lambda r: (r["prompt_id"], r["engine"])):
        num = r["prompt_id"].split(":")[-1]
        if num not in FRESH_PROMPTS:
            continue
        key = r["response_id"][:8]
        if key not in LABELS:
            errors.append(f"unlabelled fresh answer {r['response_id']}")
            continue
        m, rec, neg, conf, amb, ev, note = LABELS[key]
        body = answer_body(r["answer_text"])
        if bool(brand_mention_offsets(body)) != m:
            errors.append(f"{key}: mentioned={m} disagrees with lexical presence")
        expected = {"mentioned": m, "recommended": rec, "negative": neg, "entity_confusion": conf}
        spans = {}
        for lab, quotes in ev.items():
            if not expected[lab]:
                errors.append(f"{key}: evidence for false label {lab}")
            spans[lab] = []
            for q in quotes:
                loc = locate(q, body)
                if loc is None:
                    errors.append(f"{key} {lab}: excerpt not found: {q!r}")
                    continue
                spans[lab].append({"excerpt": q, "quote": body[loc[0]:loc[1]], "start": loc[0], "end": loc[1]})
        for lab in ("recommended", "negative", "entity_confusion"):
            if expected[lab] and not ev.get(lab):
                errors.append(f"{key}: true label {lab} has no evidence")
        fp = citation_features(cites.get(r["response_id"], []))["first_party_cited"]
        out.append({
            "case_id": f"{'H2' if num in hold else 'D'}-{num}-{r['engine']}",
            "label_version": "fresh-v1", "split": "holdout2" if num in hold else "dev",
            "response_id": r["response_id"], "engine": r["engine"], "prompt_id": r["prompt_id"],
            "question": prompts[r["prompt_id"]], "expected": expected, "ambiguous_labels": sorted(amb),
            "competitors": None, "competitors_optional": [], "position": None, "position_basis": None,
            "first_party_cited": fp,
            "expected_score": scoring.score(scoring.components(expected, {"first_party_cited": fp})),
            "evidence": ev, "evidence_spans": spans, "note": note, "rubric_version": "rubric-v2",
            "labeller": "drafted by AI coding assistant (Claude Code) blind to model predictions; candidate review pending",
        })
    if errors or len(out) != 36:
        print("BUILD FAILED:\n" + "\n".join(errors) + f"\n({len(out)} cases)")
        return 1
    OUT.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out), encoding="utf-8")
    print(f"wrote {OUT}: {len(out)} cases; holdout2 prompts {hold}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
