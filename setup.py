import sys
import os
from cx_Freeze import setup, Executable

dll_path = "C:/Users/mrifk/AppData/Local/Programs/Python/Python310/python310.dll"

build_exe_options = {
    "packages": ["os", "psycopg2", "customtkinter", "tkinter", "subprocess", "csv", "tabulate"],
    "include_files": [
        dll_path  
    ]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable(
        script="nuscenetool.py",  
        base=base,
    )
]

setup(
    name="nuScenesDBTool",
    version="1.0",
    description="nuScenes DB Tool for managing nuScenes database",
    options={"build_exe": build_exe_options},
    executables=executables
)
