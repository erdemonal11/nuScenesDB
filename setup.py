import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["os", "psycopg2", "customtkinter", "tkinter", "subprocess", "csv", "tabulate"],
    "include_files": []  
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
