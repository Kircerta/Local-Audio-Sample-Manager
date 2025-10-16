import re
from pathlib import Path
import soundfile as sf

def parse_sample_info(filepath):
    p = Path(filepath)
    name = p.stem.lower()
    tokens = name.split("_")

    result = {
        "filename": p.name,
        "path": str(p),
        "type": None,
        "form": None,
        "bpm": None,
        "key": None,
        "time": None
    }

    type_keywords = ["kick", "snare", "clap", "hat", "bass", "fx", "perc", "vocal", "melody", "drum"]
    form_keywords = {"loop", "one_shot", "oneshot", "shot", "fill"}

    for token in tokens:
        if token in type_keywords and result["type"] is None:
            result["type"] = token
        if token in form_keywords and result["form"] is None:
            if "loop" in token:
                result["form"] = "loop"
            elif "fill" in token:
                result["form"] = "fill"
            else:
                result["form"] = "one-shot"
        bpm_match = re.match(r"(\d{2,3})bpm", token)
        if bpm_match:
            result["bpm"] = int(bpm_match.group(1))
        key_match = re.fullmatch(r"[a-g](#|b)?m?", token)
        if key_match:
            result["key"] = token.upper()

    try:
        with sf.SoundFile(str(filepath)) as f:
            result["time"] = round(len(f) / f.samplerate, 2)
    except Exception:
        result["time"] = 0

    return result

def scan_folder(folder_path):
    folder = Path(folder_path)
    all_wav_files = list(folder.rglob("*.wav"))
    parsed_results = []

    for f in all_wav_files:
        parsed = parse_sample_info(f.name)
        parsed["path"] = str(f)
        parsed_results.append(parsed)

    return parsed_results

def search_samples(samples, keywords, bpm_min, bpm_max, key, form):
    def matches(sample):
        name = sample["filename"].lower()
        if not all(k in name for k in keywords):
            return False

        bpm = sample["bpm"]
        if bpm_min is not None or bpm_max is not None:
            if bpm is None: return False
            if bpm_min is not None and bpm < bpm_min: return False
            if bpm_max is not None and bpm > bpm_max: return False

        if key:
            if sample["key"] is None or key.lower() not in sample["key"].lower():
                return False

        if form != "all" and sample["form"] != form:
            return False

        return True

    return [s for s in samples if matches(s)]
