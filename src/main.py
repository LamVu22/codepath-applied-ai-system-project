"""Command line runner for the applied AI music recommendation system."""

from src.applied_ai_system import AppliedMusicAgent, format_agent_result


def main() -> None:
    agent = AppliedMusicAgent()
    demo_queries = [
        "I need chill lofi music for coding homework tonight",
        "Give me high energy songs for a gym workout",
        "I want metal for sleep because I am anxious",
        "Give me songs to relieve stress and relax after a long day"
    ]

    for query in demo_queries:
        print("=" * 72)
        print(format_agent_result(agent.run(query)))
        print()


if __name__ == "__main__":
    main()
