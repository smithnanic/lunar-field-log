#!/usr/bin/env python3
"""Download NASA's 2025 "Moon Phase and Libration" video from Wikimedia Commons and
save the 30 hourly frames listed in frames.csv as JPEGs.

The video has one frame per hour of 2025, so NASA frame N is video frame N-1.
Usage: fetch_frames.py OUT_DIR
"""
import csv, json, os, subprocess, sys, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TITLE = "File:Moon Phase and Libration, 2025 (SVS5415 - phases 2025 plain 2160p30).webm"
FALLBACK = ("https://upload.wikimedia.org/wikipedia/commons/e/e1/"
            "Moon_Phase_and_Libration%2C_2025_%28SVS5415_-_phases_2025_plain_2160p30%29.webm")
UA = "lunar-field-log-build/1.0 (https://github.com/smithnanic/lunar-field-log)"

def log(*a):
    line = " ".join(str(x) for x in a)
    print(line, flush=True)
    with open(os.path.join(OUT, "log.txt"), "a") as f:
        f.write(line + "\n")

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=120)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

url = FALLBACK
try:
    api = ("https://commons.wikimedia.org/w/api.php?action=query&prop=videoinfo&viprop=url%7Csize"
           "&format=json&titles=" + urllib.parse.quote(TITLE))
    page = next(iter(json.load(get(api))["query"]["pages"].values()))
    url = page["videoinfo"][0]["url"].split("?")[0]
    log("resolved", url, page["videoinfo"][0].get("size"))
except Exception as e:  # keep going with the known address
    log("could not resolve through the Commons API, using fallback:", repr(e))

video = "/tmp/moon2025.webm"
with get(url) as r, open(video, "wb") as f:
    n = 0
    while True:
        chunk = r.read(1 << 20)
        if not chunk:
            break
        f.write(chunk); n += len(chunk)
log("downloaded bytes", n)

probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate,nb_frames,duration:format=duration",
                        "-of", "json", video], capture_output=True, text=True)
log("ffprobe", probe.stdout.replace("\n", " "), probe.stderr.strip())

rows = list(csv.DictReader(open(os.path.join(HERE, "frames.csv"))))
idx = sorted(int(r["nasa_frame"]) - 1 for r in rows)
sel = "+".join(f"eq(n\\,{i})" for i in idx)
# The Moon sits in the middle of the 3840x2160 frame; keep the centre square.
cmd = ["ffmpeg", "-v", "error", "-i", video, "-vf", f"select='{sel}',crop=2160:2160:840:0",
       "-vsync", "0", "-q:v", "2", os.path.join(OUT, "tmp_%02d.jpg")]
res = subprocess.run(cmd, capture_output=True, text=True)
log("ffmpeg exit", res.returncode, res.stderr.strip()[-2000:])

made = sorted(f for f in os.listdir(OUT) if f.startswith("tmp_"))
log("frames written", len(made), "expected", len(idx))
for name, i in zip(made, idx):
    os.rename(os.path.join(OUT, name), os.path.join(OUT, f"moon.{i + 1:04d}.jpg"))
if len(made) != len(idx):
    sys.exit(1)
