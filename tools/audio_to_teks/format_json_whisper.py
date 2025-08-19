# @title 🔧 Format JSON Whisper (Direct List) agar Cocok untuk Translate

input_whisper_path = ""  # @param {type:"string"}
output_formatted_path = (
    "/content/formatted_for_translation.json"  # @param {type:"string"}
)

import json
import os

# Cek file
if not os.path.exists(input_whisper_path):
    raise FileNotFoundError(f"❌ File tidak ditemukan: {input_whisper_path}")

# Baca JSON
with open(input_whisper_path, "r", encoding="utf-8") as f:
    raw_segments = json.load(f)

# Validasi isi
if not isinstance(raw_segments, list):
    raise ValueError("❌ Format JSON tidak sesuai. Harus berupa list array.")

# Format ulang
formatted = []
for seg in raw_segments:
    if all(k in seg for k in ("text", "start", "end")):
        formatted.append(
            {
                "text": seg["text"].strip(),
                "start": float(seg["start"]),
                "end": float(seg["end"]),
            }
        )

# Simpan hasil
with open(output_formatted_path, "w", encoding="utf-8") as f:
    json.dump(formatted, f, ensure_ascii=False, indent=2)

print(f"✅ File berhasil diformat dan disimpan ke: {output_formatted_path}")
