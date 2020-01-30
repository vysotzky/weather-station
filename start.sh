#! /bin/sh

export DISPLAY=:0.0
BASEDIR=$(dirname $0)
cd ${BASEDIR}
sudo python3 main.py > /dev/null 2>&1
