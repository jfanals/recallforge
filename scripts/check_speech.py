#!/usr/bin/env python3
"""Optional local ASR back-check. Agreement is NOT a pronunciation certificate."""
import argparse
import difflib
import json
import re
import subprocess
from pathlib import Path


def normalize(text):
    text = text.lower().replace('’', "'")
    for a, b in [("i'm", 'i am'), ("didn't", 'did not'), ("you're", 'you are'),
                 ("i'll", 'i will'), ("can't", 'cannot')]:
        text = text.replace(a, b)
    return re.findall(r'\w+', text)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('output', type=Path)
    p.add_argument('--model-dir', type=Path, help='Optional pre-provisioned ONNX model directory')
    p.add_argument('--model', default='nemo-parakeet-tdt-0.6b-v3')
    p.add_argument('--quantization', choices=['int8'])
    p.add_argument('--languages', nargs='+', default=['en-US', 'pt-BR'])
    a = p.parse_args()
    import numpy as np
    import onnx_asr
    options = {'providers': ['CPUExecutionProvider']}
    if a.quantization:
        options['quantization'] = a.quantization
    if a.model_dir:
        model = onnx_asr.load_model(a.model, str(a.model_dir), **options)
    else:
        model = onnx_asr.load_model(a.model, **options)
    timeline = json.loads((a.output / 'timeline.json').read_text())
    seen, rows, skipped = set(), [], []
    for s in timeline['segments']:
        if s['clip'] in seen or s['language'] not in a.languages:
            continue
        seen.add(s['clip'])
        if s['speech_duration_seconds'] > 20:
            skipped.append({'clip': s['clip'], 'reason': 'over 20s; split narration or use VAD'})
            continue
        clip = (a.output / s['clip']).resolve()
        if not clip.is_relative_to(a.output.resolve()):
            raise ValueError('Clip escapes output bundle')
        raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(clip),
                                       '-ar', '16000', '-ac', '1', '-f', 'f32le', '-'])
        recognized = model.recognize(np.frombuffer(raw, dtype=np.float32).copy(), sample_rate=16000)
        score = difflib.SequenceMatcher(None, normalize(s['text']), normalize(recognized)).ratio()
        rows.append({'clip': s['clip'], 'language': s['language'], 'expected': s['text'],
                     'recognized': recognized, 'token_sequence_agreement': score,
                     'review_candidate': score < .9})
        print(f'{score:.2f} {s["text"]} => {recognized}', flush=True)
    report = {'model': a.model, 'checked_clips': len(rows), 'skipped': skipped, 'results': rows,
              'limitation': 'ASR can overlook extra sounds or misrecognize correct speech. Human review required.'}
    (a.output / 'speech-check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
