from src.applied_ai_system import AppliedMusicAgent


CASES = [
    {
        "query": "chill lofi study music for homework",
        "expected_any": {"Midnight Coding", "Library Rain", "Focus Flow"},
        "min_confidence": 0.60,
    },
    {
        "query": "high energy dance music for a workout",
        "expected_any": {"Neon Circuit", "Gym Hero", "Sunrise City"},
        "min_confidence": 0.60,
    },
    {
        "query": "metal for sleep because I feel anxious",
        "expected_any": {"Cathedral Echoes", "Spacewalk Thoughts"},
        "min_confidence": 0.50,
        "requires_guardrail": True,
    },
    {
        "query": "sad reflective acoustic evening songs",
        "expected_any": {"Porchlight Tales", "Blue Room Afterglow", "Desert Highway"},
        "min_confidence": 0.50,
    },
]


def evaluate() -> int:
    agent = AppliedMusicAgent()
    passed = 0
    print("Reliability Evaluation")
    print("======================")
    for case in CASES:
        result = agent.run(case["query"])
        titles = {song["title"] for song, _, _ in result.recommendations}
        has_expected = bool(titles & case["expected_any"])
        has_confidence = result.confidence >= case["min_confidence"]
        has_guardrail = not case.get("requires_guardrail") or bool(result.guardrail_warnings)
        ok = has_expected and has_confidence and has_guardrail
        passed += int(ok)
        print(f"{'PASS' if ok else 'FAIL'}: {case['query']}")
        print(f"  Top results: {', '.join(titles)}")
        print(f"  Confidence: {result.confidence:.2f}")
        if result.guardrail_warnings:
            print(f"  Guardrails: {' | '.join(result.guardrail_warnings)}")
    print(f"\nSummary: {passed}/{len(CASES)} checks passed")
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    raise SystemExit(evaluate())
