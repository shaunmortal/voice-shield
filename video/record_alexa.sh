#!/bin/zsh
# Screen + laptop mic while the user talks to the Alexa+ stand-in (server already running).
cd /Users/Happy/Desktop/AMAZON
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
sleep 3
python3 -c "import time;print(time.time())" > video/alexa_t0.txt
ffmpeg -loglevel error -y -f avfoundation -capture_cursor 1 -framerate 30 -i "1:0" -t 75 -vf "scale=1920:-2,format=yuv420p" -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 128k video/alexa_screen.mp4
curl -s localhost:8000/api/event > video/alexa_events.json
echo done
