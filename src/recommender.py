from typing import List, Dict, Tuple
from dataclasses import dataclass
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs for a user profile."""
        scored: List[Tuple[Song, float]] = []
        for song in self.songs:
            score = 0.0
            if song.genre == user.favorite_genre:
                score += 2.0
            if song.mood == user.favorite_mood:
                score += 1.0

            energy_similarity = 1.0 - abs(song.energy - user.target_energy)
            if energy_similarity < 0:
                energy_similarity = 0.0
            score += 1.5 * energy_similarity

            if user.likes_acoustic:
                score += 0.5 * song.acousticness
            else:
                score += 0.5 * (1.0 - song.acousticness)

            scored.append((song, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        return [item[0] for item in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a short explanation for a recommended song."""
        reasons: List[str] = []
        if song.genre == user.favorite_genre:
            reasons.append("genre match (+2.0)")
        if song.mood == user.favorite_mood:
            reasons.append("mood match (+1.0)")

        energy_similarity = 1.0 - abs(song.energy - user.target_energy)
        if energy_similarity < 0:
            energy_similarity = 0.0
        reasons.append(f"energy similarity (+{1.5 * energy_similarity:.2f})")

        if user.likes_acoustic:
            reasons.append(f"prefers acoustic (+{0.5 * song.acousticness:.2f})")
        else:
            reasons.append(f"prefers non-acoustic (+{0.5 * (1.0 - song.acousticness):.2f})")

        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file as a list of dictionaries."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": int(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                }
            )
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a single song against user preferences."""
    reasons: List[str] = []
    score = 0.0

    weights = user_prefs.get("weights", {})
    genre_weight = float(weights.get("genre", 2.0))
    mood_weight = float(weights.get("mood", 1.0))
    energy_weight = float(weights.get("energy", 1.5))
    tempo_weight = float(weights.get("tempo_bpm", 1.0))
    valence_weight = float(weights.get("valence", 1.0))
    dance_weight = float(weights.get("danceability", 0.5))
    acoustic_weight = float(weights.get("acousticness", 0.5))

    if user_prefs.get("genre") and song.get("genre") == user_prefs["genre"]:
        score += genre_weight
        reasons.append(f"genre match (+{genre_weight:.1f})")

    if not user_prefs.get("disable_mood"):
        if user_prefs.get("mood") and song.get("mood") == user_prefs["mood"]:
            score += mood_weight
            reasons.append(f"mood match (+{mood_weight:.1f})")

    target_energy = user_prefs.get("energy")
    if target_energy is not None:
        energy_similarity = 1.0 - abs(song["energy"] - float(target_energy))
        if energy_similarity < 0:
            energy_similarity = 0.0
        energy_score = energy_weight * energy_similarity
        score += energy_score
        reasons.append(f"energy similarity (+{energy_score:.2f})")

    target_tempo = user_prefs.get("tempo_bpm")
    if target_tempo is not None:
        tempo_range = 120.0
        tempo_similarity = 1.0 - (abs(song["tempo_bpm"] - float(target_tempo)) / tempo_range)
        if tempo_similarity < 0:
            tempo_similarity = 0.0
        tempo_score = tempo_weight * tempo_similarity
        score += tempo_score
        reasons.append(f"tempo similarity (+{tempo_score:.2f})")

    target_valence = user_prefs.get("valence")
    if target_valence is not None:
        valence_similarity = 1.0 - abs(song["valence"] - float(target_valence))
        if valence_similarity < 0:
            valence_similarity = 0.0
        valence_score = valence_weight * valence_similarity
        score += valence_score
        reasons.append(f"valence similarity (+{valence_score:.2f})")

    target_dance = user_prefs.get("danceability")
    if target_dance is not None:
        dance_similarity = 1.0 - abs(song["danceability"] - float(target_dance))
        if dance_similarity < 0:
            dance_similarity = 0.0
        dance_score = dance_weight * dance_similarity
        score += dance_score
        reasons.append(f"danceability similarity (+{dance_score:.2f})")

    target_acoustic = user_prefs.get("acousticness")
    if target_acoustic is not None:
        acoustic_similarity = 1.0 - abs(song["acousticness"] - float(target_acoustic))
        if acoustic_similarity < 0:
            acoustic_similarity = 0.0
        acoustic_score = acoustic_weight * acoustic_similarity
        score += acoustic_score
        reasons.append(f"acousticness similarity (+{acoustic_score:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Recommend the top k songs, sorted by score."""
    scored: List[Tuple[Dict, float, str]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons) if reasons else "no strong matches"
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
