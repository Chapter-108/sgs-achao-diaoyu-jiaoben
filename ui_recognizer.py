import numpy as np

from image_processor import ImageProcessor
from setting import Config


class FishingUIRecognizer:
    """负责UI识别的类。"""

    def check_start_fishing_ui(self, img: np.ndarray) -> bool:
        start_button = ImageProcessor.load_template(str(Config.START_FISH_BUTTON))
        return ImageProcessor.is_match_template(img, start_button)

    def check_cast_rod_ui(self, img: np.ndarray) -> bool:
        huaner = ImageProcessor.load_template(str(Config.BAIT_IMAGE))
        return ImageProcessor.is_match_template(img, huaner)

    def check_no_bait_ui(self, img: np.ndarray) -> bool:
        use_button = ImageProcessor.load_template(str(Config.USE_BUTTON))
        return ImageProcessor.is_match_template(img, use_button)

    def check_spear_fish_ui(self, img: np.ndarray) -> bool:
        tijian = ImageProcessor.load_template(str(Config.TIJIAN_IMAGE))
        return ImageProcessor.is_match_template(img, tijian, threshold=0.6)

    def check_catch_fish_ui(self, img: np.ndarray) -> bool:
        time_icon = ImageProcessor.load_template(str(Config.TIME_IMAGE))
        return ImageProcessor.is_match_template(img, time_icon)

    def check_fishing_ui(self, img: np.ndarray) -> bool:
        pressure_img = ImageProcessor.load_template(str(Config.PRESSURE_IMAGE))
        return ImageProcessor.is_match_template(img, pressure_img)

    def check_instant_kill_ui(self, img: np.ndarray) -> bool:
        up_button = ImageProcessor.load_template(str(Config.UP_IMAGE))
        return ImageProcessor.is_match_template(img, up_button)

    def check_end_fishing_ui(self, img: np.ndarray) -> bool:
        retry_button = ImageProcessor.load_template(str(Config.RETRY_BUTTON))
        return ImageProcessor.is_match_template(img, retry_button)
