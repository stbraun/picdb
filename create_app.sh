#!/usr/bin/env bash

if [ $1 = -n ]; then
    echo "Creating new spec file. Do not forget to add required extensions!"
    pyinstaller --onefile --windowed -n PicDB start_picdb.py
    shift
else
    echo "Using existing spec file. Run with -n to create a new one."
    pyinstaller  PicDB.spec
fi
