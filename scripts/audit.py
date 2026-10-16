#!/usr/bin/env python3
"""Check portable render bundle integrity, silence windows, and waveform edges."""
import argparse
import json
from pathlib import Path

from lesson import RATE, load


def audit(output):
    import numpy as np
    import soundfile as sf
    lesson = load(output / 'lesson.json')
    timeline = json.loads((output / 'timeline.json').read_text())
    rows = timeline['segments']
    if len(rows) != len(lesson['segments']):
        raise ValueError('Lesson/timeline length mismatch')
    issues, seen, metrics = [], set(), []
    cursor = 0
    with sf.SoundFile(output / 'lesson.wav') as wav:
        if wav.samplerate != RATE or wav.channels != 1:
            issues.append('wrong WAV format')
        for original, row in zip(lesson['segments'], rows):
            if any(row.get(k) != v for k, v in original.items()):
                issues.append(f'{original["id"]}: author/render mismatch')
            if row['start_sample'] != cursor:
                issues.append(f'{row["id"]}: discontinuous timeline')
            gap = round(row['gap_after_seconds'] * RATE)
            if row['gap_samples'] != gap or row['end_sample'] != cursor + row['speech_samples'] + gap:
                issues.append(f'{row["id"]}: incorrect answer window')
            clip = (output / row['clip']).resolve()
            if not clip.is_relative_to(output.resolve()):
                raise ValueError('Clip escapes output bundle')
            audio, sr = sf.read(clip, dtype='float32')
            if sr != RATE or audio.ndim != 1 or len(audio) != row['speech_samples']:
                issues.append(f'{row["id"]}: invalid clip format/length')
            if not np.isfinite(audio).all() or not len(audio) or np.max(np.abs(audio)) < .01:
                issues.append(f'{row["id"]}: invalid or silent clip')
            wav.seek(cursor)
            assembled = wav.read(row['speech_samples'], dtype='float32')
            if not np.array_equal(assembled, audio):
                issues.append(f'{row["id"]}: assembled speech differs from clip')
            silence = wav.read(gap, dtype='float32')
            if len(silence) != gap or np.any(silence != 0):
                issues.append(f'{row["id"]}: missing or nonzero pause')
            if row['clip'] not in seen:
                seen.add(row['clip'])
                edge = max(abs(float(audio[0])), abs(float(audio[-1])))
                metrics.append({'clip': row['clip'], 'text': row['text'], 'edge_peak': edge})
                if edge > 1e-5:
                    issues.append(f'{row["id"]}: nonzero waveform edge')
            cursor = row['end_sample']
        if wav.frames != cursor:
            issues.append('WAV/timeline total mismatch')
    report = {'passed': not issues, 'issues': issues, 'unique_clips': len(seen), 'clips': metrics,
              'limitation': 'Integrity/edge checks only; not a perceptual pronunciation review.'}
    (output / 'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': not issues, 'issues': issues, 'unique_clips': len(seen)}, indent=2))
    return not issues


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('output', type=Path)
    raise SystemExit(0 if audit(p.parse_args().output) else 1)
