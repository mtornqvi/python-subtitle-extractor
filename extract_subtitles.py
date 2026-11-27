import json
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
ENV_FILE = PROJECT_DIR / ".env"


def load_config(env_file: Path) -> tuple[Path, Path]:
    values = {}
    with env_file.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"{env_file}:{line_number}: expected KEY=VALUE")

            key, value = line.split("=", maxsplit=1)
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            values[key] = value

    input_value = values.get("INPUT_FILE", "").strip()
    if not input_value:
        raise ValueError(f"Set INPUT_FILE in {env_file}")

    input_path = Path(input_value)
    if not input_path.is_absolute():
        input_path = PROJECT_DIR / input_path
    input_path = input_path.resolve()

    output_value = values.get("OUTPUT_FILE", "").strip()
    if output_value:
        output_path = Path(output_value)
        if not output_path.is_absolute():
            output_path = PROJECT_DIR / output_path
        output_path = output_path.resolve()
    else:
        output_path = input_path.with_suffix(".srt")

    return input_path, output_path


def extract_subtitles(input_path: Path, output_path: Path) -> None:
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise RuntimeError("FFmpeg and ffprobe must both be installed and available on PATH")

    probe = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "s",
            "-show_entries",
            "stream=index",
            "-of",
            "json",
            str(input_path),
        ],
        capture_output=True,
        check=True,
        text=True,
    )
    streams = json.loads(probe.stdout).get("streams", [])
    if not streams:
        raise ValueError(f"No embedded subtitle stream found in {input_path}")

    try:
        subprocess.run(
            [
                ffmpeg,
                "-nostdin",
                "-n",
                "-i",
                str(input_path),
                "-map",
                "0:s:0",
                "-c:s",
                "srt",
                str(output_path),
            ],
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        details = error.stderr.strip() or str(error)
        raise RuntimeError(f"FFmpeg could not extract subtitles: {details}") from error

    if not output_path.is_file():
        raise RuntimeError(f"FFmpeg completed without creating {output_path}")

    print(f"Subtitles saved to: {output_path}")


def main() -> int:
    try:
        input_path, output_path = load_config(ENV_FILE)
        extract_subtitles(input_path, output_path)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
