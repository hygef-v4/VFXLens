"""Read-only encoded-media contract check; requires FFmpeg and ffprobe on PATH."""
import argparse
import json
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return number


def positive_rate(value):
    try:
        rate = Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise argparse.ArgumentTypeError("use a positive rate, e.g. 30 or 30000/1001") from error
    if rate <= 0:
        raise argparse.ArgumentTypeError("frame rate must be positive")
    return rate


def command(*args):
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"{Path(args[0]).name} failed: {result.stderr[-2000:].strip()}")
    return result.stdout


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--width", type=positive_int, required=True)
    parser.add_argument("--height", type=positive_int, required=True)
    parser.add_argument("--fps", type=positive_rate, required=True)
    parser.add_argument("--frames", type=positive_int, required=True)
    parser.add_argument("--codec", default="h264")
    parser.add_argument("--audio", choices=("required", "none", "optional"), default="optional")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    result = {"ok": False, "file": str(args.video.resolve()), "checks": {}, "errors": []}
    try:
        if not args.video.is_file():
            raise ValueError("Input video is not a file")
        if args.report and (args.report.exists() or args.report.is_symlink()):
            raise ValueError("Report destination exists; choose a fresh filename")
        ffprobe, ffmpeg = shutil.which("ffprobe"), shutil.which("ffmpeg")
        if not ffprobe or not ffmpeg:
            raise ValueError("FFmpeg and ffprobe must be available on PATH")
        probe = json.loads(command(ffprobe, "-v", "error", "-count_frames", "-show_streams", "-of", "json", str(args.video.resolve())))
        videos = [s for s in probe["streams"] if s.get("codec_type") == "video"]
        audios = [s for s in probe["streams"] if s.get("codec_type") == "audio"]
        if len(videos) != 1:
            raise ValueError(f"Expected one video stream, got {len(videos)}")
        stream = videos[0]
        checks = {
            "codec": stream.get("codec_name") == args.codec,
            "dimensions": (stream.get("width"), stream.get("height")) == (args.width, args.height),
            "fps": Fraction(stream["avg_frame_rate"]) == args.fps,
            "decoded_frames": int(stream["nb_read_frames"]) == args.frames,
            "duration": abs(float(stream["duration"]) - float(args.frames / args.fps)) <= float(1 / args.fps) + .001,
            "audio_policy": args.audio == "optional" or bool(audios) == (args.audio == "required"),
        }
        result["observed"] = {"codec": stream.get("codec_name"), "width": stream.get("width"),
                              "height": stream.get("height"), "fps": stream["avg_frame_rate"],
                              "frames": stream["nb_read_frames"], "duration": stream["duration"],
                              "audio_streams": len(audios)}
        command(ffmpeg, "-v", "error", "-xerror", "-i", str(args.video.resolve()), "-f", "null", "-")
        checks["full_decode"] = True
        result["checks"] = checks
        result["errors"] = [name for name, passed in checks.items() if not passed]
        result["ok"] = all(checks.values())
    except (OSError, ValueError, KeyError, RuntimeError, ZeroDivisionError) as error:
        result["errors"].append(str(error))
    if args.report:
        try:
            # Exclusive creation preserves media and earlier reports, including symlinks.
            with args.report.open("x", encoding="utf-8") as report:
                json.dump(result, report, ensure_ascii=False, indent=2)
                report.write("\n")
        except OSError as error:
            result["ok"] = False
            result["errors"].append(f"Could not create report: {error}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
