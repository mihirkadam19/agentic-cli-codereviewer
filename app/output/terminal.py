"""Renders findings to the terminal.

This never looks at how many agents ran or what they were called
(beyond the label) -- it only knows about Finding objects. A JSON or
GitHub-comment formatter can be added alongside this one the same way.
"""
from __future__ import annotations

from app.schema import Finding, Severity

_ICONS = {Severity.ERROR: "x", Severity.WARNING: "!", Severity.INFO: "i"}


def print_findings(findings: list[Finding]) -> None:
    if not findings:
        print("No issues found.")
        return

    by_file: dict[str, list[Finding]] = {}
    for f in findings:
        by_file.setdefault(f.file, []).append(f)

    for file, file_findings in by_file.items():
        print(f"\n{file}")
        for f in sorted(file_findings, key=lambda x: x.line or 0):
            loc = f"line {f.line}" if f.line else "general"
            print(f"  [{_ICONS[f.severity]}] ({f.agent}) {loc}: {f.message}")
            if f.suggestion:
                print(f"      -> {f.suggestion}")
