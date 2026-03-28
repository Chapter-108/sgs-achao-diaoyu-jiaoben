import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Final

class Config:
    """配置类，管理所有配置项"""
    
    # 窗口配置
    WINDOW_SIZE: Final[tuple[int, int, int, int]] = (163, 33, 1602, 946)
    WINDOW_TITLE: Final[str] = "雷电模拟器"
    
    # 游戏配置
    ROD_RETRIEVE_INTERVAL: Final[int] = 14 # 钓鱼时收杆的间隔
    FISHING_CLICK_INTERVAL: Final[float] = 0.08 # 钓鱼时点击的间隔
    
    # 路径配置
    BASE_DIR: Final[Path] = Path(__file__).parent.absolute()
    GENERATE_DIR: Final[Path] = BASE_DIR / "generate"
    CONFIG_FILE: Final[Path] = GENERATE_DIR / "config.yaml"
    PROFILES_FILE: Final[Path] = GENERATE_DIR / "profiles.yaml"
    LOG_FILE: Final[Path] = GENERATE_DIR / "log.txt"
    LOG_MAX_BYTES: Final[int] = 2 * 1024 * 1024
    LOG_BACKUP_COUNT: Final[int] = 3
    
    # 根据是否打包成exe选择不同的资源路径
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        IMAGE_DIR: Final[Path] = Path(getattr(sys, '_MEIPASS', BASE_DIR)) / "data"
    else:
        IMAGE_DIR: Final[Path] = BASE_DIR / "images"
    
    # 图像资源路径
    START_FISH_BUTTON: Final[Path] = IMAGE_DIR / "start_fish.png"
    UP_IMAGE: Final[Path] = IMAGE_DIR / "01_up.png"
    LEFT_IMAGE: Final[Path] = IMAGE_DIR / "02_left.png"
    DOWN_IMAGE: Final[Path] = IMAGE_DIR / "03_un.png"
    RIGHT_IMAGE: Final[Path] = IMAGE_DIR / "04_right.png"
    WIND_IMAGE: Final[Path] = IMAGE_DIR / "05_wind.png"
    FIRE_IMAGE: Final[Path] = IMAGE_DIR / "06_fire.png"
    RAY_IMAGE: Final[Path] = IMAGE_DIR / "07_ray.png"
    ELECTRICITY_IMAGE: Final[Path] = IMAGE_DIR / "08_electricity.png"
    BAIT_IMAGE: Final[Path] = IMAGE_DIR / "huaner.png"
    USE_BUTTON: Final[Path] = IMAGE_DIR / "use_button.png"
    TIME_IMAGE: Final[Path] = IMAGE_DIR / "time.png"
    BUY_BUTTON: Final[Path] = IMAGE_DIR / "buy_button.png"
    PUSH_ROD_BUTTON: Final[Path] = IMAGE_DIR / "push_gan_button.png"
    PRESSURE_IMAGE: Final[Path] = IMAGE_DIR / "guogao.png"
    RETRY_BUTTON: Final[Path] = IMAGE_DIR / "again_button.png"
    CURRENT_UI: Final[Path] = IMAGE_DIR / "current_UI.png"
    TIJIAN_IMAGE: Final[Path] = IMAGE_DIR / "tijian.png"
    RED_ZONE_IMAGE: Final[Path] = IMAGE_DIR / "red_zone.png"
    
    # 方向图标列表
    DIRECTION_ICONS: Final[list[Path]] = [
        UP_IMAGE, DOWN_IMAGE, LEFT_IMAGE, RIGHT_IMAGE,
        WIND_IMAGE, FIRE_IMAGE, RAY_IMAGE, ELECTRICITY_IMAGE
    ]
    _runtime_ready: bool = False
    
    @classmethod
    def setup_logging(cls) -> None:
        """配置日志系统"""
        # 确保日志目录存在
        cls.GENERATE_DIR.mkdir(exist_ok=True)

        root = logging.getLogger("")
        root.setLevel(logging.INFO)
        if root.handlers:
            for handler in list(root.handlers):
                root.removeHandler(handler)

        file_formatter = logging.Formatter(
            '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
            datefmt='%a, %d %b %Y %H:%M:%S',
        )
        file_handler = RotatingFileHandler(
            filename=str(cls.LOG_FILE),
            maxBytes=cls.LOG_MAX_BYTES,
            backupCount=cls.LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)
        root.addHandler(file_handler)

        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        root.addHandler(console_handler)

        logging.info("开始记录日志")
    
    @classmethod
    def verify_resources(cls) -> None:
        """验证必要的资源文件是否存在"""
        required_files = [
            cls.START_FISH_BUTTON,
            cls.UP_IMAGE,
            cls.LEFT_IMAGE,
            cls.DOWN_IMAGE,
            cls.RIGHT_IMAGE,
            cls.WIND_IMAGE,
            cls.FIRE_IMAGE,
            cls.RAY_IMAGE,
            cls.ELECTRICITY_IMAGE,
            cls.BAIT_IMAGE,
            cls.USE_BUTTON,
            cls.TIME_IMAGE,
            cls.BUY_BUTTON,
            cls.PUSH_ROD_BUTTON,
            cls.PRESSURE_IMAGE,
            cls.RETRY_BUTTON,
            cls.TIJIAN_IMAGE,
            cls.RED_ZONE_IMAGE,
        ]
        
        missing_files = [str(f) for f in required_files if not f.exists()]
        if missing_files:
            raise FileNotFoundError(
                f"以下必要的资源文件缺失：\n{chr(10).join(missing_files)}"
            )

    @classmethod
    def ensure_runtime_ready(cls) -> None:
        """按需初始化运行时依赖，避免导入模块时产生副作用。"""
        if cls._runtime_ready:
            return
        cls.setup_logging()
        cls.verify_resources()
        cls._runtime_ready = True
