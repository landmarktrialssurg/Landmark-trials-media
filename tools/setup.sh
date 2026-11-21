#!/usr/bin/env bash
# Rebuild the Landmark Trials build kit in a fresh cloud workspace.
# Usage: bash tools/setup.sh   (run from the repo root, branch "tools")
set -e
pip install -q --break-system-packages kokoro-onnx soundfile pillow numpy
mkdir -p /home/claude/render/fonts /home/claude/tts ~/.claude/skills/ig-reel ~/.claude/skills/ig-caption
cp tools/fonts/*.ttf /home/claude/render/fonts/
cp tools/brand.py tools/reelkit.py tools/motion.py tools/carousel.py /home/claude/
cp tools/igskills/hookscore.py tools/igskills/hooks.json ~/.claude/skills/ig-reel/
cp tools/igskills/caption.py ~/.claude/skills/ig-caption/
R=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -s /home/claude/tts/kokoro.onnx ] || curl -sSL -o /home/claude/tts/kokoro.onnx $R/kokoro-v1.0.onnx
[ -s /home/claude/tts/voices.bin ] || curl -sSL -o /home/claude/tts/voices.bin $R/voices-v1.0.bin
ffmpeg -hide_banner -filters 2>/dev/null | grep -q rubberband || echo "WARN: ffmpeg lacks rubberband (needed by render_human)"
python3 -c "import sys; sys.path.insert(0,'/home/claude'); import reelkit; print('ok', reelkit.phonemes('cholangitis'))"
