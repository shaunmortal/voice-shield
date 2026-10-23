#!/bin/zsh
# During ONE call, try each scrcpy audio source for 20 s and save it, to see which ones carry call audio.
cd /Users/Happy/Desktop/AMAZON/data/captest
TAG=$1
for src in voice-call voice-call-downlink voice-call-uplink playback output; do
  scrcpy --no-video --no-window --no-playback --audio-source=$src --time-limit=20 --record=${TAG}_$src.mka >/dev/null 2>&1
  echo "$src done"
done
