"""Upload out/countdown.png to Slack as a file, with the caption from out/caption.txt.
Needs SLACK_BOT_TOKEN (bot scopes: files:write, chat:write; bot invited to the channel).
After the launch post, disables the GitHub workflow so it stops firing.
"""
import os, sys, json, pathlib, datetime, zoneinfo, subprocess, urllib.request, urllib.parse, uuid

ROOT = pathlib.Path(__file__).resolve().parent
CHANNEL = "C0CA45ZKBHU"  # #cm-allteam
TARGET = datetime.datetime(2026, 10, 26, 12, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Dubai"))
TOKEN = os.environ.get("SLACK_BOT_TOKEN", "").strip()
if not TOKEN:
    sys.exit("SLACK_BOT_TOKEN is not set. Add it under Settings > Secrets and variables > Actions.")

def api(method, data=None, form=True):
    url = "https://slack.com/api/" + method
    body = urllib.parse.urlencode(data or {}).encode() if form else json.dumps(data or {}).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Content-Type", "application/x-www-form-urlencoded" if form else "application/json; charset=utf-8")
    with urllib.request.urlopen(req) as r:
        out = json.load(r)
    if not out.get("ok"):
        sys.exit(f"Slack {method} failed: {out}")
    return out

now = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Dubai"))
png = (ROOT / "out/countdown.png").read_bytes()
caption = (ROOT / "out/caption.txt").read_text().strip()
live = now >= TARGET
filename = ("cm-launch-live.png" if live else f"cm-launch-countdown-{now:%Y%m%d-%H%M}.png")

# 1. get an upload URL
up = api("files.getUploadURLExternal", {"filename": filename, "length": len(png)})

# 2. upload the bytes (multipart)
boundary = uuid.uuid4().hex
body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
        f"Content-Type: image/png\r\n\r\n").encode() + png + f"\r\n--{boundary}--\r\n".encode()
req = urllib.request.Request(up["upload_url"], data=body, method="POST")
req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
with urllib.request.urlopen(req) as r:
    r.read()

# 3. finish and share into the channel with the caption
api("files.completeUploadExternal",
    {"files": [{"id": up["file_id"], "title": "Combat Market full launch" if live else "Combat Market launch countdown"}],
     "channel_id": CHANNEL, "initial_comment": caption}, form=False)
print("Posted:", caption)

# 4. after the launch post, switch the workflow off
if live and os.environ.get("GH_TOKEN"):
    subprocess.run(["gh", "workflow", "disable", "countdown.yml"], check=False)
    print("Launch posted. Workflow disabled.")
