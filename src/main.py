"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import sys
from src.recommender import load_songs, recommend_songs, SCORING_MODES


def _format_table(rows) -> str:
    """Renders (title, score, reasons) rows as a plain ASCII table."""
    headers = ("Title", "Score", "Reasons")
    str_rows = [(title, f"{score:.2f}", reasons) for title, score, reasons in rows]
    widths = [max(len(headers[i]), *(len(r[i]) for r in str_rows)) if str_rows else len(headers[i])
              for i in range(3)]

    def fmt_row(cells):
        return " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    separator = "-+-".join("-" * w for w in widths)
    lines = [fmt_row(headers), separator]
    lines.extend(fmt_row(row) for row in str_rows)
    return "\n".join(lines)


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    # Pass a scoring mode as the first CLI arg, e.g.: python -m src.main mood-first
    mode = sys.argv[1] if len(sys.argv) > 1 else "balanced"
    if mode not in SCORING_MODES:
        print(f"Unknown mode '{mode}', falling back to 'balanced'. Options: {list(SCORING_MODES)}")
        mode = "balanced"

    recommendations = recommend_songs(user_prefs, songs, k=5, mode=mode)

    print(f"\nMode: {mode}\n")
    rows = [(song["title"], score, explanation) for song, score, explanation in recommendations]
    print(_format_table(rows))


if __name__ == "__main__":
    main()
