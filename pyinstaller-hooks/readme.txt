The files in this folder are patches for the pyinstaller files.

With OS X tcl and tk could not correctly processed,
because the file system is not case sensitive (at least in most installations).


Usage:
pyinstaller --onefile --windowed \
            --additional-hooks-dir pyinstaller-hooks \
            --runtime-hook pyinstaller-hooks/pyi_rth__tkinter.py <my_app.py>



See:
https://github.com/viotti/pyinstaller/commit/597af5cb01c064620b53ea1ee537e30f56fa481d?diff=unified
