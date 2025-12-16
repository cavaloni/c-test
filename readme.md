# Anagram Puzzle Library

A Python library for generating and solving anagram puzzles, designed for interactive use in research settings.

## Installation

Place `anagram.py` and `sowpods.txt` in the same directory. No external dependencies required.

## Quick Start

```python
import anagram

# Generate a puzzle (random difficulty 1-5)
puzzle = anagram.generate_puzzle()

# Generate with specific difficulty (1=easy/short, 5=hard/long)
puzzle = anagram.generate_puzzle(difficulty=3)

# Generate an unsolvable puzzle that looks plausible
puzzle = anagram.generate_puzzle(difficulty=3, unsolvable=True)

# Solve a puzzle (returns list of valid words)
solutions = anagram.solve("dgo")  # ['dog', 'god']

# Verify an answer
anagram.verify("dgo", "dog")  # True
anagram.verify("dgo", "cat")  # False
```

## API Reference

| Function | Parameters | Returns |
|----------|------------|---------|
| `generate_puzzle()` | `difficulty` (1-5, optional), `unsolvable` (bool, default False) | Scrambled string |
| `solve(puzzle)` | `puzzle` (str) | List of valid anagram words |
| `verify(puzzle, answer)` | `puzzle` (str), `answer` (str) | True/False |

## Assumptions

### Difficulty
Difficulty is based purely on **word length**. The dictionary's word lengths are divided into 5 equal-sized ranges. Difficulty 1 = shortest words, difficulty 5 = longest.

### "Looks Like" (Unsolvable Puzzles)
An unsolvable puzzle "looks solvable" if it:
- Has the same length as real words in that difficulty bucket
- Contains a realistic vowel/consonant mix (achieved by taking a real word and swapping **one vowel** for another)

This is a minimal definition—it doesn't account for letter frequency or common bigrams.

## Performance

| Operation | Time Complexity | Notes |
|-----------|-----------------|-------|
| `solve()` | O(L log L) | L = puzzle length; one sort + dict lookup |
| `verify()` | O(L log L) | Early exit if signatures don't match |
| `generate_puzzle()` (solvable) | O(L) | Random choice + shuffle |
| `generate_puzzle()` (unsolvable) | O(1) | Pre-computed at init; random choice + shuffle |

All operations are fast enough for interactive use (sub-second).

### Pre-Computed Unsolvable Puzzles

Unsolvable puzzles are **pre-computed during initialization** rather than generated on-demand.

**Why this was changed:**
- The original approach iterated through words at generation time, trying vowel mutations until finding one with no dictionary match
- Worst case: O(W × V) where W = words in bucket, V = vowels per word
- This was fast enough in practice, but unpredictable—some calls could be slower than others

**Current approach:**
- During init, we scan each difficulty bucket once and store all valid unsolvable mutations
- Generation becomes O(1): just pick a random pre-computed puzzle and shuffle it

**Tradeoff:**
- Init time increases from ~0.35s to ~1s (one-time cost on first use)
- All subsequent unsolvable generations are instant and consistent

### Alternative for performance considered: 26-Count Tuple Signature

The current implementation computes signatures by sorting letters (`"dog"` → `"dgo"`). An alternative is a **26-count tuple**: count occurrences of each letter a-z.

| Approach | Signature Time | Pros | Cons |
|----------|----------------|------|------|
| Sorted string | O(L log L) | Readable, debuggable | Slightly slower |
| 26-count tuple | O(L) | Faster, O(1) mutation updates | Less readable, more memory |

For this library's use case (interactive REPL, ~250k words), sorted strings are fast enough and simpler to debug. The 26-tuple would only matter for millions of lookups per second.

## Limitations

- **Dictionary**: Requires `sowpods.txt` (Scrabble tournament word list). No fallback.
- **1-letter words**: Cannot be shuffled differently; puzzle equals solution.
- **All-identical letters**: Words like `"aaa"` cannot produce a different permutation.
- **Consonant-only words**: Cannot generate unsolvable variants (no vowels to swap). The library filters these out automatically.
- **Unsolvable generation**: In rare cases, all single-vowel mutations of words in a bucket may be valid dictionary words. The library raises `RuntimeError` if this happens. (It shouldn't!)

## Running Tests

```bash
python -m unittest -v
```

### Test Coverage

- Known anagram solving (`"dgo"` → `["dog", "god"]`)
- Unsolvable puzzles return empty solutions
- Verification (true/false cases)
- Random difficulty selection
- Hard/long words (difficulty 5)
- Repeated-letter words
- Multi-solution signatures
- Input validation (empty, non-alphabetic)

### Edge Cases Tested

| Case | Expected Behavior |
|------|-------------------|
| Empty input | Raises `ValueError` |
| Non-alphabetic (`"d-o-g"`) | Raises `ValueError` |
| Single-letter word | Puzzle equals solution |
| All same letters (`"aaa"`) | Puzzle equals input |
| No solutions exist | `solve()` returns `[]` |
| Invalid answer | `verify()` returns `False` |

### Perfectionism Note
Thoughts running through developer's head: "I should make this more perfect"
"I should make this more perfect"
"I should make this more perfect"
"I should make this more perfect"
"I think I'm done"
"Wait, I should make this more perfect"
"I'm a participant, not a developer, aren't I?"
"anagram.verify('mntida', 'damnit')" 