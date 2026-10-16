"""Small synthetic-audio integration tests; no model download or TTS dependency."""
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from lesson import RATE, row_for
from render import encode, safe_edges
from audit import audit

AUDIO = all(importlib.util.find_spec(m) is not None for m in ('numpy', 'soundfile'))
BINARIES = bool(shutil.which('ffmpeg') and shutil.which('ffprobe'))


@unittest.skipUnless(AUDIO, 'optional numpy/soundfile not installed')
class AudioTests(unittest.TestCase):
    def test_edges_preserve_length_and_zero_boundaries(self):
        import numpy as np
        audio = np.ones(1000, dtype=np.float32) * .1
        result = safe_edges(audio)
        self.assertEqual(len(result), len(audio))
        self.assertEqual(result[0], 0)
        self.assertEqual(result[-1], 0)
        self.assertAlmostEqual(float(result[500]), .1)

    def test_silence_and_nonfinite_fail(self):
        import numpy as np
        for audio in (np.zeros(100), np.array([.1, np.nan]), np.array([])):
            with self.assertRaises(ValueError):
                safe_edges(audio)

    @unittest.skipUnless(BINARIES, 'ffmpeg/ffprobe not installed')
    def test_encode_and_audit_then_detect_corrupted_gap(self):
        import numpy as np
        import soundfile as sf
        lesson = json.loads((ROOT / 'examples/quickstart.json').read_text())
        lesson['segments'] = lesson['segments'][:2]
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            (out / 'clips').mkdir()
            sine = (.1 * np.sin(2 * np.pi * 440 * np.arange(4800) / RATE)).astype(np.float32)
            clip = out / 'clips/tone.wav'
            sf.write(clip, safe_edges(sine), RATE, subtype='PCM_16')
            audio, _ = sf.read(clip, dtype='float32')
            rows, chunks, cursor = [], [], 0
            for s in lesson['segments']:
                row = row_for(s, cursor, len(audio), 'clips/tone.wav')
                rows.append(row)
                chunks += [audio, np.zeros(row['gap_samples'], dtype=np.float32)]
                cursor = row['end_sample']
            combined = np.concatenate(chunks)
            sf.write(out / 'lesson.wav', combined, RATE, subtype='PCM_16')
            chapters, probes = encode(out, lesson, rows)
            self.assertEqual(len(chapters), 1)
            self.assertEqual(probes['mp3']['codec'], 'mp3')
            self.assertEqual(probes['m4a']['codec'], 'aac')
            (out / 'lesson.json').write_text(json.dumps(lesson))
            (out / 'timeline.json').write_text(json.dumps({'segments': rows}))
            self.assertTrue(audit(out))
            combined[rows[0]['speech_samples'] + 10] = .1
            sf.write(out / 'lesson.wav', combined, RATE, subtype='PCM_16')
            self.assertFalse(audit(out))


if __name__ == '__main__':
    unittest.main()
