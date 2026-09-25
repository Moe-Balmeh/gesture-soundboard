import os

# without this media foundation takes ~2 min to open the webcam
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

from app.ui.main_window import run  # noqa: E402

if __name__ == "__main__":
    run()
