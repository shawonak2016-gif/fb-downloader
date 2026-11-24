# =====================================================================
#  PATCH FOR YOUR app.py  (3 small edits)
# =====================================================================
#
#  EDIT 1 - requirements.txt: add one line (a bundled ffmpeg program)
#  -----------------------------------------------------------------
#      flask
#      flask-cors
#      yt-dlp
#      gunicorn
#      imageio-ffmpeg
#
#  EDIT 2 - top of app.py: replace your first lines with this
#  -----------------------------------------------------------------
import io
import os
import re
import shutil
import subprocess
import tempfile
from urllib.parse import quote, urlparse

from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# expose_headers lets the Blogger page read the title of the MP3 file
CORS(app, expose_headers=["X-Title", "X-Duration", "Content-Disposition"])

#
#  EDIT 3 - paste everything below ABOVE the line:  if __name__ == '__main__':
#  -----------------------------------------------------------------

ALLOWED_DOMAINS = ("facebook.com", "fb.watch", "fb.com")
MAX_SECONDS = 600            # 10 minutes: protects the free server
MAX_BYTES = 80 * 1024 * 1024


def _is_facebook_url(url):
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in ("http", "https"):
            return False
    except Exception:
        return False
    return any(host == d or host.endswith("." + d) for d in ALLOWED_DOMAINS)


def _ffmpeg_path():
    system = shutil.which("ffmpeg")
    if system:
        return system
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


@app.route("/api/mp3", methods=["POST"])
def get_mp3():
    data = request.get_json(silent=True) or {}
    video_url = (data.get("url") or "").strip()

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400
    if not _is_facebook_url(video_url):
        return jsonify({"error": "Please use a valid Facebook video or Reels link."}), 400

    with tempfile.TemporaryDirectory() as tmp:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "format": "bestaudio/best",
            "outtmpl": os.path.join(tmp, "src.%(ext)s"),
            "max_filesize": MAX_BYTES,
            "socket_timeout": 20,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                duration = info.get("duration") or 0
                if duration > MAX_SECONDS:
                    return jsonify({"error": "This video is longer than 10 minutes. Please use a shorter video."}), 400
                ydl.process_ie_result(info, download=True)

            src = next(
                (os.path.join(tmp, f) for f in os.listdir(tmp) if f.startswith("src.")),
                None,
            )
            if not src:
                return jsonify({"error": "Could not download the audio. Make sure the video is Public."}), 400

            out = os.path.join(tmp, "out.mp3")
            subprocess.run(
                [_ffmpeg_path(), "-y", "-i", src, "-vn",
                 "-codec:a", "libmp3lame", "-b:a", "128k", out],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=120,
            )

            with open(out, "rb") as fh:
                buf = io.BytesIO(fh.read())

            title = info.get("title") or "Facebook Video"
            mins, secs = int(duration // 60), int(duration % 60)

            resp = send_file(
                buf,
                mimetype="audio/mpeg",
                as_attachment=True,
                download_name="fb_audio.mp3",
            )
            resp.headers["X-Title"] = quote(title[:150], safe="")
            resp.headers["X-Duration"] = f"{mins}:{secs:02d}" if duration else ""
            return resp

        except subprocess.TimeoutExpired:
            return jsonify({"error": "Conversion took too long. Try a shorter video."}), 400
        except Exception:
            return jsonify({"error": "Could not convert this video. Make sure it is Public and the link is correct."}), 400
