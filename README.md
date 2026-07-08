# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real platforms like Spotify mostly blend two approaches. **Collaborative
filtering** predicts what you'll like from *other users'* behavior: likes,
skips, playlist co-occurrence, listening history, even without knowing
anything about the song itself. **Content-based filtering** predicts from
the *song's own* attributes: genre, mood, tempo, energy, matched against
a profile built from what you've liked before. Collaborative filtering finds
patterns humans wouldn't think to encode by hand, but needs a large user base
and struggles with new/unpopular songs ("cold start"). Content-based works
from day one with no other users, but stays inside your stated taste and
won't surprise you the way "people like you also liked X" can.

This simulation is **content-based only**: no other users, no play history,
just song attributes scored against one stated profile.

- `Song` features: `genre`, `mood`, `energy`, `tempo_bpm`, `valence`,
  `danceability`, `acousticness` (see `data/songs.csv`)
- `UserProfile` stores: `favorite_genre`, `favorite_mood`, `target_energy`,
  `likes_acoustic`
- **Scoring rule** (per song): exact match on `genre` and `mood` each add
  fixed points (genre weighted higher since it's a stronger taste signal
  than mood); `energy` is scored by closeness to `target_energy`
  (`1 - abs(song.energy - target_energy)`) rather than "higher is better",
  since a user wanting calm music shouldn't get the most intense song in the
  catalog; `acousticness` adds a small bonus only when `likes_acoustic` is
  true.
- **Ranking rule**: score every song, sort descending, return the top `k`.
  The scoring rule handles *one* song in isolation; the ranking rule turns
  many individual scores into an ordered list. You need both because a
  score alone doesn't tell you how a song compares to the rest of the
  catalog.

### Algorithm Recipe (finalized)

`user_prefs = {"genre": "lofi", "mood": "chill", "energy": 0.4}` is the
example profile used for planning and manual testing.

Per song, starting from 0 points:

- `+2.0` if `song.genre == user_prefs["genre"]`
- `+1.0` if `song.mood == user_prefs["mood"]`
- `+ (1 - abs(song.energy - user_prefs["energy"]))` similarity points for
  energy, so a near-exact energy match is worth close to `+1.0` and a
  wildly mismatched one is worth close to `0`

Genre outweighs mood 2:1 because in this catalog genre is the stronger,
more stable taste signal; mood shifts more from song to song within the
same artist.

**Data flow:** `Input (user_prefs dict)` &rarr; `Process (loop: score_song()
over every row in songs.csv)` &rarr; `Output (sort by score, return top k)`.

**Known bias:** this recipe over-prioritizes genre. A right-genre song that
matches nothing else scores 2.0. A wrong-genre song with a perfect mood
match and a near-perfect energy match tops out just under 2.0 (1.0 mood
plus almost 1.0 energy). So the wrong-genre song usually loses even when
it fits the user's mood and energy far better, unless its energy match is
close to exact.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` with the default profile
`{"genre": "pop", "mood": "happy", "energy": 0.8}`:

```
Loaded songs: 18

Top recommendations:

Sunrise City - Score: 3.98
Because: genre match (+2.0), mood match (+1.0), energy similarity (+0.98)

Gym Hero - Score: 2.87
Because: genre match (+2.0), energy similarity (+0.87)

Rooftop Lights - Score: 1.96
Because: mood match (+1.0), energy similarity (+0.96)

Concrete Bloom - Score: 1.00
Because: energy similarity (+1.00)

Night Drive Loop - Score: 0.95
Because: energy similarity (+0.95)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

### Stress test: four profiles

```
=== High-Energy Pop -> {'genre': 'pop', 'mood': 'happy', 'energy': 0.9} ===
Sunrise City - Score: 3.92
Because: genre match (+2.0), mood match (+1.0), energy similarity (+0.92)
Gym Hero - Score: 2.97
Because: genre match (+2.0), energy similarity (+0.97)
Rooftop Lights - Score: 1.86
Because: mood match (+1.0), energy similarity (+0.86)
Riot Fuel - Score: 1.00
Because: energy similarity (+1.00)
Storm Runner - Score: 0.99
Because: energy similarity (+0.99)

=== Chill Lofi -> {'genre': 'lofi', 'mood': 'chill', 'energy': 0.3} ===
Library Rain - Score: 3.95
Because: genre match (+2.0), mood match (+1.0), energy similarity (+0.95)
Midnight Coding - Score: 3.88
Because: genre match (+2.0), mood match (+1.0), energy similarity (+0.88)
Focus Flow - Score: 2.90
Because: genre match (+2.0), energy similarity (+0.90)
Spacewalk Thoughts - Score: 1.98
Because: mood match (+1.0), energy similarity (+0.98)
Tears in Neon - Score: 1.00
Because: energy similarity (+1.00)

=== Deep Intense Rock -> {'genre': 'rock', 'mood': 'intense', 'energy': 0.9} ===
Storm Runner - Score: 3.99
Because: genre match (+2.0), mood match (+1.0), energy similarity (+0.99)
Gym Hero - Score: 1.97
Because: mood match (+1.0), energy similarity (+0.97)
Riot Fuel - Score: 1.00
Because: energy similarity (+1.00)
Iron Collapse - Score: 0.93
Because: energy similarity (+0.93)
Sunrise City - Score: 0.92
Because: energy similarity (+0.92)

=== Adversarial (genre metal, mood sad, energy 0.9) -> {'genre': 'metal', 'mood': 'sad', 'energy': 0.9} ===
Iron Collapse - Score: 2.93
Because: genre match (+2.0), energy similarity (+0.93)
Tears in Neon - Score: 1.40
Because: mood match (+1.0), energy similarity (+0.40)
Riot Fuel - Score: 1.00
Because: energy similarity (+1.00)
Storm Runner - Score: 0.99
Because: energy similarity (+0.99)
Gym Hero - Score: 0.97
Because: energy similarity (+0.97)
```

The first three profiles "feel" right: each top result is exactly the genre/mood/energy combo it asked for (Sunrise City for happy pop, Library Rain for chill lofi, Storm Runner for intense rock). `Sunrise City` beats `Gym Hero` for the pop profile because genre+mood both match (+3.0) even though `Gym Hero` is closer on raw energy, matching genre and mood is worth more than a slightly tighter energy number.

The fourth profile is a contradiction on purpose: "metal" (usually high energy) paired with mood "sad" (usually low energy) and a high target energy. The system doesn't notice the contradiction, it just adds up points. `Iron Collapse` wins on genre plus energy while completely ignoring mood. `Tears in Neon`, the one song that actually matches the stated mood, drops to second because its energy (0.30) is far from the requested 0.9. A user who typed "sad" probably wanted `Tears in Neon`, not an aggressive metal track.

### Weight-shift experiment: genre 2.0 → 1.0, energy ×2

Same High-Energy Pop profile, ranking barely moved (still Sunrise City, Gym Hero, Rooftop Lights, Riot Fuel, Storm Runner in that order) with the top-3 gap much tighter, from 2.06 points down to 1.12.

The bigger effect showed up on the adversarial profile:

```
=== Adversarial (genre halved, energy doubled) ===
Iron Collapse - Score: 2.86
Because: genre match (+1.0), energy similarity (+1.86)
Riot Fuel - Score: 2.00
Because: energy similarity (+2.00)
Storm Runner - Score: 1.98
Because: energy similarity (+1.98)
Gym Hero - Score: 1.94
Because: energy similarity (+1.94)
Sunrise City - Score: 1.84
Because: energy similarity (+1.84)
```

`Tears in Neon`, the only song matching the requested mood, fell out of the top 5 entirely, replaced by four songs that match nothing but raw energy (not even genre). Doubling the energy weight didn't make this profile's results more accurate, it made them worse: the list is now just "loudest songs available" with taste signals drowned out. This change was reverted; the shipped system still uses genre 2.0 / mood 1.0 / energy ×1.

---

## Limitations and Risks

- 18-song catalog. There's no guarantee a good match for any given profile exists at all.
- Genre outweighs mood 2:1, so a wrong-genre song can lose to a right-genre song even when it fits the user's mood and energy far better (see the adversarial profile above).
- No contradiction detection. A profile like `genre=metal, mood=sad, energy=0.9` is internally inconsistent, but the scorer just adds points and returns a confident-looking ranked list anyway.
- Content-based only, no other users, no play history, no lyrics or audio analysis, no way to learn from skips or replays over time.

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



