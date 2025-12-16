from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path
from random import choice, shuffle

# Words file can be found here 
DICTIONARY_PATH = Path(__file__).resolve().parent / "sowpods.txt"

_VOWELS = set("aeiou")
_ANAGRAM_MAP: dict[str, list[str]] | None = None
_BUCKET_WORDS: dict[int, list[str]] | None = None
_MIN_LEN: int | None = None
_MAX_LEN: int | None = None


def _signature(s: str) -> str:
    return "".join(sorted(s))


def _load_words() -> list[str]:
    if not DICTIONARY_PATH.exists():
        raise FileNotFoundError(
            f"Required dictionary file not found: {DICTIONARY_PATH}. "
            "This module requires sowpods.txt to be present."
        )

    with DICTIONARY_PATH.open("r", encoding="utf-8") as f:
        words = []
        for line in f:
            w = line.strip()
            if not w:
                continue
            words.append(w.lower())
    if not words:
        raise ValueError(f"Dictionary file is empty: {DICTIONARY_PATH}")
    return words


def _difficulty_for_length(length: int) -> int:
    if _MIN_LEN is None or _MAX_LEN is None:
        raise RuntimeError("Dictionary not initialized")
    if _MAX_LEN == _MIN_LEN:
        return 3

    span = (_MAX_LEN - _MIN_LEN) + 1
    idx = ((length - _MIN_LEN) * 5) // span
    return max(1, min(5, int(idx) + 1))


def _init() -> None:
    global _ANAGRAM_MAP, _BUCKET_WORDS, _MIN_LEN, _MAX_LEN
    if _ANAGRAM_MAP is not None and _BUCKET_WORDS is not None:
        return

    words = _load_words()
    _MIN_LEN = min(len(w) for w in words)
    _MAX_LEN = max(len(w) for w in words)

    anagram_map: dict[str, list[str]] = defaultdict(list)
    bucket_words: dict[int, list[str]] = defaultdict(list)

    for w in words:
        sig = _signature(w)
        anagram_map[sig].append(w)

        d = _difficulty_for_length(len(w))
        bucket_words[d].append(w)

    for d in range(1, 6):
        if bucket_words.get(d):
            continue
        nearest = None
        for delta in (1, 2, 3, 4):
            if bucket_words.get(d - delta):
                nearest = d - delta
                break
            if bucket_words.get(d + delta):
                nearest = d + delta
                break
        if nearest is None:
            raise RuntimeError("No words available to create difficulty buckets")
        bucket_words[d] = bucket_words[nearest]

    _ANAGRAM_MAP = dict(anagram_map)
    _BUCKET_WORDS = dict(bucket_words)


def _validate_input(s: str, name: str) -> str:
    """Normalize and validate input: lowercase, stripped, alphabetic only."""
    normalized = s.strip().lower()
    if not normalized:
        raise ValueError(f"{name} cannot be empty")
    if not normalized.isalpha():
        raise ValueError(f"{name} must contain only alphabetic characters")
    return normalized


def solve(puzzle: str) -> list[str]:
    """Return all valid English words that are anagrams of the puzzle string.

    Args:
        puzzle: A string of letters to find anagrams for.

    Returns:
        A list of valid dictionary words that use exactly the same letters.
        Returns an empty list if no anagrams exist.

    Raises:
        ValueError: If puzzle is empty or contains non-alphabetic characters.
    """
    _init()
    assert _ANAGRAM_MAP is not None
    puzzle_norm = _validate_input(puzzle, "puzzle")
    sig = _signature(puzzle_norm)
    return list(_ANAGRAM_MAP.get(sig, []))


def verify(puzzle: str, answer: str) -> bool:
    """Check if an answer is a valid solution to the puzzle.

    Args:
        puzzle: The anagram puzzle string.
        answer: The proposed solution word.

    Returns:
        True if the answer is a valid anagram of the puzzle that exists
        in the dictionary; False otherwise.

    Raises:
        ValueError: If puzzle or answer is empty or contains non-alphabetic characters.
    """
    _init()
    assert _ANAGRAM_MAP is not None

    puzzle_norm = _validate_input(puzzle, "puzzle")
    answer_norm = _validate_input(answer, "answer")

    puzzle_sig = _signature(puzzle_norm)
    answer_sig = _signature(answer_norm)
    if puzzle_sig != answer_sig:
        return False

    return answer_norm in _ANAGRAM_MAP.get(puzzle_sig, [])


def generate_puzzle(difficulty: int | None = None, unsolvable: bool = False) -> str:
    """Generate an anagram puzzle of the specified difficulty.

    Args:
        difficulty: An integer from 1 (easiest/shortest) to 5 (hardest/longest).
            If None, a random difficulty is chosen.
        unsolvable: If True, generates a puzzle that has no valid solutions
            but still looks like a plausible word (uses minimal vowel swaps).

    Returns:
        A scrambled string of letters representing the puzzle.

    Raises:
        ValueError: If difficulty is not an integer from 1 to 5.
        RuntimeError: If an unsolvable puzzle cannot be generated for the
            given difficulty (e.g., all candidate mutations happen to be
            valid dictionary words).
    """
    _init()
    assert _BUCKET_WORDS is not None

    if difficulty is None:
        difficulty = choice((1, 2, 3, 4, 5))
    if difficulty not in (1, 2, 3, 4, 5):
        raise ValueError("difficulty must be an int from 1 to 5")

    words = _BUCKET_WORDS[difficulty]

    if not unsolvable:
        base = choice(words)
        return _shuffle_not_identity(base)

    return _generate_unsolvable_from_words(words)


def _shuffle_not_identity(word: str) -> str:
    """Shuffle letters to produce a different arrangement when possible.

    Note: For single-character words or words where all letters are identical
    (e.g., "aaa"), the output will equal the input since no different
    permutation exists.
    """
    letters = list(word)
    shuffle(letters)
    candidate = "".join(letters)
    if candidate != word:
        return candidate

    # Fallback: if random shuffle accidentally returned the original word,
    # force a swap of two distinct characters to ensure a valid puzzle.
    # We pick random indices to avoid deterministic patterns.
    n = len(letters)
    indices = list(range(n))
    shuffle(indices)

    for i in range(n - 1):
        idx1 = indices[i]
        for j in range(i + 1, n):
            idx2 = indices[j]
            if letters[idx1] != letters[idx2]:
                letters[idx1], letters[idx2] = letters[idx2], letters[idx1]
                return "".join(letters)
    return candidate


def _generate_unsolvable_from_words(words: list[str]) -> str:
    """Generate an unsolvable puzzle by mutating vowels in real words.

    Strategy: Filter to words containing vowels, shuffle them, then
    systematically try single-vowel mutations until we find one whose
    letter signature doesn't exist in the dictionary. This guarantees
    we try every candidate exactly once before giving up.
    """
    assert _ANAGRAM_MAP is not None

    words_with_vowels = [w for w in words if any(ch in _VOWELS for ch in w)]
    if not words_with_vowels:
        raise RuntimeError(
            "No words with vowels in this difficulty bucket; "
            "cannot generate unsolvable puzzle"
        )

    shuffled_words = words_with_vowels[:]
    shuffle(shuffled_words)

    for base in shuffled_words:
        for mutated in _single_vowel_mutations(base):
            sig = _signature(mutated)
            if sig not in _ANAGRAM_MAP:
                return _shuffle_not_identity(mutated)

    raise RuntimeError(
        "Failed to generate an unsolvable puzzle: all vowel mutations "
        "for this difficulty level are valid dictionary words"
    )


def _single_vowel_mutations(word: str) -> Iterator[str]:
    """Yield all single-vowel substitutions of the given word."""
    letters = list(word)
    vowel_positions = [i for i, ch in enumerate(letters) if ch in _VOWELS]
    for pos in vowel_positions:
        current = letters[pos]
        for v in "aeiou":
            if v == current:
                continue
            mutated_letters = letters[:]
            mutated_letters[pos] = v
            yield "".join(mutated_letters)


if __name__ == "__main__":
    print("Hello, anagram!")
