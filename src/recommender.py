import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

_NUMERIC_FIELDS = ("energy", "tempo_bpm", "valence", "danceability", "acousticness", "popularity", "instrumentalness")

# Strategy pattern: each mode is a named weight preset. score_song()/Recommender._score()
# look up a preset by name instead of branching on if/elif, so adding a new mode is just
# adding a new dict entry.
BALANCED_WEIGHTS = {"genre": 2.0, "mood": 1.0, "energy": 1.0}
SCORING_MODES: Dict[str, Dict[str, float]] = {
    "balanced": BALANCED_WEIGHTS,
    "genre-first": {"genre": 3.0, "mood": 0.5, "energy": 1.0},
    "mood-first": {"genre": 1.0, "mood": 2.5, "energy": 1.0},
    "energy-focused": {"genre": 1.0, "mood": 0.5, "energy": 2.5},
}

DIVERSITY_ARTIST_PENALTY = 1.5
DIVERSITY_GENRE_PENALTY = 0.75
MAX_SAME_GENRE_BEFORE_PENALTY = 2

def _score_attributes(
    genre_match: bool,
    mood_match: bool,
    energy_diff: float,
    acoustic_bonus: float = 0.0,
    weights: Optional[Dict[str, float]] = None,
    popularity_diff: Optional[float] = None,
    decade_match: Optional[bool] = None,
    mood_tag_overlap: int = 0,
    instrumentalness_diff: Optional[float] = None,
    language_match: Optional[bool] = None,
) -> Tuple[float, List[str]]:
    """Shared point-weighted scoring recipe used by both the OOP and functional paths."""
    weights = weights or BALANCED_WEIGHTS
    score = 0.0
    reasons = []
    if genre_match:
        score += weights["genre"]
        reasons.append(f"genre match (+{weights['genre']:.1f})")
    if mood_match:
        score += weights["mood"]
        reasons.append(f"mood match (+{weights['mood']:.1f})")
    energy_points = (1 - energy_diff) * weights["energy"]
    score += energy_points
    reasons.append(f"energy similarity (+{energy_points:.2f})")
    if acoustic_bonus:
        score += acoustic_bonus
        reasons.append(f"acoustic bonus (+{acoustic_bonus:.2f})")
    if popularity_diff is not None:
        points = (1 - popularity_diff) * 0.5
        score += points
        reasons.append(f"popularity similarity (+{points:.2f})")
    if decade_match:
        score += 0.5
        reasons.append("release decade match (+0.5)")
    if mood_tag_overlap:
        points = 0.5 * mood_tag_overlap
        score += points
        reasons.append(f"mood tag overlap x{mood_tag_overlap} (+{points:.2f})")
    if instrumentalness_diff is not None:
        points = (1 - instrumentalness_diff) * 0.5
        score += points
        reasons.append(f"instrumentalness similarity (+{points:.2f})")
    if language_match:
        score += 0.5
        reasons.append("language match (+0.5)")
    return score, reasons

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
    popularity: float = 50.0
    release_decade: str = "unknown"
    detailed_mood_tags: str = ""
    instrumentalness: float = 0.0
    language: str = "unknown"

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
    target_popularity: Optional[float] = None
    preferred_decade: Optional[str] = None
    mood_tags: Optional[List[str]] = None
    preferred_instrumentalness: Optional[float] = None
    preferred_language: Optional[str] = None

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song, mode: str = "balanced") -> Tuple[float, List[str]]:
        """Applies the Algorithm Recipe to one Song/UserProfile pair."""
        acoustic_bonus = 0.5 if user.likes_acoustic and song.acousticness >= 0.6 else 0.0
        return _score_attributes(
            genre_match=song.genre == user.favorite_genre,
            mood_match=song.mood == user.favorite_mood,
            energy_diff=abs(song.energy - user.target_energy),
            acoustic_bonus=acoustic_bonus,
            weights=SCORING_MODES.get(mode, BALANCED_WEIGHTS),
            popularity_diff=abs(song.popularity - user.target_popularity) / 100
            if user.target_popularity is not None else None,
            decade_match=(song.release_decade == user.preferred_decade) if user.preferred_decade else None,
            mood_tag_overlap=len(set(song.detailed_mood_tags.split(";")) & set(user.mood_tags))
            if user.mood_tags else 0,
            instrumentalness_diff=abs(song.instrumentalness - user.preferred_instrumentalness)
            if user.preferred_instrumentalness is not None else None,
            language_match=(song.language == user.preferred_language) if user.preferred_language else None,
        )

    def recommend(self, user: UserProfile, k: int = 5, mode: str = "balanced") -> List[Song]:
        """Returns the top k songs for user, ranked highest score first."""
        scored = [(song, self._score(user, song, mode)[0]) for song in self.songs]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song, mode: str = "balanced") -> str:
        """Returns a human-readable reason string for why song scored the way it did."""
        _, reasons = self._score(user, song, mode)
        return ", ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        songs = list(csv.DictReader(f))
    for song in songs:
        song["id"] = int(song["id"])
        for field_name in _NUMERIC_FIELDS:
            song[field_name] = float(song[field_name])
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(
    user_prefs: Dict, song: Dict, weights: Optional[Dict[str, float]] = None
) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    return _score_attributes(
        genre_match=song["genre"] == user_prefs.get("genre"),
        mood_match=song["mood"] == user_prefs.get("mood"),
        energy_diff=abs(song["energy"] - user_prefs.get("energy", 0.0)),
        weights=weights,
        popularity_diff=abs(song["popularity"] - user_prefs["target_popularity"]) / 100
        if "target_popularity" in user_prefs else None,
        decade_match=song["release_decade"] == user_prefs["preferred_decade"]
        if "preferred_decade" in user_prefs else None,
        mood_tag_overlap=len(set(song["detailed_mood_tags"].split(";")) & set(user_prefs["mood_tags"]))
        if "mood_tags" in user_prefs else 0,
        instrumentalness_diff=abs(song["instrumentalness"] - user_prefs["preferred_instrumentalness"])
        if "preferred_instrumentalness" in user_prefs else None,
        language_match=song["language"] == user_prefs["preferred_language"]
        if "preferred_language" in user_prefs else None,
    )

def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5, mode: str = "balanced"
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Ranks by score, then greedily re-ranks for artist/genre diversity.
    Required by src/main.py
    """
    weights = SCORING_MODES.get(mode, BALANCED_WEIGHTS)
    candidates = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, weights)
        candidates.append({"song": song, "base_score": score, "reasons": reasons})

    selected: List[Tuple[Dict, float, str]] = []
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}
    remaining = candidates
    while remaining and len(selected) < k:
        for c in remaining:
            artist = c["song"]["artist"]
            genre = c["song"]["genre"]
            penalty = 0.0
            penalty_reasons = []
            if artist_counts.get(artist, 0) >= 1:
                penalty += DIVERSITY_ARTIST_PENALTY
                penalty_reasons.append(f"same-artist diversity penalty (-{DIVERSITY_ARTIST_PENALTY:.2f})")
            if genre_counts.get(genre, 0) >= MAX_SAME_GENRE_BEFORE_PENALTY:
                penalty += DIVERSITY_GENRE_PENALTY
                penalty_reasons.append(f"same-genre diversity penalty (-{DIVERSITY_GENRE_PENALTY:.2f})")
            c["adjusted_score"] = c["base_score"] - penalty
            c["penalty_reasons"] = penalty_reasons
        remaining.sort(key=lambda c: c["adjusted_score"], reverse=True)
        best = remaining.pop(0)
        explanation = ", ".join(best["reasons"] + best["penalty_reasons"])
        selected.append((best["song"], best["adjusted_score"], explanation))
        artist = best["song"]["artist"]
        genre = best["song"]["genre"]
        artist_counts[artist] = artist_counts.get(artist, 0) + 1
        genre_counts[genre] = genre_counts.get(genre, 0) + 1

    return selected
