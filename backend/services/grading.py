"""Server-side answer grading.

correct_answer_id is stripped from every lesson the client receives, so the
client cannot grade. Answers are collected locally during the lesson and graded
here in one batch at completion, which is also what makes editing an earlier
answer safe: nothing is scored, and no XP moves, until the single submit.
"""

import re

_PUNCTUATION = re.compile(r"[.,!?;:\"“”‘’]")
_WHITESPACE = re.compile(r"\s+")


def normalize_answer(text: str) -> str:
    """Lowercase, trim, collapse whitespace, drop non-meaningful punctuation.

    Apostrophes and hyphens are kept: they are meaningful inside words in
    several of the supported languages.
    """
    if not text:
        return ""
    cleaned = _PUNCTUATION.sub("", text.strip().lower())
    return _WHITESPACE.sub(" ", cleaned)


def resolve_typed_answer(question: dict, typed: str) -> str | None:
    """Match free text against the options' texts.

    Option text may hold slash-separated alternatives ("Happy/Feeling good");
    any one alternative matching is accepted.
    """
    target = normalize_answer(typed)
    if not target:
        return None
    for option in question.get("options") or []:
        alternatives = (option.get("text") or "").split("/")
        if any(normalize_answer(alt) == target for alt in alternatives):
            return option.get("id")
    return None


def grade_answer(question: dict, answer_id: str | None, answer_text: str | None) -> dict:
    """Grade one submitted answer against its question."""
    correct_id = question.get("correct_answer_id")
    resolved = answer_id
    if resolved is None and answer_text is not None:
        resolved = resolve_typed_answer(question, answer_text)

    correct_text = next(
        (o.get("text") for o in (question.get("options") or []) if o.get("id") == correct_id),
        None,
    )
    return {
        "question_id": question.get("id"),
        "correct": resolved is not None and resolved == correct_id,
        "answer_given": resolved if resolved is not None else (answer_text or ""),
        "answer_text": answer_text,
        "correct_answer_id": correct_id,
        "correct_answer_text": correct_text,
    }


def grade_lesson(questions: list[dict], submitted: list) -> tuple[list[dict], int]:
    """Grade every submitted answer. Returns (results, score 0-100).

    Unanswered questions count against the score, so skipping is not a way to
    inflate accuracy.
    """
    by_id = {q.get("id"): q for q in questions}
    results = []
    for answer in submitted:
        question = by_id.get(answer.question_id)
        if not question:
            continue
        results.append(grade_answer(question, answer.answer_id, answer.answer_text))

    total = len(questions) or len(results)
    if not total:
        return results, 0
    correct = sum(1 for r in results if r["correct"])
    return results, round(correct / total * 100)
