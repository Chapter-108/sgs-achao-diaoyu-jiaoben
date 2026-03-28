import logging
from typing import Dict, Optional, Tuple

import cv2
import numpy as np
import pyautogui

from setting import Config


class ImageProcessor:
    """图像处理类，处理模板加载与匹配。"""

    _template_cache: Dict[str, np.ndarray] = {}

    @classmethod
    def load_template(cls, path: str) -> np.ndarray:
        if path not in cls._template_cache:
            with open(path, "rb") as f:
                buf = np.frombuffer(f.read(), dtype=np.uint8)
            img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
            if img is None:
                raise RuntimeError(f"模板加载失败: {path}")
            cls._template_cache[path] = img
        return cls._template_cache[path]

    @classmethod
    def preload_all_templates(cls) -> None:
        paths = [
            Config.START_FISH_BUTTON,
            Config.BAIT_IMAGE,
            Config.USE_BUTTON,
            Config.TIME_IMAGE,
            Config.PRESSURE_IMAGE,
            Config.UP_IMAGE,
            Config.RETRY_BUTTON,
            Config.PUSH_ROD_BUTTON,
            Config.BUY_BUTTON,
            Config.TIJIAN_IMAGE,
            Config.RED_ZONE_IMAGE,
        ] + list(Config.DIRECTION_ICONS)

        for path in paths:
            try:
                cls.load_template(str(path))
            except Exception as e:
                logging.warning(f"预加载模板失败: {path} -> {e}")
        logging.info(f"模板预加载完成，共 {len(cls._template_cache)} 个")

    @staticmethod
    def get_screenshot(
        size: Tuple[int, int, int, int],
        is_save: bool = False,
        save_path: Optional[str] = None,
    ) -> np.ndarray:
        img = pyautogui.screenshot(region=size)
        img_np = np.array(img)
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        if is_save and save_path:
            img.save(save_path)
        return img_np

    @staticmethod
    def is_match_template(img: np.ndarray, template: np.ndarray, threshold: float = 0.8) -> bool:
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        return len(loc[0]) > 0

    @staticmethod
    def match_template(
        img: np.ndarray,
        template: np.ndarray,
        threshold: float = 0.8,
        position: Tuple[float, float] = (0.5, 0.5),
    ) -> Tuple[int, int]:
        clamped_x = max(0, min(1, position[0]))
        clamped_y = max(0, min(1, position[1]))
        if clamped_x != position[0] or clamped_y != position[1]:
            logging.warning(f"position参数值被调整: {position} -> ({clamped_x}, {clamped_y})")

        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val < threshold:
            raise ValueError(f"模板匹配置信度不足: max_val={max_val:.4f}, threshold={threshold:.4f}")

        template_width = template.shape[1]
        template_height = template.shape[0]
        x = int(max_loc[0] + template_width * clamped_x)
        y = int(max_loc[1] + template_height * clamped_y)
        return (x, y)
