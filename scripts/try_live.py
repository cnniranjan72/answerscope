"""Developer probe: classify given response IDs with the local model and print the outcome.
Used only on TUNING cases (see evaluation/cases); never on holdout cases."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.services.analyzer import analyse_response  # noqa: E402
from app.services.llm import OllamaProvider  # noqa: E402
from app.services.text import answer_body  # noqa: E402

pack = ROOT / "assignment" / "data"
prompts = {json.loads(l)["prompt_id"]: json.loads(l)["text"] for l in open(pack / "prompts.jsonl", encoding="utf-8")}
responses = {json.loads(l)["response_id"]: json.loads(l) for l in open(pack / "responses.jsonl", encoding="utf-8")}
prov = OllamaProvider("http://localhost:11434", "gemma4:12b", 300, 1200)
for rid in sys.argv[1:]:
    r = responses[rid]
    out = analyse_response(prov, response_id=rid, question=prompts[r["prompt_id"]],
                           body=answer_body(r["answer_text"]), max_attempts=3)
    print("=" * 80, "\n", rid, r["prompt_id"], r["engine"], out.status, out.reason)
    for a in out.attempts:
        print("  attempt", a.attempt, a.outcome, a.latency_ms, "ms", (a.error or "")[:300])
    if out.labels:
        L = out.labels
        print("  labels", L["labels"], "pos", L["position"], L["position_basis"])
        for k, v in L["evidence"].items():
            for s in v:
                print("   ", k, "|", s["quote"][:160])
        print("   competitors", [c["name"] for c in L["competitors"]])
        print("   rationale", L["rationale"][:300])
    sys.stdout.flush()
