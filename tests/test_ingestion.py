"""Required: invalid input validation; duplicate response handling."""
import json

from tests.conftest import A, MINI_PACK, R


def _lines(name):
    return [json.loads(l) for l in (MINI_PACK / "data" / f"{name}.jsonl").read_text(encoding="utf-8").splitlines()]


def test_pack_import_counts(client):
    r = client.post("/datasets/pack", headers=A)
    assert r.status_code == 201
    c = r.json()["counts"]
    assert c["prompts"]["inserted"] == 2 and c["responses"]["inserted"] == 6 and c["citations"]["inserted"] == 7


def test_invalid_records_rejected_with_reasons_valid_ones_kept(client, conn):
    prompts = _lines("prompts")
    good = _lines("responses")[0]
    bad_engine = {**good, "response_id": "x1", "engine": "bing"}
    blank_answer = {**good, "response_id": "x2", "answer_text": "   "}
    missing = {k: v for k, v in good.items() if k != "capture_status"} | {"response_id": "x3"}
    orphan = {**good, "response_id": "x4", "prompt_id": "no-such-prompt"}
    r = client.post("/datasets", headers=A, json={"prompts": prompts,
                                                  "responses": [good, bad_engine, blank_answer, missing, orphan]})
    assert r.status_code == 201
    body = r.json()
    assert body["counts"]["responses"] == {"submitted": 5, "inserted": 1, "reused": 0, "rejected": 4}
    reasons = {x["id"]: x["reason"] for x in body["rejections"]}
    assert "engine" in reasons["x1"]
    assert "blank" in reasons["x2"]
    assert "capture_status" in reasons["x3"]
    assert "unknown prompt_id" in reasons["x4"]
    assert conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0] == 1
    # the ledger is queryable later
    d = client.get(f"/datasets/{body['dataset_id']}", headers=A).json()
    assert len(d["rejections"]) == 4


def test_malformed_request_body_is_422(client):
    r = client.post("/datasets", headers=A, json={"responses": "not-a-list"})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "request_validation_failed"


def test_unknown_top_level_field_rejected(client):
    r = client.post("/datasets", headers=A, json={"prompts": [], "actor": "reviewer"})
    assert r.status_code == 422


def test_duplicate_import_reused_not_duplicated(client, conn):
    client.post("/datasets/pack", headers=A)
    r = client.post("/datasets/pack", headers=A)
    c = r.json()["counts"]
    assert c["responses"] == {"submitted": 6, "inserted": 0, "reused": 6, "rejected": 0}
    assert c["citations"]["reused"] == 7
    assert conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0] == 6
    assert conn.execute("SELECT COUNT(*) FROM citations").fetchone()[0] == 7


def test_same_id_different_content_is_conflict_and_original_kept(client, conn):
    client.post("/datasets/pack", headers=A)
    altered = {**_lines("responses")[0], "answer_text": "Tampered answer naming Kasparro."}
    r = client.post("/datasets", headers=A, json={"responses": [altered]})
    assert r.json()["counts"]["responses"]["rejected"] == 1
    assert "conflict" in r.json()["rejections"][0]["reason"]
    stored = conn.execute("SELECT answer_text FROM responses WHERE response_id = 'syn-r1'").fetchone()[0]
    assert "Tampered" not in stored


def test_duplicate_within_one_batch(client, conn):
    prompts = _lines("prompts")
    resp = _lines("responses")[0]
    r = client.post("/datasets", headers=A, json={"prompts": prompts, "responses": [resp, resp]})
    assert r.json()["counts"]["responses"] == {"submitted": 2, "inserted": 1, "reused": 1, "rejected": 0}
    assert conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0] == 1


def test_reviewer_cannot_import(client):
    assert client.post("/datasets/pack", headers=R).status_code == 403
