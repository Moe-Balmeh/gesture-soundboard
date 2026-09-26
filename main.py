import ctypes
import os
import sys

# without this media foundation takes ~2 min to open the webcam
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
# the .exe has no console, so anything a library prints would crash it
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")
# so the taskbar shows our icon instead of python's
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("GestureSoundboard")

from app.logic.single_instance import already_running  # noqa: E402
from app.ui.main_window import run  # noqa: E402

if __name__ == "__main__":
    if not already_running():  # if it's already open, that copy shows its window instead
        run()
