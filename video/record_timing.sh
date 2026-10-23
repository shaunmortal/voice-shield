#!/bin/zsh
# Live WhatsApp call: server reads the caller's audio from the Oppo (playback capture) + user's voice from the laptop mic,
# Chrome shows the Alexa page with the timing meter, the screen is recorded for the video.
cd /Users/Happy/Desktop/AMAZON
pkill -f "server.py"; pkill -f scrcpy; sleep 1
.venv/bin/python server.py --source whatsapp > video/timing_server.log 2>&1 &
until curl -s -m 1 -o /dev/null localhost:8000/; do sleep 0.5; done
osascript <<'OSA'
tell application "Google Chrome"
  repeat with i from (count of windows) to 1 by -1
    if URL of active tab of window i contains "localhost:8000" then close window i
  end repeat
  set w to make new window
  set URL of active tab of w to "http://localhost:8000/"
  set bounds of w to {0, 25, 1440, 900}
  activate
end tell
OSA
sleep 2
python3 -c "import time;print(time.time())" > video/timing_t0.txt
( while true; do curl -s -X POST localhost:8000/mcp -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -H 'MCP-Protocol-Version: 2025-11-25' \
    -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_call_status","arguments":{}}}' >> video/timing_status.jsonl; echo >> video/timing_status.jsonl; sleep 1; done ) &
POLL=$!
ffmpeg -loglevel error -y -f avfoundation -capture_cursor 1 -framerate 30 -i "1:none" -t 170 -vf "scale=1920:-2,format=yuv420p" -c:v libx264 -preset veryfast -crf 20 video/timing_screen.mp4
kill $POLL; pkill -f "server.py"; pkill -f scrcpy
echo done
