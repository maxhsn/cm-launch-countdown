# CM Launch Countdown

Hourly countdown image for the Combat Market full launch (Monday 26 October 2026, 12:00 Dubai), uploaded to Slack #cm-allteam by a GitHub Action.

- `template.html` + `brand/` make the page in the real combatmarket.com branding (Titling, Space, #f3432a).
- `render.py` screenshots it to `out/countdown.png` and writes the caption.
- `post_to_slack.py` uploads the file to the channel.
- `.github/workflows/countdown.yml` runs it every hour from 07:00 to 18:00 Dubai, and disables itself after the launch post.

Setup: add a repo secret `SLACK_BOT_TOKEN` (bot scopes `files:write`, `chat:write`) and invite the bot to #cm-allteam.
