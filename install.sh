#!/usr/bin/env sh

# THIS IS A TEMP HACK FOR NOW. WE NEED A PROPER ROS PACKAGE AT SOME POINT.

if [ -z ${prefix+x} ]; then
    echo ">>> ERROR: prefix env variable is unset";
    exit 1;
else
    echo ">>> INFO prefix is set to '$prefix'"; fi

#### PIP INSTALL WSPY

if pip --version | grep 'pip 8.' ; then
  pip install --ignore-installed --prefix=$prefix --system 'ws4py==0.3.2'
  pip install --ignore-installed --prefix=$prefix --system 'ws4py==0.3.2'
else
  pip install --ignore-installed --prefix=$prefix 'ws4py==0.3.2'
  pip install --ignore-installed --prefix=$prefix 'ws4py==0.3.2'
fi

#### COPY SCRIPTS

echo ">>> INFO: Copying scripts to: '$prefix'"

cp -f kaldi_ros.py $prefix/bin
chmod +x $prefix/bin/kaldi_ros.py

cp -f helper_scripts/run_kaldi_arecord.sh $prefix/bin
cp -f helper_scripts/run_kaldi_docker.sh  $prefix/bin
chmod +x $prefix/bin/run_kaldi_*

echo ">>> INFO: Done"


