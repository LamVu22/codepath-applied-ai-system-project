from src.recommender import Song, UserProfile, Recommender
from src.applied_ai_system import AppliedMusicAgent

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_agent_retrieves_context_and_recommends_focus_music():
    agent = AppliedMusicAgent()
    result = agent.run("I need chill lofi music for coding homework")

    titles = [song["title"] for song, _, _ in result.recommendations]
    assert result.retrieved_context
    assert result.confidence >= 0.6
    assert any(title in titles for title in ["Midnight Coding", "Library Rain", "Focus Flow"])


def test_agent_guardrail_handles_sleep_intense_conflict():
    agent = AppliedMusicAgent()
    result = agent.run("I want metal for sleep because I am anxious")

    assert result.guardrail_warnings
    assert result.inferred_profile["mood"] == "calm"
    assert result.recommendations[0][0]["energy"] <= 0.35
