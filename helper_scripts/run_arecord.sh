#!/usr/bin/env bash

# NB! RATE: for raw 16-bit audio it must be 2*samplerate!
arecord -f S16_LE -r 16000 | python ../kaldi_ros.py -r 32000 -
