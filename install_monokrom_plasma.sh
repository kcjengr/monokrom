#!/bin/bash

zenity --entry \
    --title="Path to save download to" \
    --text="Please enter path. e.g. ~/dev"
    --entry-text="~/dev"
SAVE_LOC = $?

if [! -d  $SAVE_LOC]
then
    mkdir $SAVE_LOC
fi

cd $SAVE_LOC

pip3 uninstall qtpyvcp
git clone https://github.com/kcjengr/qtpyvcp
cd qtpyvcp
git checkout plasma_db
python3 -m pip install --editable .
cp scripts/.xsessionrc ~/

cd $SAVE_LOC

pip3 uninstall monokrom-vcp
git clone https://github.com/joco-nz/monokrom-vcp.git
cd monokrom-vcp
python3 -m pip install --editable .
