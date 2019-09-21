#!/bin/sh

# start.sh

# Usage:
# $ start.sh <port>

echo "In picocom, press C-a C-x to exit"

if [ -n "$1" ]; then
  echo "Connecting to $1"
  picocom -c $1
else
  echo "Port not supplied. Connecting to /dev/ttyACM0 now..."
  picocom -c /dev/ttyACM0
fi
