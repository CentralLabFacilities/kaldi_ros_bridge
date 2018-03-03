#!/usr/bin/env bash

echo "Your prefix is ---> $prefix"
echo "After the container has started, run: /opt/start.sh -y /opt/models/sample_english_nnet2.yaml"
echo ""

docker run -it -p 8181:80 -v $prefix/share/kaldi_models:/opt/models jcsilva/docker-kaldi-gstreamer-server:latest /bin/bash
