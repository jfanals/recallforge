import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from lesson import RATE, cache_key, load, row_for, validate
from render import metadata_escape
from check_speech import normalize


class LessonTests(unittest.TestCase):
    def setUp(self):
        self.lesson = load(ROOT / 'examples/quickstart.json')

    def rejected(self, change):
        change(self.lesson)
        with self.assertRaises(ValueError):
            validate(self.lesson)

    def test_examples_validate(self):
        for path in (ROOT / 'examples').glob('*.json'):
            load(path)

    def test_duplicate_ids(self):
        self.rejected(lambda x: x['segments'][1].update(id='s001'))

    def test_language_voice_mismatch(self):
        self.rejected(lambda x: x['segments'][0].update(voice='af_bella'))

    def test_invalid_gaps(self):
        for gap in (-1, float('nan'), float('inf'), True, '6', 121):
            lesson = copy.deepcopy(self.lesson)
            lesson['segments'][0]['gap_after_seconds'] = gap
            with self.assertRaises(ValueError):
                validate(lesson)

    def test_invalid_speed(self):
        self.rejected(lambda x: x['segments'][0].update(speed=0))

    def test_unsupported_language(self):
        self.rejected(lambda x: x['segments'][0].update(language='xx'))

    def test_blank_text(self):
        self.rejected(lambda x: x['segments'][0].update(text='  '))

    def test_prompt_requires_answer(self):
        self.rejected(lambda x: x['segments'][6].pop('expected_answer'))

    def test_prompt_requires_confirmation(self):
        self.rejected(lambda x: x['segments'][7].update(kind='model'))

    def test_chapters_must_be_contiguous(self):
        self.rejected(lambda x: x['segments'][-1].update(chapter=x['segments'][0]['chapter']))

    def test_free_response_needs_no_fixed_answer(self):
        self.assertNotIn('expected_answer', self.lesson['segments'][-2])
        validate(self.lesson)

    def test_cache_ignores_gap_and_chapter(self):
        s = self.lesson['segments'][0]
        versions = {'kokoro': '0.9.4'}
        self.assertEqual(cache_key(s, versions), cache_key(s | {'gap_after_seconds': 9, 'chapter': 'new'}, versions))

    def test_cache_changes_for_voice_text_speed_versions(self):
        s = self.lesson['segments'][1]
        original = cache_key(s, {'kokoro': '0.9.4'})
        for changes in ({'voice': 'am_adam'}, {'text': 'New text.'}, {'speed': .9}, {'language': 'en-GB'}):
            self.assertNotEqual(original, cache_key(s | changes, {'kokoro': '0.9.4'}))
        self.assertNotEqual(original, cache_key(s, {'kokoro': 'other'}))

    def test_sample_timing_and_exact_gap(self):
        cursor = 0
        for i in range(1000):
            segment = self.lesson['segments'][i % len(self.lesson['segments'])]
            row = row_for(segment, cursor, 19001, 'clips/example.wav')
            self.assertEqual(row['start_sample'], cursor)
            self.assertEqual(row['gap_samples'], round(segment['gap_after_seconds'] * RATE))
            self.assertEqual(row['end_sample'], cursor + 19001 + row['gap_samples'])
            cursor = row['end_sample']
        self.assertEqual(row['end_seconds'], cursor / RATE)

    def test_metadata_escaping(self):
        self.assertEqual(metadata_escape('A=B;C#D\\E\nF'), 'A\\=B\\;C\\#D\\\\E F')

    def test_asr_normalization(self):
        self.assertEqual(normalize("I'm working."), normalize('I am working'))
        self.assertEqual(normalize("I didn’t record!"), normalize('I did not record.'))

    def test_skill_references_exist(self):
        skill = ROOT / '.agents/skills/recallforge/SKILL.md'
        import re
        for relative in re.findall(r'`(\.\./\.\./\.\./[^`]+)`', skill.read_text()):
            self.assertTrue((skill.parent / relative).exists(), relative)

    def test_original_studio_counts(self):
        studio = load(ROOT / 'examples/studio-pt-en.json')
        self.assertEqual(len(studio['segments']), 156)
        self.assertEqual(sum(s['kind'] == 'assessment_prompt' for s in studio['segments']), 9)
        self.assertEqual(sum(round(s['gap_after_seconds'] * RATE) for s in studio['segments']), 497 * RATE)


if __name__ == '__main__':
    unittest.main()
