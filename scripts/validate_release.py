"""Validate release files and, when supplied, immutable source workbook hashes."""
from pathlib import Path
import argparse
import hashlib
import os

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_SHA256 = "49935362af5d65ca1a737946961fe4ea3b0708ee2677e7eb38a4eafa8cbb917e"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-root",
        default=os.getenv("PULSEIQ_SOURCE_ROOT"),
        help="Folder containing phase-1, phase-2 and phase-3 folders (or set PULSEIQ_SOURCE_ROOT).",
    )
    parser.add_argument(
        "--require-source-workbooks",
        action="store_true",
        help="Fail if the three original source workbooks are not available for hash verification.",
    )
    args = parser.parse_args()

    required = [
        ROOT / "api.py",
        ROOT / "explorer.py",
        ROOT / "build_report.py",
        ROOT / "board_pack.py",
        ROOT / "board_pack" / "PulseIQ_Board_Pack_Phase4.pptx",
        ROOT / "docs" / "ACCEPTANCE_CHECKLIST.md",
        ROOT / "RELEASE_NOTES.md",
        ROOT / "phase4_complete" / "security" / "policy.py",
        ROOT / "phase4_complete" / "config" / "metric_permissions.csv",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise SystemExit("Missing release files:\n" + "\n".join(missing))
    print("Required Phase 4 files: PASS")

    if not args.source_root:
        message = "Source workbook hash check: NOT RUN (set PULSEIQ_SOURCE_ROOT to the Phase 1-3 workspace)."
        if args.require_source_workbooks:
            raise SystemExit(message)
        print(message)
        return

    source_root = Path(args.source_root).expanduser().resolve()
    failures = []
    for phase in ("phase-1", "phase-2", "phase-3"):
        source = source_root / phase / "data" / "PulseIQ_Dataset.xlsx"
        if not source.is_file():
            failures.append(f"Missing source workbook: {source}")
            continue
        actual = sha256(source)
        if actual != EXPECTED_SOURCE_SHA256:
            failures.append(f"{phase} source workbook hash mismatch: {actual}")
    if failures:
        raise SystemExit("\n".join(failures))
    print("Phase 1/2/3 source workbook SHA-256 checks: PASS")


if __name__ == "__main__":
    main()
