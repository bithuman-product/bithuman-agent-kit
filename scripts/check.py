#!/usr/bin/env python3
"""Local gate for the bitHuman agent kit (no CI). Exit 1 on any error.

Checks: every JSON/TOML/YAML file parses; SKILL.md front matter; manifest paths exist;
no secret-looking strings; optional claims scan against the marketing truth register
(forbidden and owner-review patterns) with --claims PATH.
"""
import argparse, json, pathlib, re, sys, tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {".git"}
TEXT = {".md", ".json", ".toml", ".yaml", ".yml", ".py", ".txt"}
SECRET_PATTERNS = [
    r"(?i)BITHUMAN_(?:API|MASTER)_SECRET\s*=\s*['\"]?[A-Za-z0-9_\-]{12,}",
    r"(?i)api[-_]secret['\"]?\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}",
    r"\bsk-[A-Za-z0-9]{20,}", r"\bek_[A-Za-z0-9]{12,}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
]


def files():
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and not SKIP.intersection(p.relative_to(ROOT).parts):
            yield p


def parse_all(errors, counts):
    for p in files():
        rel = p.relative_to(ROOT)
        try:
            if p.suffix == ".json":
                json.loads(p.read_text()); counts["json"] += 1
            elif p.suffix == ".toml":
                tomllib.loads(p.read_text()); counts["toml"] += 1
            elif p.suffix in (".yaml", ".yml"):
                import yaml
                yaml.safe_load(p.read_text()); counts["yaml"] += 1
        except Exception as e:  # noqa: BLE001
            errors.append(f"{rel}: does not parse: {e}")


def front_matter(path):
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip()
    return out


def check_skills(errors, counts):
    for skill in sorted((ROOT / "skills").glob("*/SKILL.md")):
        counts["skills"] += 1
        fm = front_matter(skill)
        rel = skill.relative_to(ROOT)
        if fm is None:
            errors.append(f"{rel}: no YAML front matter"); continue
        if fm.get("name") != skill.parent.name:
            errors.append(f"{rel}: name {fm.get('name')!r} != folder {skill.parent.name!r}")
        if not 20 <= len(fm.get("description", "")) <= 1024:
            errors.append(f"{rel}: description missing or longer than 1024 chars")
    if not counts["skills"]:
        errors.append("skills/: no SKILL.md found")


def check_manifests(errors, counts):
    refs = []
    plug = json.loads((ROOT / "plugin.json").read_text())
    refs += [plug["mcp"], plug["onboardingSkill"], *plug["skills"]]
    refs += [plug["interface"][k] for k in ("icon", "logo") if k in plug["interface"]]
    lim = {"displayName": 30, "shortDescription": 30, "longDescription": 4000, "developerName": 80}
    for k, n in lim.items():
        if len(plug["interface"].get(k, "")) > n:
            errors.append(f"plugin.json: interface.{k} over {n} chars")
    cc = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    refs += [cc["skills"], cc["mcpServers"]]
    for r in refs:
        counts["refs"] += 1
        if not (ROOT / r).exists():
            errors.append(f"manifest path missing: {r}")
    url = "https://docs.bithuman.ai/docs-mcp"
    for p in [ROOT / "mcp.json", ROOT / ".mcp.json", *(ROOT / "examples/mcp").glob("*.json")]:
        try:
            d = json.loads(p.read_text())
        except ValueError:
            continue  # already reported by parse_all
        servers = d.get("mcpServers") or d.get("servers") or {}
        if servers.get("bithuman-docs", {}).get("url") != url:
            errors.append(f"{p.relative_to(ROOT)}: bithuman-docs url is not {url}")


def text_files():
    for p in files():
        if p.suffix in TEXT and p.name != "check.py":
            yield p, p.read_text()


def check_secrets(errors, counts):
    for p, text in text_files():
        counts["secret_scanned"] += 1
        for pat in SECRET_PATTERNS:
            if re.search(pat, text):
                errors.append(f"{p.relative_to(ROOT)}: secret-looking string ({pat})")


def check_claims(errors, counts, register):
    import yaml
    reg = yaml.safe_load(pathlib.Path(register).read_text())
    rules = [(c["id"], c["status"], pat) for c in reg["claims"]
             if c.get("status") in ("forbidden", "owner-review") for pat in c.get("patterns") or []]
    counts["claim_patterns"] = len(rules)
    for p, text in text_files():
        counts["claims_scanned"] += 1
        for cid, status, pat in rules:
            for m in re.finditer(pat, text, re.IGNORECASE):
                line = text.count("\n", 0, m.start()) + 1
                errors.append(f"{p.relative_to(ROOT)}:{line}: {status} claim {cid}: {m.group(0)!r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--claims", help="path to claims/truth-register.yaml")
    a = ap.parse_args()
    errors, counts = [], {k: 0 for k in ("json", "toml", "yaml", "skills", "refs",
                                          "secret_scanned", "claims_scanned")}
    parse_all(errors, counts)
    check_skills(errors, counts)
    check_manifests(errors, counts)
    check_secrets(errors, counts)
    if a.claims:
        check_claims(errors, counts, a.claims)
    print(" ".join(f"{k}={v}" for k, v in counts.items()))
    for e in errors:
        print("ERROR", e)
    print("FAIL" if errors else "PASS", f"({len(errors)} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
