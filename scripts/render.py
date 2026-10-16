#!/usr/bin/env python3
"""Local Kokoro -> cached utterances -> explicit silence -> WAV/MP3/chaptered M4A."""
import argparse
import importlib.metadata
import json
import shutil
import subprocess
from pathlib import Path

from lesson import LANGUAGES, MODEL, RATE, REVISION, cache_key, default_speed, load, row_for


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def safe_edges(audio):
    import numpy as np
    if audio.ndim != 1 or not len(audio) or not np.isfinite(audio).all():
        raise ValueError('TTS returned invalid waveform')
    active = np.flatnonzero(np.abs(audio) > .001)
    if not len(active):
        raise ValueError('TTS returned silence')
    audio = audio[max(0, active[0] - round(.08 * RATE)):
                  min(len(audio), active[-1] + round(.20 * RATE) + 1)].copy()
    n = min(round(.005 * RATE), len(audio) // 2)
    if n:
        audio[:n] *= np.linspace(0, 1, n, dtype=np.float32)
        audio[-n:] *= np.linspace(1, 0, n, dtype=np.float32)
    return audio


def metadata_escape(text):
    for a, b in [('\\', '\\\\'), ('=', '\\='), (';', '\\;'), ('#', '\\#')]:
        text = text.replace(a, b)
    return text.replace('\r', ' ').replace('\n', ' ')


def timestamp(seconds):
    return f'{int(seconds)//60:02}:{int(seconds)%60:02}'


def encode(out, lesson, timeline):
    chapters = []
    for row in timeline:
        if not chapters or chapters[-1]['title'] != row['chapter']:
            chapters.append({'title': row['chapter'], 'start_seconds': row['start_seconds'],
                             'end_seconds': row['end_seconds']})
        else:
            chapters[-1]['end_seconds'] = row['end_seconds']
    lines = [';FFMETADATA1', 'title=' + metadata_escape(lesson['title'])]
    for c in chapters:
        lines += ['[CHAPTER]', 'TIMEBASE=1/1000', f'START={round(c["start_seconds"]*1000)}',
                  f'END={round(c["end_seconds"]*1000)}', 'title=' + metadata_escape(c['title'])]
    meta = out / 'chapters.ffmetadata'
    meta.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    common = ['-af', 'loudnorm=I=-18:TP=-2:LRA=11', '-ar', str(RATE)]
    for ext, codec in [('mp3', 'libmp3lame'), ('m4a', 'aac')]:
        cmd = ['ffmpeg', '-y', '-v', 'error', '-i', str(out / 'lesson.wav')]
        if ext == 'm4a':
            cmd += ['-i', str(meta), '-map_metadata', '1', '-map_chapters', '1']
        else:
            cmd += ['-metadata', 'title=' + lesson['title']]
        subprocess.run(cmd + common + ['-codec:a', codec, '-b:a', '128k', str(out / f'lesson.{ext}')], check=True)
    probes = {}
    total = timeline[-1]['end_seconds']
    for ext, codec in [('mp3', 'mp3'), ('m4a', 'aac')]:
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format',
            '-show_streams', '-show_chapters', '-of', 'json', str(out / f'lesson.{ext}')], text=True))
        if abs(float(probe['format']['duration']) - total) > .3:
            raise ValueError(f'{ext}: encoded duration mismatch')
        audio = [s for s in probe['streams'] if s['codec_type'] == 'audio']
        if len(audio) != 1 or audio[0]['codec_name'] != codec:
            raise ValueError(f'{ext}: codec mismatch')
        if ext == 'm4a' and len(probe['chapters']) != len(chapters):
            raise ValueError('M4A chapter count mismatch')
        probes[ext] = {'codec': codec, 'duration_seconds': float(probe['format']['duration'])}
    return chapters, probes


def render(lesson_path, out, cache):
    lesson = load(lesson_path)
    for binary in ('ffmpeg', 'ffprobe'):
        if not shutil.which(binary):
            raise RuntimeError(f'Install {binary} first; see docs/setup.md')
    import numpy as np
    import soundfile as sf
    import torch
    from kokoro import KPipeline
    versions = {name: importlib.metadata.version(name) for name in ('kokoro', 'misaki', 'torch', 'numpy', 'soundfile')}
    torch.set_num_threads(4)
    # Refuse mixing partial revisions; choose a new output folder on each revision.
    if out.exists() and any(out.iterdir()):
        raise ValueError('Output folder is nonempty. Choose a new --output directory.')
    out.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    clips = out / 'clips'
    clips.mkdir()
    pipelines, timeline = {}, []
    cursor = 0
    peak = 0.0
    # Stream assembly instead of retaining an entire course in RAM.
    with sf.SoundFile(out / 'lesson.wav', mode='w', samplerate=RATE, channels=1, subtype='PCM_16') as combined:
        for i, s in enumerate(lesson['segments']):
            key = cache_key(s, versions)
            cached = cache / f'{key}.wav'
            if not cached.exists():
                lang = LANGUAGES[s['language']]
                if lang not in pipelines:
                    pipelines[lang] = KPipeline(lang_code=lang, repo_id=MODEL,
                        model=next(iter(pipelines.values())).model if pipelines else True)
                parts = [np.asarray(a, dtype=np.float32) for _, _, a in pipelines[lang](
                    s['text'], voice=s['voice'], speed=s.get('speed', default_speed(s)))]
                if not parts:
                    raise ValueError(f'{s["id"]}: no generated audio')
                audio = safe_edges(np.concatenate(parts))
                # Atomic replacement avoids reusing an interrupted synthesis cache.
                temp = cached.with_suffix('.tmp.wav')
                sf.write(temp, audio, RATE, subtype='PCM_16')
                temp.replace(cached)
            audio, sr = sf.read(cached, dtype='float32')
            if (sr != RATE or audio.ndim != 1 or len(audio) == 0
                    or not np.isfinite(audio).all() or np.max(np.abs(audio)) < .01):
                raise ValueError(f'Invalid cached clip: {cached}')
            peak = max(peak, float(np.max(np.abs(audio))))
            relative = f'clips/{key}.wav'
            if not (out / relative).exists():
                shutil.copyfile(cached, out / relative)
            row = row_for(s, cursor, len(audio), relative)
            timeline.append(row)
            combined.write(audio)
            combined.write(np.zeros(row['gap_samples'], dtype=np.float32))
            cursor = row['end_sample']
            print(f'{i+1}/{len(lesson["segments"])} {s["id"]}: {timestamp(cursor/RATE)}', flush=True)
    chapters, probes = encode(out, lesson, timeline)
    write_json(out / 'lesson.json', lesson)
    write_json(out / 'timeline.json', {'sample_rate_hz': RATE, 'duration_seconds': cursor / RATE,
                                     'chapters': chapters, 'segments': timeline})
    script = ['# ' + lesson['title'], '', 'Practice audio-first; read after attempting.', '']
    previous = None
    for r in timeline:
        if r['chapter'] != previous:
            script += ['## ' + r['chapter'], '']
            previous = r['chapter']
        script += [f'**{timestamp(r["start_seconds"])} [{r["language"]}]** {r["text"]}',
                   f'\n*Pause: {r["gap_after_seconds"]:g} seconds ({r["kind"]}).*', '']
    (out / 'script.md').write_text('\n'.join(script), encoding='utf-8')
    write_json(out / 'render-report.json', {'duration_seconds': cursor / RATE,
        'explicit_gap_seconds': sum(r['gap_samples'] for r in timeline) / RATE,
        'speech_seconds': sum(r['speech_samples'] for r in timeline) / RATE,
        'segments': len(timeline), 'unique_clips': len(list(clips.glob('*.wav'))),
        'chapters': len(chapters), 'model': MODEL, 'dependencies': versions,
        'edge_processing': REVISION, 'sample_rate_hz': RATE, 'raw_peak': peak,
        'encoded_verification': probes, 'human_listening_review': False})
    print(f'Created {out}; human listening review still required.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('lesson', type=Path)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--cache', type=Path, default=Path('build/clips'))
    a = p.parse_args()
    render(a.lesson, a.output, a.cache)
