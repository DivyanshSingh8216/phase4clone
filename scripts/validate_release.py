"""Validate the packaged release contract and immutable source workbook hashes."""
from pathlib import Path
import hashlib, sys
ROOT=Path(__file__).resolve().parents[1]
REPO=Path(r"C:\Users\KIIT0001\PulseIQ-Master-Integration")
def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()
def main():
    required=[ROOT/"api.py",ROOT/"explorer.py",ROOT/"build_report.py",ROOT/"board_pack"/"PulseIQ_Board_Pack_Phase4.pptx",
              ROOT/"docs"/"ACCEPTANCE_CHECKLIST.md",ROOT/"RELEASE_NOTES.md"]
    missing=[str(p) for p in required if not p.exists()]
    if missing: raise SystemExit("Missing required Phase 4 artifacts:\\n" + "\\n".join(missing))
    expected="49935362af5d65ca1a737946961fe4ea3b0708ee2677e7eb38a4eafa8cbb917e"
    for phase in ("phase-1","phase-2","phase-3"):
        source=REPO/phase/"data"/"PulseIQ_Dataset.xlsx"
        if not source.exists(): raise SystemExit(f"Source workbook missing: {source}")
        actual=sha(source)
        if actual != expected:
            raise SystemExit(f"{phase} source workbook hash changed: {actual}")
    print("Phase 4 required files: PASS")
    print("Phase 1/2/3 source workbook SHA-256 checks: PASS")
    print("Note: run DuckDB/report/API acceptance tests on a machine with Phase 4 requirements installed.")
if __name__=="__main__": main()
