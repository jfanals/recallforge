"""Shared, dependency-free lesson validation and sample-accurate planning."""
import hashlib
import json
import math
from pathlib import Path

RATE = 24000
LANGUAGES = {'en-US': 'a', 'en-GB': 'b', 'es': 'e', 'fr-FR': 'f',
             'hi': 'h', 'it': 'i', 'ja': 'j', 'pt-BR': 'p', 'zh-CN': 'z'}
KINDS = {'instruction', 'dialogue', 'model', 'repeat_model', 'confirmation',
         'recall_prompt', 'assessment_prompt', 'free_response_prompt'}
REVISION = 'safe-edges-v2'
MODEL = 'hexgrad/Kokoro-82M'


def number(value, low, high):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and low <= value <= high)


def validate(lesson):
    """Raise ValueError before model loading or output creation."""
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    require(isinstance(lesson, dict), 'lesson must be an object')
    for key in ('title', 'source', 'narrator_language', 'target_language'):
        require(isinstance(lesson.get(key), str) and bool(lesson[key].strip()), f'missing {key}')
    for key in ('narrator_language', 'target_language'):
        require(lesson[key] in LANGUAGES, f'unsupported {key}: {lesson[key]}')
    segments = lesson.get('segments')
    require(isinstance(segments, list) and bool(segments), 'segments must be a nonempty list')
    seen, closed, previous = set(), set(), None
    for i, s in enumerate(segments):
        require(isinstance(s, dict), f'segment {i} must be an object')
        for key in ('id', 'chapter', 'text', 'voice', 'language', 'kind'):
            require(isinstance(s.get(key), str) and bool(s[key].strip()), f'segment {i}: missing {key}')
        require(s['id'] not in seen, f'duplicate id: {s["id"]}')
        seen.add(s['id'])
        require(s['kind'] in KINDS, f'{s["id"]}: unsupported kind')
        require(s['language'] in LANGUAGES, f'{s["id"]}: unsupported language')
        require(s['voice'].startswith(LANGUAGES[s['language']]), f'{s["id"]}: voice/language mismatch')
        require(number(s.get('gap_after_seconds'), 0, 120), f'{s["id"]}: gap must be 0..120 seconds')
        require(number(s.get('speed', default_speed(s)), .5, 2), f'{s["id"]}: speed must be 0.5..2')
        require(len(s['text']) <= 1000, f'{s["id"]}: split long narration into short utterances')
        if s['kind'] in ('recall_prompt', 'assessment_prompt'):
            require(isinstance(s.get('expected_answer'), str) and bool(s['expected_answer'].strip()),
                    f'{s["id"]}: expected_answer required')
            require(i + 1 < len(segments) and segments[i + 1].get('kind') == 'confirmation',
                    f'{s["id"]}: next segment must be a confirmation')
        if 'acceptable_variants' in s:
            require(isinstance(s['acceptable_variants'], list)
                    and all(isinstance(v, str) and v.strip() for v in s['acceptable_variants']),
                    f'{s["id"]}: invalid acceptable_variants')
        if s['chapter'] != previous:
            require(s['chapter'] not in closed, f'{s["id"]}: chapters must be contiguous')
            if previous is not None:
                closed.add(previous)
            previous = s['chapter']
    return lesson


def default_speed(segment):
    return .95 if segment['language'] in ('en-US', 'en-GB') else 1.0


def cache_key(s, versions):
    payload = [MODEL, LANGUAGES[s['language']], s['voice'], s['text'],
               s.get('speed', default_speed(s)), REVISION, versions]
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:24]


def load(path):
    return validate(json.loads(Path(path).read_text(encoding='utf-8')))


def row_for(segment, start_sample, speech_samples, clip):
    gap_samples = round(segment['gap_after_seconds'] * RATE)
    end = start_sample + speech_samples + gap_samples
    return segment | {'start_sample': start_sample, 'speech_samples': speech_samples,
                      'gap_samples': gap_samples, 'end_sample': end,
                      'start_seconds': start_sample / RATE,
                      'speech_end_seconds': (start_sample + speech_samples) / RATE,
                      'end_seconds': end / RATE, 'speech_duration_seconds': speech_samples / RATE,
                      'clip': clip}


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='Validate lesson without loading speech models')
    p.add_argument('lesson', type=Path)
    args = p.parse_args()
    lesson = load(args.lesson)
    print(f'Valid: {lesson["title"]}; {len(lesson["segments"])} segments; '
          f'{sum(s["gap_after_seconds"] for s in lesson["segments"]):g}s explicit pauses')
