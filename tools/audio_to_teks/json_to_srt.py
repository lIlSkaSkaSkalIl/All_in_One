# @title 📝 Export to Subtitle (.srt)
# @markdown - Auto-split text to fit subtitle screen width

json_path = ""  # @param {type:"string"}
output_path = "/content/media_toolkit"  # @param {type:"string"}
max_chars_per_line = 100  # @param {type:"slider", min:40, max:120, step:5}

import os
import json
import textwrap
from datetime import timedelta


# ✅ Standardized logger
def log(message, level="INFO"):
    print(f"[{level}] {message}")


# ✅ Convert seconds to SRT time format
def seconds_to_srt_time(seconds: float) -> str:
    t = timedelta(seconds=seconds)
    total_seconds = int(t.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = int((t.total_seconds() - total_seconds) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


# ✅ Wrap text by character width
def wrap_text(text: str, width: int = 80) -> str:
    return "\n".join(textwrap.wrap(text, width=width))


# ✅ Export to .srt
def export_to_srt(
    json_path: str, max_chars_per_line: int = 80, output_path: str = ""
) -> str:
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"File not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        segments = json.load(f)

    log(f"Reading transcript from: {json_path}")
    log(f"Number of segments: {len(segments)}")

    srt_lines = []
    for idx, seg in enumerate(segments, 1):
        if not seg.get("text"):  # skip empty segments
            continue

        start = seconds_to_srt_time(seg["start"])
        end = seconds_to_srt_time(seg["end"])
        text = wrap_text(seg["text"].strip(), width=max_chars_per_line)

        srt_lines.append(f"{idx}")
        srt_lines.append(f"{start} --> {end}")
        srt_lines.append(text)
        srt_lines.append("")  # empty line between segments

    # ✅ Determine output path
    if not output_path.strip():
        output_path = "/content/media_toolkit/subtitles"
    os.makedirs(output_path, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(json_path))[0]
    srt_path = os.path.join(output_path, f"{base_name}.srt")

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))

    log("Subtitle successfully saved to:")
    log(srt_path, "SUCCESS")
    return srt_path


# ✅ Run export
export_to_srt(json_path, max_chars_per_line, output_path)
