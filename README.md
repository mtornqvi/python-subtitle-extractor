# python-subtitle-extractor

Extract the first embedded subtitle track from an MP4 file and save it as an
SRT file, preserving its timing. This extracts existing subtitles; it does not
transcribe speech.

## Requirements

- Python 3.10 or later
- FFmpeg, with both `ffmpeg` and `ffprobe` available on `PATH`

## Configure and run

Copy `.env.example` to `.env`, then set `INPUT_FILE` to the MP4 path. Optionally
set `OUTPUT_FILE` to choose the SRT destination. Absolute paths are supported;
relative paths are resolved from the project directory.

If `OUTPUT_FILE` is blank or omitted, the SRT is saved next to the input file
using its original filename (for example, `video.mp4` becomes `video.srt`).
Existing output files are not overwritten.

Run:

```powershell
python extract_subtitles.py
```

The extractor uses the first embedded subtitle stream. It reports an error if
the MP4 contains no embedded subtitles.