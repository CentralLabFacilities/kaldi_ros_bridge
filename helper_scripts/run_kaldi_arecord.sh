#!/usr/bin/env bash

echo ""
echo "Your prefix is ---> $prefix"
echo ""

# NB! RATE: for raw 16-bit audio it must be 2*samplerate!
arecord -f S16_LE -r 16000 | python $prefix/bin/kaldi_ros.py -r 32000 -
