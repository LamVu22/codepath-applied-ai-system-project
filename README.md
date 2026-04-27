# VibeMatch Applied AI System

VibeMatch is a retrieval-augmented music recommendation system that turns a natural-language listening request into ranked song recommendations with explanations, confidence scoring, guardrails, and an evaluation harness.

## Original Project

Base project: `Project3_MusicRecommenderSimulation`.

The original Module 3 project was a content-based music recommender. It loaded a small CSV catalog, compared each song against a structured user profile, scored genre/mood/numeric feature similarity, and printed top recommendations with short explanations. This final version keeps that scoring engine but wraps it in an applied AI workflow that can interpret free-text user requests, retrieve custom context, apply guardrails, and evaluate reliability.

## What The System Does

- Accepts natural-language requests such as "chill lofi music for coding homework."
- Retrieves relevant context from custom documents in `knowledge/` and song metadata from `data/songs.csv`.
- Infers a structured taste profile: genre, mood, energy, tempo, valence, danceability, and acousticness.
- Applies guardrails for vague, emotionally sensitive, or conflicting requests.
- Ranks songs with the original recommender logic.
- Prints an observable plan, retrieved context, recommendations, explanations, and a confidence score.
- Logs each run to `logs/system.log`.
- Includes automated tests and an evaluation script.

## Architecture Overview

![System architecture](assets/system_architecture.svg)

Data flow:

1. A human enters a music request.
2. `AppliedMusicAgent` retrieves matching context from project knowledge docs and song metadata.
3. The agent infers a structured profile from the request.
4. Guardrails adjust unsafe or conflicting requests, such as asking for intense music for sleep.
5. The content-based scorer ranks the catalog.
6. The system returns recommendations with reasons and confidence.
7. `src/evaluate.py` checks expected behavior across predefined scenarios.

## Project Structure

```text
assets/                 System diagram files
data/songs.csv          Song catalog
knowledge/              Custom retrieval documents
src/applied_ai_system.py Retrieval, planning, guardrails, confidence
src/recommender.py      Original scoring engine
src/main.py             End-to-end CLI demo
src/evaluate.py         Reliability evaluation script
tests/                  Unit and behavior tests
model_card.md           Ethics, limitations, and reflection
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the end-to-end demo:

```bash
python -m src.main
```

Run tests:

```bash
pytest -q
```

Run the reliability evaluation:

```bash
python -m src.evaluate
```

## Sample Interactions

### Input 1

```text
I need chill lofi music for coding homework tonight
```

Output summary:

```text
Confidence: 0.85
Retrieved context: listening_guidelines.md, genre_mood_map.md, song:2
1. Midnight Coding by LoRoom - genre match, mood match, energy/tempo similarity
2. Library Rain by Paper Lanterns - genre match, mood match, acousticness similarity
3. Focus Flow by LoRoom - genre match, focus-friendly audio features
```

### Input 2

```text
Give me high energy songs for a gym workout
```

Output summary:

```text
Confidence: 0.95
Guardrail: No exact genre detected; using mood and audio features more heavily.
1. Neon Circuit by Phase Drift
2. Gym Hero by Max Pulse
3. Storm Runner by Voltline
```

### Input 3

```text
I want metal for sleep because I am anxious
```

Output summary:

```text
Confidence: 0.82
Guardrail: sleep context conflicts with intense/high-energy terms, so calm tracks are favored.
1. Cathedral Echoes by Aurora Strings
2. Spacewalk Thoughts by Orbit Bloom
3. Library Rain by Paper Lanterns
```

## Design Decisions

I used deterministic retrieval and scoring instead of an external LLM so the project is reproducible without API keys. The RAG layer retrieves both custom listening guidelines and catalog metadata, then the agent uses that context to infer the profile that drives recommendations. This makes the AI behavior inspectable: every run shows the plan, retrieved sources, inferred profile effects, confidence, and guardrail warnings.

The main trade-off is flexibility versus reliability. A full LLM could understand more nuanced language, but it would be harder to test and might produce inconsistent outputs. This version handles a smaller set of intents but is easier to debug and evaluate.

## Reliability And Evaluation

Reliability tools included:

- Unit tests for the original scoring logic.
- Behavior tests for RAG context retrieval and guardrail behavior.
- `src/evaluate.py`, a test harness with four predefined user requests.
- Confidence scoring based on top-score separation, retrieved-context coverage, and warning penalties.
- Runtime logging in `logs/system.log`.

Current result:

```text
pytest: 4 passed
evaluation: 4/4 checks passed
```

What worked: clear requests for lofi study, workout music, and calm sleep music produced expected top results. The guardrail correctly overrode the conflicting "metal for sleep" request. What did not work perfectly: vague requests still depend on keyword matching, so the system lowers confidence and explains uncertainty instead of pretending to know more than it does.

## Reflection And Ethics

Limitations and bias: The catalog is tiny and hand-labeled, so recommendations reflect the available genres and feature values. Exact keyword parsing can miss slang, multilingual requests, or mixed preferences. The system can also over-recommend similar songs because it optimizes fit rather than diversity.

Possible misuse: This should not be used as mental health advice or as a claim that music can treat anxiety, sadness, or sleep problems. Guardrails avoid therapeutic claims and favor lower-risk recommendations when emotional or sleep-related terms appear.

Reliability surprise: The guardrail case was the most interesting test. Without the guardrail, a literal genre match could recommend intense metal for sleep. Adding a simple conflict check made the output more responsible.

AI collaboration: AI assistance was helpful for brainstorming the agent workflow and evaluation cases. One flawed suggestion was to make the system sound more like a general chatbot; I kept it narrower because a constrained, testable recommender is more reliable for this project.

## Presentation And Walkthrough

I had trouble recording a Loom walkthrough, so this section is written as the walkthrough I would present in the video. It explains the end-to-end run, the AI feature behavior, the guardrails, and the reliability test results.

### Walkthrough Script

First, I would introduce the project as an applied AI music recommendation system. The original Module 3 project accepted structured music preferences and scored songs from a CSV file. In this final version, the system accepts natural-language requests, retrieves relevant context, infers a structured profile, applies guardrails, and returns recommendations with explanations and confidence scores.

The command below runs the end-to-end applied AI workflow:

```bash
python -m src.main
```

When `src.main` runs, it creates an `AppliedMusicAgent` and sends several demo prompts through the full system. For each prompt, the agent prints:

- the original user query
- a confidence score
- the agent's observable plan
- retrieved context from `knowledge/` and song metadata
- guardrail warnings when needed
- ranked recommendations with scoring explanations

The important part is that the retrieved context is not just printed beside the answer. It changes how the system builds the recommendation profile. For example, study and coding requests shift the profile toward focused, lower-energy, more acoustic songs. Workout requests shift the profile toward high energy and high danceability. Sleep or anxiety-related requests activate safer low-energy behavior.

### Demo Screenshot 1

![Demo 1 output](screenshots/demo1.png)

In the first half of this screenshot, the prompt is:

```text
I need chill lofi music for coding homework tonight
```

The system retrieves `knowledge/listening_guidelines.md`, `knowledge/genre_mood_map.md`, and a matching song document from the catalog. From that context and the query words, the agent infers that this is a study/coding request. It builds a profile that favors lofi, chill or focused mood, moderate-low energy, steady tempo, and higher acousticness. The top recommendations are `Midnight Coding`, `Library Rain`, and `Focus Flow`, which makes sense because they are lofi tracks with study-friendly energy and acousticness scores.

In the second half of the screenshot, the prompt is:

```text
Give me high energy songs for a gym workout
```

This demonstrates the system's behavior when the user gives a use case but no exact genre. The guardrail says no exact genre was detected, so the system lowers the genre weight and relies more on energy, danceability, tempo, and mood. The top results become `Neon Circuit`, `Gym Hero`, and `Storm Runner`, which are high-energy songs that fit a workout context.

### Demo Screenshot 2

![Demo 2 output](screenshots/demo2.png)

This screenshot demonstrates reliability and guardrail behavior. The first prompt is:

```text
I want metal for sleep because I am anxious
```

A simple recommender might over-prioritize the word "metal" and return intense, high-energy songs. This system detects a conflict: sleep and anxiety-related language should not be handled the same way as a workout or intense music request. The guardrail warning explains that sleep conflicts with intense/high-energy terms, so the system favors calm tracks. That is why the output recommends `Cathedral Echoes`, `Spacewalk Thoughts`, and `Library Rain` instead of metal songs.

The final prompt is:

```text
Give me songs to relieve stress and relax after a long day
```

This request is more vague because it does not name a genre. The system reports lower confidence than the clearer examples and again warns that no exact genre was detected. It then uses the retrieved listening guidelines and calm audio targets to recommend lower-energy, more acoustic songs such as `Library Rain`, `Porchlight Tales`, and `Spacewalk Thoughts`.

### Reliability Demo

After showing `src.main`, I would run the evaluation harness:

```bash
python -m src.evaluate
```

This script runs predefined test cases and checks whether the system returns expected songs, meets minimum confidence thresholds, and activates guardrails when required. The current result is:

```text
Summary: 4/4 checks passed
```

This matters because the project does not only show outputs that look good manually. It includes a repeatable evaluation script that can be rerun after changes to confirm that core behavior still works.

Finally, I would run the automated tests:

```bash
pytest -q
```

The current result is:

```text
4 passed
```

These tests verify the original scoring logic, explanation generation, RAG context retrieval, and the guardrail case for a conflicting sleep/intense request.

### Walkthrough Commands

```bash
python -m src.main
python -m src.evaluate
pytest -q
```

Together, these commands demonstrate the complete applied AI system: natural-language input, retrieval, profile inference, guardrails, explainable recommendations, confidence scoring, and reliability testing.
