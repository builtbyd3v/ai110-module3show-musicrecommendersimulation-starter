import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

_NUMERIC_FIELDS = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")

def _score_attributes(
    genre_match: bool, mood_match: bool, energy_diff: float, acoustic_bonus: float = 0.0
) -> Tuple[float, List[str]]:
    """Shared point-weighted scoring recipe used by both the OOP and functional paths."""
    score = 0.0
    reasons = []
    if genre_match:
        score += 2.0
        reasons.append("genre match (+2.0)")
    if mood_match:
        score += 1.0
        reasons.append("mood match (+1.0)")
    energy_points = 1 - energy_diff
    score += energy_points
    reasons.append(f"energy similarity (+{energy_points:.2f})")
    if acoustic_bonus:
        score += acoustic_bonus
        reasons.append(f"acoustic bonus (+{acoustic_bonus:.2f})")
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

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Applies the Algorithm Recipe to one Song/UserProfile pair."""
        acoustic_bonus = 0.5 if user.likes_acoustic and song.acousticness >= 0.6 else 0.0
        return _score_attributes(
            genre_match=song.genre == user.favorite_genre,
            mood_match=song.mood == user.favorite_mood,
            energy_diff=abs(song.energy - user.target_energy),
            acoustic_bonus=acoustic_bonus,
        )

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k songs for user, ranked highest score first."""
        scored = [(song, self._score(user, song)[0]) for song in self.songs]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable reason string for why song scored the way it did."""
        _, reasons = self._score(user, song)
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
        for field in _NUMERIC_FIELDS:
            song[field] = float(song[field])
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    return _score_attributes(
        genre_match=song["genre"] == user_prefs.get("genre"),
        mood_match=song["mood"] == user_prefs.get("mood"),
        energy_diff=abs(song["energy"] - user_prefs.get("energy", 0.0)),
    )

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, ", ".join(reasons)))
    scored.sort(key=lambda triple: triple[1], reverse=True)
    return scored[:k]
