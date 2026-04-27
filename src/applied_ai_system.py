from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import logging
import re
from typing import Dict, Iterable, List, Tuple

from src.recommender import load_songs, recommend_songs


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = PROJECT_ROOT / "logs" / "system.log"


@dataclass
class RetrievedDocument:
    source: str
    score: float
    text: str


@dataclass
class AgentResult:
    query: str
    plan: List[str]
    inferred_profile: Dict
    retrieved_context: List[RetrievedDocument]
    recommendations: List[Tuple[Dict, float, str]]
    confidence: float
    guardrail_warnings: List[str]


def configure_logging() -> None:
    LOG_PATH.parent.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


class SimpleRetriever:
    """Small keyword retriever over project documents and song metadata."""

    def __init__(self, documents: Iterable[Tuple[str, str]]):
        self.documents = list(documents)

    @staticmethod
    def tokenize(text: str) -> set[str]:
        return set(re.findall(r"[a-z0-9]+", text.lower()))

    def retrieve(self, query: str, k: int = 4) -> List[RetrievedDocument]:
        query_tokens = self.tokenize(query)
        scored: List[RetrievedDocument] = []
        for source, text in self.documents:
            doc_tokens = self.tokenize(text)
            overlap = len(query_tokens & doc_tokens)
            if overlap:
                score = overlap / max(len(query_tokens), 1)
                scored.append(RetrievedDocument(source=source, score=score, text=text))

        scored.sort(key=lambda doc: doc.score, reverse=True)
        return scored[:k]


class AppliedMusicAgent:
    """
    Retrieval-augmented music recommender with observable planning,
    guardrails, confidence scoring, and logging.
    """

    DEFAULT_WEIGHTS = {
        "genre": 2.0,
        "mood": 1.2,
        "energy": 1.6,
        "tempo_bpm": 0.9,
        "valence": 1.0,
        "danceability": 0.7,
        "acousticness": 0.7,
    }

    GENRE_KEYWORDS = {
        "lofi": "lofi",
        "lo-fi": "lofi",
        "ambient": "ambient",
        "classical": "classical",
        "pop": "pop",
        "edm": "edm",
        "electronic": "edm",
        "rock": "rock",
        "metal": "metal",
        "jazz": "jazz",
        "hip hop": "hip hop",
        "rap": "hip hop",
        "synthwave": "synthwave",
        "folk": "folk",
        "country": "country",
        "blues": "blues",
    }

    MOOD_KEYWORDS = {
        "happy": ("happy", 0.82),
        "upbeat": ("happy", 0.78),
        "chill": ("chill", 0.42),
        "calm": ("calm", 0.25),
        "sleep": ("calm", 0.20),
        "study": ("focused", 0.38),
        "focus": ("focused", 0.42),
        "coding": ("focused", 0.42),
        "homework": ("focused", 0.40),
        "intense": ("intense", 0.88),
        "workout": ("energetic", 0.90),
        "gym": ("energetic", 0.92),
        "party": ("happy", 0.84),
        "dance": ("energetic", 0.88),
        "sad": ("moody", 0.35),
        "moody": ("moody", 0.48),
        "reflective": ("reflective", 0.34),
        "nostalgic": ("nostalgic", 0.48),
        "relaxed": ("relaxed", 0.38),
    }

    def __init__(self, songs_path: Path | None = None, knowledge_dir: Path | None = None):
        configure_logging()
        self.songs_path = songs_path or PROJECT_ROOT / "data" / "songs.csv"
        self.knowledge_dir = knowledge_dir or PROJECT_ROOT / "knowledge"
        self.songs = load_songs(str(self.songs_path))
        self.retriever = SimpleRetriever(self._build_documents())

    def _build_documents(self) -> List[Tuple[str, str]]:
        documents: List[Tuple[str, str]] = []
        for path in sorted(self.knowledge_dir.glob("*.md")):
            documents.append((str(path.relative_to(PROJECT_ROOT)), path.read_text(encoding="utf-8")))
        for song in self.songs:
            text = (
                f"{song['title']} by {song['artist']} is {song['genre']} with a {song['mood']} mood. "
                f"energy {song['energy']}, tempo {song['tempo_bpm']} bpm, valence {song['valence']}, "
                f"danceability {song['danceability']}, acousticness {song['acousticness']}."
            )
            documents.append((f"song:{song['id']}", text))
        return documents

    def infer_profile(self, query: str, retrieved_docs: List[RetrievedDocument]) -> Tuple[Dict, List[str]]:
        lowered = query.lower()
        warnings: List[str] = []
        profile = {
            "genre": None,
            "mood": None,
            "energy": 0.55,
            "tempo_bpm": 100,
            "valence": 0.60,
            "danceability": 0.60,
            "acousticness": 0.45,
            "weights": dict(self.DEFAULT_WEIGHTS),
        }

        for keyword, genre in self.GENRE_KEYWORDS.items():
            if keyword in lowered:
                profile["genre"] = genre
                break

        for keyword, (mood, energy) in self.MOOD_KEYWORDS.items():
            if keyword in lowered:
                profile["mood"] = mood
                profile["energy"] = energy
                break

        if any(word in lowered for word in ["sleep", "calm", "anxious", "anxiety", "relax"]):
            profile["energy"] = min(float(profile["energy"]), 0.32)
            profile["tempo_bpm"] = 72
            profile["danceability"] = 0.35
            profile["acousticness"] = 0.85
            profile["weights"]["energy"] = 2.4
            profile["weights"]["acousticness"] = 1.2

        if any(word in lowered for word in ["workout", "gym", "run", "party", "dance"]):
            profile["energy"] = max(float(profile["energy"]), 0.86)
            profile["tempo_bpm"] = 128
            profile["danceability"] = 0.88
            profile["acousticness"] = 0.12
            profile["weights"]["energy"] = 2.2
            profile["weights"]["danceability"] = 1.3

        if any(word in lowered for word in ["study", "focus", "coding", "homework", "read"]):
            profile["tempo_bpm"] = 82
            profile["valence"] = 0.58
            profile["danceability"] = 0.55
            profile["acousticness"] = 0.78
            profile["weights"]["mood"] = 1.6

        if "sad" in lowered or "heartbreak" in lowered:
            profile["valence"] = 0.35
            warnings.append("Low-valence request detected; recommendations avoid presenting music as emotional treatment.")

        if "sleep" in lowered and any(word in lowered for word in ["metal", "intense", "workout"]):
            warnings.append("Conflicting request: sleep context conflicts with intense/high-energy terms. Safety guardrail favors calm tracks.")
            profile["genre"] = None
            profile["mood"] = "calm"

        if profile["genre"] is None:
            warnings.append("No exact genre detected; using mood and audio features more heavily.")
            profile["weights"]["genre"] = 0.7

        if profile["mood"] is None:
            inferred_from_docs = self._infer_mood_from_docs(retrieved_docs)
            if inferred_from_docs:
                profile["mood"] = inferred_from_docs
            else:
                warnings.append("No clear mood detected; using balanced defaults.")
                profile["weights"]["mood"] = 0.6

        return profile, warnings

    def _infer_mood_from_docs(self, retrieved_docs: List[RetrievedDocument]) -> str | None:
        known_moods = {"happy", "chill", "focused", "calm", "intense", "energetic", "relaxed", "moody", "reflective"}
        joined = " ".join(doc.text.lower() for doc in retrieved_docs)
        for mood in known_moods:
            if mood in joined:
                return mood
        return None

    def run(self, query: str, k: int = 3) -> AgentResult:
        plan = [
            "Retrieve relevant listening guidelines and catalog facts.",
            "Infer a structured taste profile from the request.",
            "Apply guardrails for vague, conflicting, or sensitive requests.",
            "Rank songs and compute confidence from score separation and context coverage.",
        ]
        retrieved = self.retriever.retrieve(query, k=5)
        profile, warnings = self.infer_profile(query, retrieved)
        recommendations = recommend_songs(profile, self.songs, k=k)
        confidence = self._confidence(recommendations, retrieved, warnings)

        logging.info(
            "query=%r profile=%s top=%s confidence=%.2f warnings=%s",
            query,
            profile,
            [rec[0]["title"] for rec in recommendations],
            confidence,
            warnings,
        )
        return AgentResult(
            query=query,
            plan=plan,
            inferred_profile=profile,
            retrieved_context=retrieved,
            recommendations=recommendations,
            confidence=confidence,
            guardrail_warnings=warnings,
        )

    @staticmethod
    def _confidence(
        recommendations: List[Tuple[Dict, float, str]],
        retrieved_docs: List[RetrievedDocument],
        warnings: List[str],
    ) -> float:
        if not recommendations:
            return 0.0
        top_score = recommendations[0][1]
        runner_up = recommendations[1][1] if len(recommendations) > 1 else 0.0
        separation = min(max((top_score - runner_up) / 2.0, 0.0), 0.25)
        context_bonus = min(len(retrieved_docs) * 0.05, 0.20)
        warning_penalty = min(len(warnings) * 0.08, 0.24)
        confidence = 0.58 + separation + context_bonus - warning_penalty
        return round(min(max(confidence, 0.05), 0.95), 2)


def format_agent_result(result: AgentResult) -> str:
    lines = [
        f"Query: {result.query}",
        f"Confidence: {result.confidence:.2f}",
        "Plan:",
    ]
    lines.extend(f"- {step}" for step in result.plan)
    if result.guardrail_warnings:
        lines.append("Guardrails:")
        lines.extend(f"- {warning}" for warning in result.guardrail_warnings)
    lines.append("Retrieved context:")
    for doc in result.retrieved_context[:3]:
        lines.append(f"- {doc.source} (score {doc.score:.2f})")
    lines.append("Recommendations:")
    for index, (song, score, explanation) in enumerate(result.recommendations, start=1):
        lines.append(f"{index}. {song['title']} by {song['artist']} - {score:.2f}")
        lines.append(f"   {explanation}")
    return "\n".join(lines)
