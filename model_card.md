# Model Card: VibeMatch Applied AI System

## Model Name

VibeMatch Applied AI System 2.0

## Intended Use

This system recommends songs from a small classroom catalog based on natural-language listening requests. It is intended for a portfolio/class project that demonstrates retrieval, agentic planning, guardrails, confidence scoring, and reliability testing.

It is not intended for production music personalization, health advice, emotional diagnosis, or any high-stakes decision.

## How It Works

The system combines three parts:

1. Retrieval: `SimpleRetriever` searches custom knowledge files and song metadata.
2. Agentic workflow: `AppliedMusicAgent` follows visible steps: retrieve context, infer a profile, apply guardrails, rank songs, and compute confidence.
3. Scoring: the original content-based recommender scores each song using genre, mood, energy, tempo, valence, danceability, and acousticness.

The output includes recommendations, reasons, confidence, retrieved sources, and warnings.

## Data

The song catalog is `data/songs.csv` with 18 hand-labeled songs. The retrieval corpus also includes:

- `knowledge/listening_guidelines.md`
- `knowledge/genre_mood_map.md`

The data is small and not culturally comprehensive. It underrepresents many genres, languages, artists, and listening contexts.

## Guardrails

The system adds warnings when:

- No exact genre is detected.
- No clear mood is detected.
- A low-valence emotional request appears.
- Sleep/anxiety language conflicts with intense or high-energy music.

For sleep or anxiety-related requests, it avoids presenting recommendations as treatment and favors calmer, lower-energy tracks.

## Evaluation Results

Automated tests:

```text
pytest -q
4 passed
```

Evaluation harness:

```text
python -m src.evaluate
4/4 checks passed
```

The four evaluation cases cover lofi study music, workout music, a conflicting sleep/metal request, and sad reflective acoustic music.

## Strengths

- Reproducible without API keys.
- Easy to inspect because retrieved context, plan, confidence, and warnings are printed.
- Reliable on the included test cases.
- Guardrails improve behavior for conflicting emotional/sleep requests.

## Limitations And Biases

The system relies on keyword matching, so it may miss indirect language or mixed preferences. The catalog is small, so recommendations can become repetitive. Hand-labeled genre and mood values encode subjective assumptions. The system does not understand lyrics, artist background, culture, user history, or real-time popularity.

## Misuse Risks

The system could be misused if someone treats music recommendations as emotional or medical advice. To reduce that risk, the system avoids therapeutic claims and logs guardrail warnings for sensitive requests.

## What Surprised Me

The reliability tests showed that the same scoring system could produce very different behavior once guardrails changed the inferred profile. The "metal for sleep" case was especially useful because it exposed how a literal match can be less responsible than a context-aware recommendation.

## AI Collaboration Reflection

AI assistance helped me identify a practical final-project scope: extend the original recommender with retrieval, guardrails, confidence, and evaluation instead of rebuilding the whole app. A flawed AI suggestion was to make the app behave like an open-ended chatbot; I rejected that because it would be harder to test and less reproducible. The better choice was a narrow applied AI system with observable intermediate steps.
