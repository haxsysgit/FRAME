#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_DIMENSIONS = (
    "coverage",
    "clarity",
    "agent_usefulness",
    "retrieval_usefulness",
    "stability",
    "adoptability",
    "bloat_resistance",
    "token_efficiency",
)


@dataclass(slots=True)
class Scorecard:
    path: Path
    candidate: str
    candidate_version: str
    fixture: str
    status: str
    scale_max: float
    weighted_total: float
    raw_average: float
    scores: dict[str, float]
    weights: dict[str, float]


def load_scorecard(path: Path, *, include_drafts: bool) -> Scorecard | None:
    data = tomllib.loads(path.read_text(encoding="utf-8"))

    meta = data.get("meta", {})
    status = str(meta.get("status", "draft"))
    if status != "complete" and not include_drafts:
        return None

    scores = data.get("scores", {})
    weights = data.get("weights", {})
    candidate = str(meta.get("candidate", "unknown-candidate"))
    candidate_version = str(meta.get("candidate_version", "unknown-version"))
    fixture = str(meta.get("fixture", path.stem))
    scale_max = float(meta.get("scale_max", 5))

    missing = [dimension for dimension in REQUIRED_DIMENSIONS if dimension not in scores]
    if missing:
        raise ValueError(f"{path}: missing scores for {', '.join(missing)}")

    weighted_sum = 0.0
    weight_total = 0.0
    raw_values: list[float] = []

    for dimension in REQUIRED_DIMENSIONS:
        score = float(scores[dimension])
        if score < 0 or score > scale_max:
            raise ValueError(
                f"{path}: score for '{dimension}' must be between 0 and {scale_max}"
            )

        weight = float(weights.get(dimension, 1.0))
        if weight < 0:
            raise ValueError(f"{path}: weight for '{dimension}' cannot be negative")

        weighted_sum += score * weight
        weight_total += weight
        raw_values.append(score)

    weighted_total = 0.0 if weight_total == 0 else weighted_sum / weight_total
    raw_average = sum(raw_values) / len(raw_values)

    return Scorecard(
        path=path,
        candidate=candidate,
        candidate_version=candidate_version,
        fixture=fixture,
        status=status,
        scale_max=scale_max,
        weighted_total=weighted_total,
        raw_average=raw_average,
        scores={dimension: float(scores[dimension]) for dimension in REQUIRED_DIMENSIONS},
        weights={dimension: float(weights.get(dimension, 1.0)) for dimension in REQUIRED_DIMENSIONS},
    )


def discover_scorecard_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(
        path
        for path in target.rglob("*.toml")
        if path.name != "scorecard-template.toml"
    )


def summarize_by_candidate(scorecards: list[Scorecard]) -> dict[tuple[str, str], dict[str, Any]]:
    summary: dict[tuple[str, str], dict[str, Any]] = {}
    for scorecard in scorecards:
        key = (scorecard.candidate, scorecard.candidate_version)
        bucket = summary.setdefault(
            key,
            {
                "count": 0,
                "weighted_total_sum": 0.0,
                "raw_average_sum": 0.0,
                "dimension_sums": {dimension: 0.0 for dimension in REQUIRED_DIMENSIONS},
            },
        )
        bucket["count"] += 1
        bucket["weighted_total_sum"] += scorecard.weighted_total
        bucket["raw_average_sum"] += scorecard.raw_average
        for dimension in REQUIRED_DIMENSIONS:
            bucket["dimension_sums"][dimension] += scorecard.scores[dimension]
    return summary


def print_scorecards(scorecards: list[Scorecard]) -> None:
    print("Per-scorecard results")
    print("candidate\tversion\tfixture\tweighted\traw_avg\tfile")
    for scorecard in sorted(scorecards, key=lambda item: (-item.weighted_total, item.candidate, item.fixture)):
        print(
            f"{scorecard.candidate}\t{scorecard.candidate_version}\t{scorecard.fixture}\t"
            f"{scorecard.weighted_total:.2f}/{scorecard.scale_max:.0f}\t"
            f"{scorecard.raw_average:.2f}/{scorecard.scale_max:.0f}\t{scorecard.path}"
        )


def print_candidate_summary(scorecards: list[Scorecard]) -> None:
    summary = summarize_by_candidate(scorecards)
    print()
    print("Candidate summary")
    print("candidate\tversion\tscorecards\tweighted_avg\traw_avg")

    ranked = []
    for (candidate, version), bucket in summary.items():
        count = bucket["count"]
        weighted_avg = bucket["weighted_total_sum"] / count
        raw_avg = bucket["raw_average_sum"] / count
        ranked.append((weighted_avg, candidate, version, count, raw_avg, bucket))

    for weighted_avg, candidate, version, count, raw_avg, _bucket in sorted(ranked, reverse=True):
        print(f"{candidate}\t{version}\t{count}\t{weighted_avg:.2f}/5\t{raw_avg:.2f}/5")

    print()
    print("Average dimension scores by candidate")
    for weighted_avg, candidate, version, count, _raw_avg, bucket in sorted(ranked, reverse=True):
        print(f"- {candidate} {version} ({count} scorecard{'s' if count != 1 else ''}, weighted avg {weighted_avg:.2f}/5)")
        for dimension in REQUIRED_DIMENSIONS:
            dimension_avg = bucket["dimension_sums"][dimension] / count
            print(f"  - {dimension}: {dimension_avg:.2f}/5")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate FRAME Lab scorecards from TOML files."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="Frame lab/evaluations/scoring",
        help="Scorecard file or directory (default: Frame lab/evaluations/scoring)",
    )
    parser.add_argument(
        "--include-drafts",
        action="store_true",
        help="Include draft scorecards instead of only complete ones.",
    )
    args = parser.parse_args(argv)

    target = Path(args.target)
    if not target.exists():
        print(f"Target not found: {target}", file=sys.stderr)
        return 1

    files = discover_scorecard_files(target)
    if not files:
        print(f"No scorecards found under {target}")
        return 0

    scorecards: list[Scorecard] = []
    for path in files:
        scorecard = load_scorecard(path, include_drafts=args.include_drafts)
        if scorecard is not None:
            scorecards.append(scorecard)

    if not scorecards:
        print("No complete scorecards found. (Drafts are ignored by default.)")
        return 0

    print_scorecards(scorecards)
    print_candidate_summary(scorecards)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
