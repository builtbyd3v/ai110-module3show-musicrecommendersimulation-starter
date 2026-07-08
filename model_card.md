# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0**

---

## 2. Intended Use  

VibeMatch takes a simple taste profile (a genre, a mood, and a target
energy level) and returns a ranked top-5 list of songs from a small
catalog, with a plain-English reason for each pick.

It assumes the user can describe their taste in exactly those three terms.
It does not learn from listening history, likes, or skips, and it does not
know anything about a user beyond what's typed in for that one request.

This is a classroom exploration project, not a product. It is not
intended for real users, real catalogs, or any use where a wrong or biased
recommendation would matter (for example, don't wire this into anything
that affects what content real people see without a human reviewing it
first).

---

## 3. How the Model Works  

Every song in the catalog gets a score, starting at 0. If the song's
genre matches what the user asked for, it gets 2 points. If the mood
matches, it gets 1 more point. Then, for energy, the closer the song's
energy is to the user's target energy, the more points it gets, up to 1
extra point for a near-perfect match. A song can also get a small bonus
if the user says they like acoustic music and the song is acoustic.

Genre is worth twice as much as mood on purpose. In testing, genre felt
like the stronger, more stable signal of the two.

Once every song has a score, the system sorts them from highest to
lowest and returns the top 5, along with the specific reasons ("genre
match," "mood match," "energy similarity") that added up to that score.

---

## 4. Data  

The catalog has 18 songs (10 in the starter file, 8 I added). Each song
has: title, artist, genre, mood, energy, tempo, valence, danceability,
and acousticness.

Genres: pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop,
classical, folk, metal, r&b, country, punk, electronic. Moods: happy,
chill, intense, relaxed, moody, focused, energetic, peaceful, nostalgic,
aggressive, dreamy, uplifting, rebellious, sad.

I only added songs, I didn't remove any starter data.

18 songs is tiny for how many genre/mood combinations exist. Most
genres only have 1 or 2 songs, so a lot of possible taste profiles have
no close match in the catalog at all. There's also nothing about the
actual audio (no lyrics, no real audio analysis) or about the artist
beyond a name, all attributes are hand-typed numbers.

---

## 5. Strengths  

When a user's stated genre and mood both exist in the catalog together
(pop/happy, lofi/chill, rock/intense), VibeMatch's top pick matched my
own intuition every time in testing, see the Evaluation section below.

The energy score works the way it's supposed to: it rewards closeness
to the target, not just "more energy is better," so a user who wants
calm music doesn't get handed the most intense song in the catalog.

It's also honest about its reasoning. Because every recommendation comes
with a plain-language "because" list, it's easy to see exactly why a
song ranked where it did, which made the bias in Section 6 easy to spot
in the first place.

---

## 6. Limitations and Bias 

The scoring recipe weights genre (+2.0) twice as heavily as mood (+1.0), so it systematically favors users whose stated genre exists in the 18-song catalog over users whose mood or vibe is the stronger signal. Testing an adversarial profile (`genre=metal, mood=sad, energy=0.9`) showed the system will confidently rank a high-energy, wrong-mood song above the one song that actually matches the user's stated mood, purely because genre points outweigh a mood-plus-energy combination. The system also has no way to flag an internally contradictory profile ("sad" with a 0.9 energy target); it just scores whatever it's given and returns a ranked list with no warning. Genres and moods not well represented in the 18-song catalog (there's one song per genre in several cases) will get thin, low-confidence recommendations even when a real match doesn't exist. Because this is content-based only, a user's actual taste, likes, skips, replays, is invisible to the system; it can only ever match the profile it's told, so it will happily reinforce whatever genre/mood the user already typed in rather than surfacing something outside that box.

---

## 7. Evaluation  

Tested four profiles against the 18-song catalog (full terminal output in the README's [Experiments You Tried](README.md#experiments-you-tried) section): **High-Energy Pop** (`genre=pop, mood=happy, energy=0.9`), **Chill Lofi** (`genre=lofi, mood=chill, energy=0.3`), **Deep Intense Rock** (`genre=rock, mood=intense, energy=0.9`), and an **adversarial** profile (`genre=metal, mood=sad, energy=0.9`) chosen specifically to contradict itself.

For each of the first three, I checked whether the top result matched my own intuition for that vibe. It did in all three cases: `Sunrise City` for pop/happy, `Library Rain` for lofi/chill, `Storm Runner` for rock/intense. Comparing High-Energy Pop and Chill Lofi shows what the system is actually testing for: the high-energy profile pulls upbeat, danceable tracks (`Sunrise City`, `Gym Hero`) while the low-energy profile pulls the opposite corner of the catalog (`Library Rain`, `Midnight Coding`), same scoring recipe, opposite result, because `energy` is the one numeric axis in the recipe and it's doing real work.

What surprised me was the adversarial profile: I expected the contradiction (metal/high-energy paired with mood "sad") to produce a messy or clearly-wrong top result, and it did, but not in the way I expected. `Iron Collapse` (aggressive metal) beat `Tears in Neon` (the only song actually tagged "sad") because 2.0 genre points plus a near-perfect energy match outscored the mood match. The system never notices the profile is self-contradictory; it just picks the highest scorer and moves on. I ran a follow-up weight-shift experiment (genre 2.0 to 1.0, energy points doubled) on this same adversarial profile and the result got worse, not better: `Tears in Neon` fell out of the top 5 entirely, replaced by songs matching nothing but raw energy. That confirmed the 2:1 genre-to-mood weighting, while it does over-favor genre, is doing more good than harm compared to the alternative I tried.

---

## 8. Future Work  

- Let the user weight genre vs. mood vs. energy themselves, instead of a
  fixed 2 / 1 / 1 recipe baked into the code.
- Flag contradictory profiles (like "sad" plus a high target energy)
  instead of silently scoring them and returning a confident-looking list.
- Grow the catalog so most genre/mood pairs actually have a real match,
  and cap how many songs from the same artist can appear in one top-5
  list so results don't feel repetitive.

---

## 9. Personal Reflection  

The biggest learning moment was the adversarial test in Phase 4. I
expected a contradictory profile to just look messy. Instead it revealed
a real, specific bias: genre quietly outweighs mood every time, and the
system never says so, it just hands back a confident ranked list either
way.

AI tools were fastest for turning a described scoring rule into working
code and for generating the CSV rows for new songs. I still had to
double-check the math by hand (running real profiles and reading the
score breakdowns) before trusting that "genre 2.0, mood 1.0, energy
closeness" behaved the way I expected, especially after the weight-shift
experiment, where the AI-suggested change looked reasonable on paper but
made results worse in practice.

What surprised me is how much a tiny, fully-explainable scoring formula
can still "feel" like a real recommendation, right up until you feed it
an edge case it wasn't built to handle. If I kept going, I'd want to test
many more adversarial profiles before trusting this kind of system with
anything beyond a classroom demo.
