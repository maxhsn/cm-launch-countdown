"""Render the Combat Market launch countdown as a static PNG.
Usage: python3 render.py            -> writes out/countdown.png and out/caption.txt
"""
import base64, re, pathlib, time, datetime, zoneinfo
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent
TARGET = datetime.datetime(2026, 10, 26, 12, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Dubai"))

def build_html():
    t = (ROOT / "template.html").read_text()
    t = t.replace("__TITLING__", base64.b64encode((ROOT / "brand/titling.otf").read_bytes()).decode())
    t = t.replace("__SPACE__", base64.b64encode((ROOT / "brand/space.ttf").read_bytes()).decode())
    logo = re.sub(r'\s(width|height)="\d+"', '', (ROOT / "brand/logo.svg").read_text().strip(), count=2)
    t = t.replace("__LOGO__", logo).replace("__MARK__", (ROOT / "brand/mark.svg").read_text().strip())
    out = ROOT / "out/page.html"; out.write_text(t); return out

def caption(now):
    diff = TARGET - now
    if diff.total_seconds() <= 0:
        return "Combat Market is live. The market is open."
    d = diff.days; h = diff.seconds // 3600; m = (diff.seconds % 3600) // 60
    bits = []
    if d: bits.append(f"{d} day{'s' if d != 1 else ''}")
    if h: bits.append(f"{h} hour{'s' if h != 1 else ''}")
    if not d and not h: bits.append(f"{m} minute{'s' if m != 1 else ''}")
    return f"Full launch in {' '.join(bits)}. Monday 26 October, 12:00 Dubai."

def main():
    now = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Dubai"))
    stamp = now.strftime("%a %d %b, %H:%M") + " Dubai"
    html = build_html()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1400, "height": 880}, device_scale_factor=2)
        pg.add_init_script("window.CM_STATIC = {now: %d, stamp: %r};" % (int(time.time() * 1000), stamp))
        pg.goto("file://" + str(html))
        pg.wait_for_function("document.fonts.status === 'loaded'")
        pg.wait_for_timeout(300)
        pg.screenshot(path=str(ROOT / "out/countdown.png"), type="png")
        b.close()
    (ROOT / "out/caption.txt").write_text(caption(now))
    print(caption(now))

if __name__ == "__main__":
    main()
