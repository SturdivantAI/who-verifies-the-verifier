"""Re-fetch logbook markdown for re-judgment, reusing the harness serialisation
verbatim (app.py @ dc9028d) but PINNING revision=sha.

The harness itself did not pin: read_logbook_markdown() called list_repo_files()
and hf_hub_download() at current HEAD. For a test-retest we must hold the input
constant, so we pin to the sha recorded in each verdict record and additionally
report whether HEAD has moved since.
"""
import json, os, re, sys
from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.utils import EntryNotFoundError, RepositoryNotFoundError, RevisionNotFoundError

MAX_LOGBOOK_CHARS = 120_000          # app.py:65
HF_TOKEN = os.environ.get("HF_TOKEN")  # not required for public spaces
api = HfApi(token=HF_TOKEN)


def _strip_figure_payloads(text: str) -> str:       # app.py, verbatim
    def repl(match):
        fence, info, body = match.group(1), match.group(2).strip(), match.group(3)
        lang = (info.split() or [""])[0].lower()
        if lang == "html":
            return f"[figure html omitted: {len(body)} chars]"
        if lang == "raw" and len(body) > 4000:
            return f"{fence}raw\n{body[:4000]}\n[... raw data truncated ...]\n{fence}"
        return match.group(0)
    return re.sub(r"(`{3,4}|~{3,4})([^\n]*)\n([\s\S]*?)\n\1", repl, text)


def read_logbook_markdown(space_id: str, revision: str | None = None) -> str:
    """app.py read_logbook_markdown with an added `revision` pin."""
    files = api.list_repo_files(space_id, repo_type="space", revision=revision)
    pages = sorted(f for f in files if f.startswith("pages/") and f.endswith(".md"))
    pages = [p for p in pages if p == "pages/index.md"] + [
        p for p in pages if p != "pages/index.md"
    ]
    parts, total = [], 0
    for page in pages:
        try:
            path = hf_hub_download(space_id, page, repo_type="space",
                                   revision=revision, token=HF_TOKEN)
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"  could not fetch {space_id}/{page}: {e!r}", file=sys.stderr)
            continue
        text = re.sub(r"<!-- trackio-cell\n[\s\S]*?\n-->", "", text)
        text = _strip_figure_payloads(text)
        block = f"\n\n===== FILE {page} =====\n{text}"
        remaining = MAX_LOGBOOK_CHARS - total
        if remaining <= 0:
            break
        if len(block) > remaining:
            block = block[:remaining] + "\n[... page truncated for length ...]"
        parts.append(block)
        total += len(block)
    return "".join(parts)


def head_sha(space_id):
    try:
        return api.space_info(space_id).sha
    except Exception:
        return None


if __name__ == "__main__":
    import csv
    rows = list(csv.DictReader(open(sys.argv[1])))
    out, meta = {}, []
    for i, r in enumerate(rows, 1):
        sid, sha = r["space_id"], r["sha"]
        rec = {"space_id": sid, "pinned_sha": sha, "orid": r["orid"], "arm": r["arm"]}
        try:
            h = head_sha(sid)
            rec["head_sha"] = h
            rec["head_moved"] = (h is not None and h != sha)
            md = read_logbook_markdown(sid, revision=sha)
            out[sid] = md
            rec.update(status="ok", chars=len(md),
                       truncated="[... page truncated for length ...]" in md)
        except (RepositoryNotFoundError, RevisionNotFoundError, EntryNotFoundError) as e:
            rec.update(status=type(e).__name__, chars=0)
        except Exception as e:
            rec.update(status=f"error:{type(e).__name__}", chars=0)
        meta.append(rec)
        print(f"[{i}/{len(rows)}] {sid} {rec['status']} {rec.get('chars',0)} chars", flush=True)
    json.dump(out, open(sys.argv[2], "w"))
    json.dump(meta, open(sys.argv[3], "w"), indent=1)
