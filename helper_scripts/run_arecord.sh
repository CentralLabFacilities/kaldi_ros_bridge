#!/usr/bin/env bash

arecord -f S16_LE -r 16000 | python ../kaldi_ros.py -r 32000 -
