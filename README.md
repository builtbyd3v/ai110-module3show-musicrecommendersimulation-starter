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

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



