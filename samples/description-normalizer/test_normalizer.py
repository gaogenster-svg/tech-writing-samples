import unittest
from normalizer import normalize_content, normalize_summary, limit_at_boundary


class NormalizerTests(unittest.TestCase):
    def test_summary_excludes_leading_metadata_but_full_text_retains_it(self):
        value = '**Position:** Deckhand\n**Location:** Spain\nDeckhand required.'
        self.assertEqual(normalize_summary(value), 'Deckhand required.')
        self.assertIn('Position: Deckhand', normalize_content(value))

    def test_encoded_script_body_is_removed(self):
        self.assertEqual(normalize_content('&lt;script&gt;bad()&lt;/script&gt;<p>Role.</p>'), 'Role.')

    def test_input_is_optional_and_line_endings_are_normalized(self):
        self.assertEqual(normalize_content(None), '')
        self.assertEqual(normalize_content('First.\r\nSecond.'), 'First.\nSecond.')

    def test_sentence_boundary_and_fallback_are_explicit(self):
        self.assertEqual(limit_at_boundary('One two three four five', 10), 'One two...')
        self.assertEqual(limit_at_boundary('x' * 30, 10), '...')

    def test_documented_data_loss_is_visible(self):
        self.assertEqual(normalize_summary('engine_room'), 'engineroom')
        self.assertEqual(normalize_summary('Our cookie policy covers allergies.'), '')


if __name__ == '__main__':
    unittest.main()
