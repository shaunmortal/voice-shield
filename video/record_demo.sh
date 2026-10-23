#!/bin/zsh
# Records the Alexa+ simulator page while the server replays audio captured from the real VoLTE call.
cd /Users/Happy/Desktop/AMAZON
pkill -f "server.py" ; sleep 1
.venv/bin/python server.py --source file:video/demo_input.wav > video/server.log 2>&1 &
until curl -s -m 1 -o /dev/null localhost:8000/; do sleep 0.5; done
osascript <<'OSA'
tell application "Google Chrome"
  repeat with i from (count of windows) to 1 by -1
    if URL of active tab of window i contains "localhost:8000" then close window i
  end repeat
  set w to make new window
  set URL of active tab of w to "http://localhost:8000/?demo=1"
  set bounds of w to {0, 25, 1440, 900}
  activate
end tell
OSA
sleep 3
python3 -c "import time;print(time.time())" > video/t0.txt
ffmpeg -loglevel error -y -f avfoundation -capture_cursor 1 -framerate 30 -i "1:none" -t 90 -vf "scale=1920:-2,format=yuv420p" -c:v libx264 -preset veryfast -crf 20 video/screen.mp4
curl -s localhost:8000/api/event > video/events.json
pkill -f "server.py"
echo done
