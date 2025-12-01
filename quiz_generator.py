#!/usr/bin/env python3
"""Generate multiple-choice and fill-in-the-blank quizzes for the top 200 drugs.

The output groups questions by direction:
- brand_to_generic: asks for the generic equivalent of a brand name.
- generic_to_brand: asks for the brand equivalent of a generic name.

Each direction contains both multiple choice and fill-in-the-blank questions.
"""
import argparse
import csv
import json
import random
from pathlib import Path
from typing import Dict, List, Sequence

Question = Dict[str, object]


def load_drugs(csv_path: Path) -> List[Dict[str, str]]:
    """Load brand/generic pairs from ``csv_path``.

    The CSV is expected to have ``brand`` and ``generic`` headers.
    """
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [{"brand": row["brand"].strip(), "generic": row["generic"].strip()} for row in reader]


def build_multiple_choice(
    drugs: Sequence[Dict[str, str]], *, direction: str, distractor_count: int, seed: int
) -> List[Question]:
    """Create multiple-choice questions in the requested ``direction``.

    ``direction`` must be ``brand_to_generic`` or ``generic_to_brand``.
    ``distractor_count`` determines how many incorrect options are added.
    """
    rng = random.Random(seed)
    questions: List[Question] = []
    source_field, target_field = ("brand", "generic") if direction == "brand_to_generic" else ("generic", "brand")
    targets = [entry[target_field] for entry in drugs]

    for idx, entry in enumerate(drugs, start=1):
        prompt_value = entry[source_field]
        correct = entry[target_field]
        pool = [option for option in targets if option != correct]
        distractors = rng.sample(pool, k=min(distractor_count, len(pool)))
        options = distractors + [correct]
        rng.shuffle(options)
        labeled_options = []
        for option_idx, option_text in enumerate(options):
            label = chr(ord("A") + option_idx)
            labeled_options.append(
                {
                    "label": label,
                    "display_label": f"🔵 {label}",
                    "text": option_text,
                }
            )
        questions.append(
            {
                "id": f"{direction}-mc-{idx}",
                "question": f"What is the {target_field} for {prompt_value}?",
                "options": options,
                "labeled_options": labeled_options,
                "answer": correct,
            }
        )
    return questions


def build_fill_in_the_blank(drugs: Sequence[Dict[str, str]], *, direction: str) -> List[Question]:
    """Create fill-in-the-blank questions for a ``direction`` (brand or generic first)."""
    source_field, target_field = ("brand", "generic") if direction == "brand_to_generic" else ("generic", "brand")
    questions: List[Question] = []
    for idx, entry in enumerate(drugs, start=1):
        questions.append(
            {
                "id": f"{direction}-fib-{idx}",
                "question": f"{entry[source_field]} → ________ ({target_field})",
                "answer": entry[target_field],
            }
        )
    return questions


def generate_quiz(drugs: Sequence[Dict[str, str]], *, distractors: int, seed: int) -> Dict[str, Dict[str, List[Question]]]:
    """Build quiz content grouped by direction and question type."""
    return {
        "brand_to_generic": {
            "multiple_choice": build_multiple_choice(drugs, direction="brand_to_generic", distractor_count=distractors, seed=seed),
            "fill_in_the_blank": build_fill_in_the_blank(drugs, direction="brand_to_generic"),
        },
        "generic_to_brand": {
            "multiple_choice": build_multiple_choice(drugs, direction="generic_to_brand", distractor_count=distractors, seed=seed + 1),
            "fill_in_the_blank": build_fill_in_the_blank(drugs, direction="generic_to_brand"),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate quiz questions for top 200 drugs.")
    parser.add_argument("--data", type=Path, default=Path("data/top_200_drugs.csv"), help="Path to CSV of brand/generic pairs.")
    parser.add_argument("--output", type=Path, default=Path("quizzes.json"), help="Where to write the generated JSON.")
    parser.add_argument("--distractors", type=int, default=3, help="Number of distractors for multiple-choice questions.")
    parser.add_argument("--seed", type=int, default=2024, help="Random seed for reproducible shuffling.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    drugs = load_drugs(args.data)
    quiz = generate_quiz(drugs, distractors=args.distractors, seed=args.seed)
    args.output.write_text(json.dumps(quiz, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} with {len(drugs)} drug pairs.")


if __name__ == "__main__":
    main()
