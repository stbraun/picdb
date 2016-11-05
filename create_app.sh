#!/usr/bin/env bash

pyinstaller --onefile --windowed \
            -n PicDB \
            --additional-hooks-dir pyinstaller-hooks \
            --runtime-hook pyinstaller-hooks/pyi_rth__tkinter.py \
            start_picdb.py

#pyinstaller  PicDB.spec
