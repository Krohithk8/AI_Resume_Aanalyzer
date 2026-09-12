#!/usr/bin/env python3
"""Analyze a text resume with Claude and present an evidence-based report."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# Fast and cost-conscious for an interactive portfolio demo.
MODEL = "claude-haiku-4-5-20251001"
REQUIRED_KEYS = {
    "match_score",
    "summary",
    "strengths",
    "gaps",
    "missing_keywords",
    "bullet_rewrites",
    "red_flags",
}

SYSTEM_PROMPT = """You are an expert technical recruiter with 15+ years of
experience screening software-engineering candidates. Be rigorous, fair, and
evidence-based. Base every observation only on the supplied resume and, when
provided, job description. Do not invent experience, technologies, metrics,
education, achievements, dates, or gaps that are not supported by the text.

Return strictly valid JSON only: no Markdown fences, no preamble, and no
trailing commentary. The response must use exactly this schema:
{
  "match_score": 0,
  "summary": "2-3 sentence plain-language verdict",
  "strengths": ["short strength strings"],
  "gaps": ["short gap strings"],
  "missing_keywords": ["ATS/recruiter keywords absent from resume"],
  "bullet_rewrites": [
    {"original": "verbatim weak bullet", "improved": "rewritten version with strong action verb and quantified impact"}
  ],
  "red_flags": ["formatting issues, vague claims, unexplained gaps"]
}

match_score must be an integer from 0 through 100. For improved bullets, retain
the resume's facts; if no metric is present, do not fabricate one. Use empty
lists when there are no applicable items."""


def parse_arguments() -> argparse.Namespace:
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze a plain-text resume with Claude."
    )
    parser.add_argument("--resume", required=True, type=Path, help="Path to a text resume")
    parser.add_argument("--jd", type=Path, help="Optional path to a job description")
    parser.add_argument("--output", type=Path, help="Optional JSON report output path")
    return parser.parse_args()


def read_text_file(path: Path, label: str) -> str:
    """Read a non-empty UTF-8 text file or exit with a helpful error."""
    if not path.is_file():
        raise ValueError(f"{label} file not found: {path}")
    try:
        content = path.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError as error:
        raise ValueError(f"{label} must be a UTF-8 plain-text file: {path}") from error
    if not content:
        raise ValueError(f"{label} file is empty: {path}")
    return content


def build_user_prompt(resume: str, job_description: str | None) -> str:
    """Build the analysis request from the supplied source documents."""
    if job_description:
        task = (
            "Compare the resume to the job description. Score role fit and identify "
            "keywords that are present in the job description but absent from the resume."
        )
        job_section = f"\n\nJOB DESCRIPTION:\n{job_description}"
    else:
        task = (
            "Evaluate overall resume quality for technical recruiting. Set match_score "
            "as a general market-readiness score; missing_keywords may be empty."
        )
        job_section = ""
    return f"{task}\n\nRESUME:\n{resume}{job_section}"


def strip_json_fences(text: str) -> str:
    """Remove one accidental Markdown JSON fence surrounding model output."""
    cleaned = text.strip()
    if cleaned.startswith("```") and cleaned.endswith("```"):
        lines = cleaned.splitlines()
        if len(lines) >= 2:
            return "\n".join(lines[1:-1]).strip()
    return cleaned


def validate_report(report: Any) -> dict[str, Any]:
    """Validate the model response shape and return it as a report dictionary."""
    if not isinstance(report, dict):
        raise ValueError("The JSON response must be an object.")
    if set(report) != REQUIRED_KEYS:
        missing = REQUIRED_KEYS - set(report)
        extra = set(report) - REQUIRED_KEYS
        details = []
        if missing:
            details.append(f"missing keys: {', '.join(sorted(missing))}")
        if extra:
            details.append(f"unexpected keys: {', '.join(sorted(extra))}")
        raise ValueError("Response does not match the required schema (" + "; ".join(details) + ").")
    if not isinstance(report["match_score"], int) or isinstance(report["match_score"], bool) or not 0 <= report["match_score"] <= 100:
        raise ValueError("match_score must be an integer from 0 to 100.")
    if not isinstance(report["summary"], str):
        raise ValueError("summary must be a string.")
    for key in ("strengths", "gaps", "missing_keywords", "red_flags"):
        if not isinstance(report[key], list) or not all(isinstance(item, str) for item in report[key]):
            raise ValueError(f"{key} must be a list of strings.")
    if not isinstance(report["bullet_rewrites"], list):
        raise ValueError("bullet_rewrites must be a list.")
    for rewrite in report["bullet_rewrites"]:
        if not isinstance(rewrite, dict) or set(rewrite) != {"original", "improved"}:
            raise ValueError("Each bullet rewrite must contain only original and improved strings.")
        if not all(isinstance(rewrite[key], str) for key in ("original", "improved")):
            raise ValueError("Bullet rewrite values must be strings.")
    return report


def parse_model_response(raw_output: str) -> dict[str, Any]:
    """Parse fenced or unfenced JSON and raise a diagnostic error if invalid."""
    cleaned = strip_json_fences(raw_output)
    try:
        report = json.loads(cleaned)
        return validate_report(report)
    except (json.JSONDecodeError, ValueError) as error:
        raise ValueError(
            f"Claude returned an invalid report: {error}\n\nRaw model output:\n{raw_output}"
        ) from error


def analyze_resume(resume: str, job_description: str | None, api_key: str) -> dict[str, Any]:
    """Call Claude and return its validated structured report."""
    try:
        from anthropic import Anthropic
    except ImportError as error:
        raise RuntimeError(
            "The anthropic package is not installed. Run: pip install -r requirements.txt"
        ) from error
    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1800,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(resume, job_description)}],
    )
    raw_output = "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )
    if not raw_output:
        raise ValueError("Claude returned no text content.")
    return parse_model_response(raw_output)


def format_list(items: list[str]) -> str:
    """Format a string list for a human-readable terminal report."""
    return "\n".join(f"  - {item}" for item in items) if items else "  None identified."


def format_report(report: dict[str, Any]) -> str:
    """Format a validated report as readable terminal text."""
    rewrites = report["bullet_rewrites"]
    rewrite_text = "\n".join(
        f"  Original: {item['original']}\n  Improved: {item['improved']}"
        for item in rewrites
    ) if rewrites else "  None suggested."
    return (
        "\nAI RESUME ANALYZER\n"
        "=" * 58
        + f"\nMatch score: {report['match_score']}/100\n\nSummary\n{report['summary']}"
        + f"\n\nStrengths\n{format_list(report['strengths'])}"
        + f"\n\nGaps\n{format_list(report['gaps'])}"
        + f"\n\nMissing ATS keywords\n{format_list(report['missing_keywords'])}"
        + f"\n\nBullet-point rewrites\n{rewrite_text}"
        + f"\n\nRed flags\n{format_list(report['red_flags'])}\n"
    )


def main() -> int:
    """Run the CLI and return a process exit status."""
    args = parse_arguments()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY is not set. Export it before running this tool.", file=sys.stderr)
        return 2
    try:
        resume = read_text_file(args.resume, "Resume")
        job_description = read_text_file(args.jd, "Job description") if args.jd else None
        report = analyze_resume(resume, job_description, api_key)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(f"JSON report saved to: {args.output}")
        print(format_report(report))
        return 0
    except Exception as error:  # Keep CLI failures concise and actionable.
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
