#!/usr/bin/env bash
# Remux VLC-exported MP3-in-MP4 LC tracks to AAC-in-M4A for reliable <audio> playback.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
shopt -s nullglob
for mp4 in "$ROOT"/audio/*/*.mp4; do
  m4a="${mp4%.mp4}.m4a"
  if [[ -f "$m4a" ]]; then
    echo "skip (exists): $m4a"
    continue
  fi
  echo "convert: $mp4"
  ffmpeg -y -hide_banner -loglevel error -i "$mp4" \
    -c:a aac -b:a 128k -movflags +faststart "$m4a"
done
echo "done"
