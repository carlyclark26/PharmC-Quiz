# PharmC-Quiz

This repository generates practice questions for the top 200 outpatient drugs, covering both brand-to-generic and generic-to-brand directions. The generated content includes multiple-choice and fill-in-the-blank formats, grouped by direction so you can focus on either conversion.

## Data

Drug pairs live in [`data/top_200_drugs.csv`](data/top_200_drugs.csv) with `brand` and `generic` headers. Rows are intentionally ordered to mirror common study lists.

## Usage

1. Create questions as JSON:

   ```bash
   python quiz_generator.py --output quizzes.json
   ```

2. Adjust the number of multiple-choice distractors or random seed if desired:

   ```bash
   python quiz_generator.py --distractors 4 --seed 42 --output quizzes.json
   ```

The resulting `quizzes.json` has this shape:

```json
{
  "brand_to_generic": {
    "multiple_choice": [
      {
        "id": "brand_to_generic-mc-1",
        "question": "What is the generic for Synthroid?",
        "options": ["levothyroxine", "..."],
        "labeled_options": [
          {"label": "A", "display_label": "🔵 A", "text": "levothyroxine"},
          {"label": "B", "display_label": "🔵 B", "text": "..."}
        ],
        "answer": "levothyroxine"
      }
    ],
    "fill_in_the_blank": [
      {"id": "brand_to_generic-fib-1", "question": "Synthroid → ________ (generic)", "answer": "levothyroxine"}
    ]
  },
  "generic_to_brand": {
    "multiple_choice": [...],
    "fill_in_the_blank": [...]
  }
}
```

Each list contains all 200 brand/generic pairs so you can load them into a flashcard app or quiz engine.
