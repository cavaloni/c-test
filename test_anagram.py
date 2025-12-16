import unittest

import anagram


class TestAnagram(unittest.TestCase):
    def _pick_word(self, difficulty: int, predicate) -> str:
        anagram._init()
        words = anagram._BUCKET_WORDS[difficulty]
        for w in words:
            if predicate(w):
                return w
        self.fail(f"No word found for difficulty={difficulty} matching predicate")

    def _pick_signature(self, predicate) -> str:
        anagram._init()
        for sig, words in anagram._ANAGRAM_MAP.items():
            if predicate(sig, words):
                return sig
        self.fail("No anagram signature found matching predicate")

    def test_solve_known_anagram_has_solutions(self):
        # SOWPODS includes DOG and GOD.
        sols = anagram.solve("dgo")
        self.assertIn("dog", sols)
        self.assertIn("god", sols)

    def test_solve_returns_empty_for_unsolvable(self):
        # Use generator to ensure we pick something with zero solutions.
        p = anagram.generate_puzzle(difficulty=3, unsolvable=True)
        self.assertEqual(anagram.solve(p), [])

    def test_verify_true_for_valid_solution(self):
        sols = anagram.solve("dgo")
        self.assertTrue(anagram.verify("dgo", sols[0]))

    def test_verify_false_for_invalid_solution(self):
        self.assertFalse(anagram.verify("dgo", "cat"))

    def test_generate_puzzle_returns_string(self):
        p = anagram.generate_puzzle(difficulty=1)
        self.assertIsInstance(p, str)
        self.assertGreater(len(p), 0)

    def test_generate_puzzle_random_difficulty_when_none(self):
        # Not asserting distribution; just that it returns a plausible puzzle string.
        p = anagram.generate_puzzle()
        self.assertIsInstance(p, str)
        self.assertGreater(len(p), 0)

    def test_shuffle_not_identity_when_possible(self):
        # Directly test helper: for a word with at least 2 distinct letters,
        # we should never get the same word back.
        s = anagram._shuffle_not_identity("ab")
        self.assertNotEqual(s, "ab")
        self.assertCountEqual(list(s), list("ab"))

    def test_generate_solvable_has_at_least_one_solution(self):
        p = anagram.generate_puzzle(difficulty=2, unsolvable=False)
        self.assertGreaterEqual(len(anagram.solve(p)), 1)

    def test_generate_hard_solvable_is_longer_word(self):
        base = self._pick_word(5, lambda w: len(w) >= 8)
        puzzle = anagram._shuffle_not_identity(base)
        solutions = anagram.solve(puzzle)
        self.assertIn(base, solutions)
        self.assertEqual(len(puzzle), len(base))

    def test_generate_hard_unsolvable_has_no_solutions(self):
        puzzle = anagram.generate_puzzle(difficulty=5, unsolvable=True)
        self.assertEqual(anagram.solve(puzzle), [])

    def test_repeated_letter_word_still_solves(self):
        # Pick a word in the hardest bucket that has repeated letters.
        def has_repeat(w: str) -> bool:
            return len(set(w)) < len(w)

        base = self._pick_word(5, has_repeat)
        puzzle = anagram._shuffle_not_identity(base)
        self.assertIn(base, anagram.solve(puzzle))

    def test_multi_solution_signature_returns_multiple_words(self):
        sig = self._pick_signature(lambda _sig, words: len(words) >= 2)
        base = anagram._ANAGRAM_MAP[sig][0]
        puzzle = anagram._shuffle_not_identity(base)
        sols = anagram.solve(puzzle)
        self.assertGreaterEqual(len(sols), 2)

    def test_solve_raises_on_empty_input(self):
        with self.assertRaises(ValueError) as ctx:
            anagram.solve("")
        self.assertIn("empty", str(ctx.exception))

    def test_solve_raises_on_non_alpha_input(self):
        with self.assertRaises(ValueError) as ctx:
            anagram.solve("d-o-g")
        self.assertIn("alphabetic", str(ctx.exception))

    def test_verify_raises_on_empty_answer(self):
        with self.assertRaises(ValueError) as ctx:
            anagram.verify("dog", "")
        self.assertIn("empty", str(ctx.exception))

    def test_verify_raises_on_non_alpha_puzzle(self):
        with self.assertRaises(ValueError) as ctx:
            anagram.verify("dog!", "dog")
        self.assertIn("alphabetic", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
