import argparse
import pyautogui
import time
import cv2
import numpy as np
import keyboard
from threading import Thread, Event
from enum import Enum, auto
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from setting import Config
from config_manager import ConfigManager
from window_manager import WindowManager
from image_processor import ImageProcessor
from ui_recognizer import FishingUIRecognizer
import logging
 
 
class FishState(Enum):
    """钓鱼游戏的状态枚举"""
    START_FISHING = auto()  # 开始钓鱼
    CAST_ROD = auto()       # 抛竿
    NO_BAIT = auto()        # 鱼饵不足
    SPEAR_FISH = auto()     # 刺鱼
    CATCH_FISH = auto()     # 捕鱼
    FISHING = auto()        # 钓鱼中
    INSTANT_KILL = auto()   # 秒杀
    END_FISHING = auto()    # 结束钓鱼
    EXIT = auto()           # 退出
 
 
@dataclass
class GameConfig:
    """游戏配置数据类"""
    window_title: str  # 模拟器窗口标题
    window_size: Tuple[int, int, int, int]  # 模拟器窗口大小和位置 (x, y, width, height)
    start_fishing_pos: Optional[Tuple[int, int]] = None  # 开始钓鱼按钮的中心点坐标
    rod_position: Optional[Tuple[int, int]] = None  # 钓鱼界面拉杆位置中心点坐标
    pressure_indicator_pos: Optional[Tuple[int, int]] = None  # 用来判断压力是否过高的点的位置
    low_pressure_color: Optional[Tuple[int, int, int]] = None  # 用来判断压力是否过高的点的颜色
    original_rod_color: Optional[Tuple[int, int, int]] = None  # 钓鱼界面拉杆位置中心点颜色
    direction_icon_positions: Optional[Dict[str, Tuple[int, int]]] = None  # 方向图标位置字典
    retry_button_center: Optional[Tuple[int, int]] = None  # 再来一次按钮的中心点坐标
    use_bait_button_pos: Optional[Tuple[int, int]] = None  # 使用鱼饵按钮的位置
    tijian_pos: Optional[Tuple[int, int]] = None  # 提竿按钮位置
 
 
class MouseController:
    """鼠标控制类，处理所有鼠标操作"""
    
    @staticmethod
    def press_mouse_move(start_x: int, start_y: int, 
                        x: int, y: int, button: str = 'left') -> None:
        """模拟鼠标拖拽操作"""
        pyautogui.mouseDown(start_x, start_y, button=button)
        pyautogui.moveTo(start_x + x, start_y + y, duration=0.03)
        pyautogui.mouseUp(button=button)
    
    @staticmethod
    def click(position: Tuple[int, int]) -> None:
        """点击指定位置"""
        pyautogui.click(position)
 
 
class FishingStateManager:
    """负责状态管理和转换的类"""
    
    def __init__(self, current_img: np.ndarray):
        self.ui_recognizer = FishingUIRecognizer()
        self.current_state = self._determine_initial_state(current_img)
        self._setup_state_flags()
    
    def _setup_state_flags(self) -> None:
        """初始化状态标志"""
        self.first_start_fishing = True
        self.first_cast_rod = True
        self.first_no_bait = True
        self.first_spear_fish = True
        self.first_retry = True
        self.first_instant_kill = True
        self.rod_retrieve_time = 0
    
    def update_state(self, current_img: np.ndarray) -> None:
        """更新当前状态"""
        old_state = self.current_state
        
        match self.current_state:
            case FishState.START_FISHING:
                if self.ui_recognizer.check_cast_rod_ui(current_img):
                    self.current_state = FishState.CAST_ROD
            
            case FishState.CAST_ROD:
                if self.ui_recognizer.check_no_bait_ui(current_img):
                    self.current_state = FishState.NO_BAIT
                elif self.ui_recognizer.check_spear_fish_ui(current_img):
                    self.current_state = FishState.SPEAR_FISH
                elif self.ui_recognizer.check_catch_fish_ui(current_img):
                    self.current_state = FishState.CATCH_FISH
            
            case FishState.SPEAR_FISH:
                if self.ui_recognizer.check_catch_fish_ui(current_img):
                    self.current_state = FishState.CATCH_FISH
            
            case FishState.NO_BAIT:
                if not self.ui_recognizer.check_no_bait_ui(current_img):
                    self.current_state = FishState.CAST_ROD
            
            case FishState.CATCH_FISH:
                if self.ui_recognizer.check_fishing_ui(current_img):
                    # FISHING 页面已就绪，但有些元素状态重置需要时间，比如挥杆
                    time.sleep(2)
                    self.current_state = FishState.FISHING
            
            case FishState.FISHING:
                if self.ui_recognizer.check_end_fishing_ui(current_img):
                    self.current_state = FishState.END_FISHING
                elif self.ui_recognizer.check_instant_kill_ui(current_img):
                    self.current_state = FishState.INSTANT_KILL
 
            case FishState.INSTANT_KILL:
                if self.ui_recognizer.check_end_fishing_ui(current_img):
                    self.current_state = FishState.END_FISHING
            
            case FishState.END_FISHING:
                if self.ui_recognizer.check_cast_rod_ui(current_img):
                    self.current_state = FishState.CAST_ROD
        
        if old_state != self.current_state:
            logging.info(f"页面状态变化: {old_state} -> {self.current_state}")
    
    def reset_state_flags(self) -> None:
        """重置所有状态标志"""
        self._setup_state_flags()
        
    def _determine_initial_state(self, current_img: np.ndarray) -> FishState:
        """调整初始状态，兼容从任何页面启动程序
        
        Args:
            current_img: 当前屏幕截图
        """
 
        state = FishState.START_FISHING
        # 检查各个UI界面，设置对应的状态
        if self.ui_recognizer.check_start_fishing_ui(current_img):
            state = FishState.START_FISHING
        elif self.ui_recognizer.check_cast_rod_ui(current_img):
            state = FishState.CAST_ROD
        elif self.ui_recognizer.check_no_bait_ui(current_img):
            state = FishState.NO_BAIT
        elif self.ui_recognizer.check_spear_fish_ui(current_img):
            state = FishState.SPEAR_FISH
        elif self.ui_recognizer.check_catch_fish_ui(current_img):
            state = FishState.CATCH_FISH
        elif self.ui_recognizer.check_fishing_ui(current_img):
            state = FishState.FISHING
        elif self.ui_recognizer.check_end_fishing_ui(current_img):
            state = FishState.END_FISHING
        elif self.ui_recognizer.check_instant_kill_ui(current_img):
            state = FishState.INSTANT_KILL
        else:
            # 如果都不匹配，默认设置为开始钓鱼状态
            state = FishState.START_FISHING
            
        logging.info(f"初始页面状态调整为: {state}")
        return state
 
class FishingPositionDetector:
    """负责位置检测的类"""
    
    def __init__(self, config: GameConfig):
        self.config = config
 
    def _find_template_with_retry(
        self,
        template_path: str,
        threshold: float = 0.8,
        position: Tuple[float, float] = (0.5, 0.5),
        screenshot_region: Optional[Tuple[int, int, int, int]] = None,
        retries: int = 10,
        retry_delay: float = 0.2,
    ) -> Tuple[int, int]:
        """重试模板匹配，降低瞬时识别失败造成的卡死概率。"""
        region = screenshot_region or self.config.window_size
        template = ImageProcessor.load_template(template_path)
 
        last_error: Optional[Exception] = None
        for _ in range(retries):
            try:
                img = ImageProcessor.get_screenshot(region)
                return ImageProcessor.match_template(
                    img, template, threshold=threshold, position=position
                )
            except Exception as e:
                last_error = e
                time.sleep(retry_delay)
 
        raise RuntimeError(
            f"模板识别失败: {template_path}, 重试次数={retries}, 最后错误={last_error}"
        )
    
    def detect_start_fishing_pos(self) -> None:
        """检测开始钓鱼按钮位置"""
        pos = self._find_template_with_retry(str(Config.START_FISH_BUTTON))
        self.config.start_fishing_pos = (
            pos[0] + self.config.window_size[0],
            pos[1] + self.config.window_size[1]
        )
        ConfigManager.write_yaml(self.config.__dict__)
    
    def detect_fishing_positions(self) -> None:
        """检测钓鱼相关位置"""
        rod_pos = self._find_template_with_retry(str(Config.PUSH_ROD_BUTTON), threshold=0.75)
        pressure_pos = self._find_template_with_retry(
            str(Config.PRESSURE_IMAGE), threshold=0.75, position=(0.25, 0.5)
        )
        
        self.config.rod_position = (
            rod_pos[0] + self.config.window_size[0],
            rod_pos[1] + self.config.window_size[1]
        )
        self.config.pressure_indicator_pos = (
            pressure_pos[0] + self.config.window_size[0],
            pressure_pos[1] + self.config.window_size[1]
        )
        
        self.config.low_pressure_color = pyautogui.pixel(*self.config.pressure_indicator_pos)
        self.config.original_rod_color = pyautogui.pixel(*self.config.rod_position)
        
        ConfigManager.write_yaml(self.config.__dict__)
    
    def detect_tijian_pos(self) -> None:
        """检测提竿按钮位置"""
        pos = self._find_template_with_retry(str(Config.TIJIAN_IMAGE), threshold=0.6)
        self.config.tijian_pos = (
            pos[0] + self.config.window_size[0],
            pos[1] + self.config.window_size[1]
        )
        ConfigManager.write_yaml(self.config.__dict__)
 
    def detect_use_button_pos(self) -> None:
        """检测使用按钮位置"""
        pos = self._find_template_with_retry(str(Config.USE_BUTTON))
        self.config.use_bait_button_pos = (
            pos[0] + self.config.window_size[0],
            pos[1] + self.config.window_size[1]
        )
        ConfigManager.write_yaml(self.config.__dict__)
    
    def detect_retry_button_pos(self) -> None:
        """检测再次钓鱼按钮位置"""
        pos = self._find_template_with_retry(str(Config.RETRY_BUTTON))
        self.config.retry_button_center = (
            pos[0] + self.config.window_size[0],
            pos[1] + self.config.window_size[1]
        )
        ConfigManager.write_yaml(self.config.__dict__)
    
    def detect_direction_icons(self) -> None:
        """检测方向图标位置"""
        bottom_half_size = self._get_bottom_half_region()
        bottom_half_img = ImageProcessor.get_screenshot(bottom_half_size)
        
        self.config.direction_icon_positions = {}
        for dir_icon_path in Config.DIRECTION_ICONS:
            dir_icon = ImageProcessor.load_template(str(dir_icon_path))
            pos = ImageProcessor.match_template(bottom_half_img, dir_icon)
            name = dir_icon_path.stem
            self.config.direction_icon_positions[name] = (
                pos[0] + bottom_half_size[0],
                pos[1] + bottom_half_size[1]
            )
        
        ConfigManager.write_yaml(self.config.__dict__)
 
    def _get_top_half_region(self) -> Tuple[int, int, int, int]:
        """获取窗口上半区域(x, y, width, height)。"""
        x, y, w, h = self.config.window_size
        top_h = h // 2
        return (x, y, w, top_h)
 
    def _get_bottom_half_region(self) -> Tuple[int, int, int, int]:
        """获取窗口下半区域(x, y, width, height)。"""
        x, y, w, h = self.config.window_size
        top_h = h // 2
        return (x, y + top_h, w, h - top_h)
 
 
class FishingActionExecutor:
    """负责执行具体的钓鱼动作的类"""
    
    def __init__(self, config: GameConfig):
        self.config = config
        self.fishing_click_time = 0
        self.rod_retrieve_time = 0
    
    def handle_default_state(self) -> None:
        """处理默认状态"""
        MouseController.click(self.config.start_fishing_pos)
    
    def handle_cast_rod_state(self) -> None:
        """处理抛竿状态"""
        MouseController.press_mouse_move(
            self.config.start_fishing_pos[0],
            self.config.start_fishing_pos[1],
            0, -100
        )
    
    def handle_no_bait_state(self) -> None:
        """处理鱼饵不足状态"""
        MouseController.click(self.config.use_bait_button_pos)
    
    def handle_spear_fish(self) -> None:
        """处理刺鱼阶段：检测到红色区域时点击提竿"""
        current_img = ImageProcessor.get_screenshot(self.config.window_size)
        red_zone = ImageProcessor.load_template(str(Config.RED_ZONE_IMAGE))
        if ImageProcessor.is_match_template(current_img, red_zone, threshold=0.7):
            MouseController.click(self.config.tijian_pos)
            logging.info("刺鱼：检测到红色区域，点击提竿")
    
    def handle_catch_fish_state(self) -> None:
        """处理捕鱼状态"""
        click_interval = Config.FISHING_CLICK_INTERVAL * 3
        current_time = time.time()
        if current_time - self.fishing_click_time >= click_interval:
            MouseController.click(self.config.start_fishing_pos)
            self.fishing_click_time = current_time
    
    def handle_ongoing_fishing(self) -> None:
        """处理持续钓鱼状态"""
        current_time = time.time()
        click_interval = Config.FISHING_CLICK_INTERVAL
        pressure_check_interval = click_interval * 3
 
        # 检查收杆
        if current_time - self.rod_retrieve_time > Config.ROD_RETRIEVE_INTERVAL:
            self.handle_rod_retrieve()
 
        # 检查点击操作
        if current_time - self.fishing_click_time >= click_interval:
            current_pressure_color = pyautogui.pixel(*self.config.pressure_indicator_pos)
            # 压力条颜色改变, 增加点击保护间隔
            if current_pressure_color != self.config.low_pressure_color:
                self.fishing_click_time = current_time + pressure_check_interval
            # 压力条颜色未改变, 点击收杆
            else:
                MouseController.click(self.config.start_fishing_pos) 
                self.fishing_click_time = current_time
 
        # 拉竿检查
        current_rod_color = pyautogui.pixel(*self.config.rod_position)
        if current_rod_color != self.config.original_rod_color:
            self.handle_rod_movement()
    
    def handle_rod_movement(self) -> None:
        """处理拉杆移动"""
        MouseController.press_mouse_move(
            self.config.rod_position[0],
            self.config.rod_position[1],
            100, 0
        )
        MouseController.press_mouse_move(
            self.config.rod_position[0],
            self.config.rod_position[1],
            -100, 0
        )
    
    def handle_rod_retrieve(self) -> None:
        """处理收杆"""
        MouseController.press_mouse_move(
            self.config.start_fishing_pos[0],
            self.config.start_fishing_pos[1],
            0, -75
        )
        self.rod_retrieve_time = time.time()
    
    def handle_end_fishing_state(self) -> None:
        """处理结束钓鱼状态"""
        MouseController.click(self.config.retry_button_center)
    
    def handle_direction_sequence(self) -> None:
        """处理方向序列"""
        x, y, w, h = self.config.window_size
        top_half_size = (x, y, w, h // 2)
        top_half_img = ImageProcessor.get_screenshot(top_half_size)
        
        all_icons_dict = {}
        for dir_icon_path in Config.DIRECTION_ICONS:
            dir_icon = ImageProcessor.load_template(str(dir_icon_path))
            res = cv2.matchTemplate(top_half_img, dir_icon, cv2.TM_CCOEFF_NORMED)
            res_loc = np.where(res >= 0.8)
            if len(res_loc[0]) > 0:
                points = list(zip(*res_loc[::-1]))
                classified_points = self._classify_positions(points)
                for point in classified_points:
                    all_icons_dict[point] = dir_icon_path.stem
        
        # 按x坐标排序
        all_icons_list = sorted(all_icons_dict.items(), key=lambda x: x[0][0])
        for pos, name in all_icons_list:
            logging.info(f"{name}, 位置: {pos}")
            click_pos = self.config.direction_icon_positions[name]
            MouseController.click(click_pos)
    
    @staticmethod
    def _classify_positions(point_list: list) -> list:
        """对识别出来的所有位置进行分类"""
        result_points = []
        for i in range(len(point_list)):
            point_set = set()
            if point_list[i] is None:
                continue
            point_set.add(point_list[i])
            for j in range(i + 1, len(point_list)):
                if point_list[j] is None:
                    continue
                if (abs(point_list[i][0] - point_list[j][0]) < 10 and 
                    abs(point_list[i][1] - point_list[j][1]) < 10):
                    point_set.add(point_list[j])
                    point_list[j] = None
            if len(point_set) > 1:
                average_x = int(sum([x[0] for x in point_set]) / len(point_set))
                average_y = int(sum([x[1] for x in point_set]) / len(point_set))
                result_points.append((average_x, average_y))
        return result_points
 
 
class FishingGame:
    """钓鱼游戏主类"""
    
    def __init__(
        self,
        window_title: Optional[str] = None,
        window_size: Optional[Tuple[int, int, int, int]] = None,
        profile: Optional[str] = None,
    ):
        self._window_title_override = window_title
        self._window_size_override = window_size
        self._profile_name = profile
        self.config = self._load_config()
        self.position_detector = FishingPositionDetector(self.config)
        self.action_executor = FishingActionExecutor(self.config)
        self.should_exit = Event()
        self.state_check_thread: Optional[Thread] = None
        self.state_check_error: Optional[Exception] = None
 
        ImageProcessor.preload_all_templates()
        current_img = ImageProcessor.get_screenshot(self.config.window_size)
        self.state_manager = FishingStateManager(current_img)
    
    def _load_config(self) -> GameConfig:
        """加载游戏配置"""
        if not Config.CONFIG_FILE.exists():
            config_dict = {}
        else:
            config_dict = ConfigManager.read_yaml()
            # 兼容历史配置：丢弃当前数据类未定义字段。
            allowed_keys = set(GameConfig.__annotations__.keys())
            config_dict = {k: v for k, v in config_dict.items() if k in allowed_keys}
 
        if self._profile_name:
            profiles = ConfigManager.read_profiles()
            profile_data = profiles.get(self._profile_name)
            if not isinstance(profile_data, dict):
                available = ", ".join(sorted(profiles.keys()))
                raise ValueError(
                    f"未找到配置: {self._profile_name}，可用配置: {available or '无'}"
                )
            if "window_title" in profile_data:
                config_dict["window_title"] = profile_data["window_title"]
            if "window_size" in profile_data:
                config_dict["window_size"] = profile_data["window_size"]
        
        # 设置默认窗口标题
        if 'window_title' not in config_dict:
            config_dict['window_title'] = Config.WINDOW_TITLE
 
        # 每次启动强制清空所有检测位置，防止残缺配置导致卡死
        config_dict['window_title'] = self._window_title_override or config_dict['window_title']
        config_dict['window_size'] = self._window_size_override or config_dict.get('window_size', Config.WINDOW_SIZE)
        config_dict['start_fishing_pos'] = None
        config_dict['rod_position'] = None
        config_dict['pressure_indicator_pos'] = None
        config_dict['low_pressure_color'] = None
        config_dict['original_rod_color'] = None
        config_dict['direction_icon_positions'] = None
        config_dict['retry_button_center'] = None
        config_dict['use_bait_button_pos'] = None
        config_dict['tijian_pos'] = None
        config_dict = self._normalize_config_types(config_dict)
        
        return GameConfig(**config_dict)
 
    @staticmethod
    def _normalize_config_types(config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """标准化配置类型，兼容 list/tuple 与旧配置。"""
        tuple4_fields = {"window_size"}
        tuple2_fields = {
            "start_fishing_pos",
            "rod_position",
            "pressure_indicator_pos",
            "retry_button_center",
            "use_bait_button_pos",
            "tijian_pos",
        }
        tuple3_fields = {"low_pressure_color", "original_rod_color"}
 
        for field in tuple4_fields:
            value = config_dict.get(field)
            if isinstance(value, list):
                config_dict[field] = tuple(value)
        for field in tuple2_fields:
            value = config_dict.get(field)
            if isinstance(value, list):
                config_dict[field] = tuple(value)
        for field in tuple3_fields:
            value = config_dict.get(field)
            if isinstance(value, list):
                config_dict[field] = tuple(value)
 
        positions = config_dict.get("direction_icon_positions")
        if isinstance(positions, dict):
            normalized = {}
            for key, value in positions.items():
                if isinstance(value, list):
                    normalized[key] = tuple(value)
                else:
                    normalized[key] = value
            config_dict["direction_icon_positions"] = normalized
 
        return config_dict
 
    def _get_state_check_region(self, state: FishState) -> Tuple[int, int, int, int]:
        x, y, w, h = self.config.window_size
        # 仅 SPEAR_FISH 限制上半屏：tijian 按钮在上半屏且无需检测下半屏元素。
        # FISHING / INSTANT_KILL 需要检测下半屏的 retry 按钮，不能裁剪。
        if state == FishState.SPEAR_FISH:
            return (x, y, w, h // 2)
        return self.config.window_size
    
    def check_current_UI(self) -> None:
        """检查当前游戏界面状态"""
        # 添加热键监听器（try/except防止重复注册）
        try:
            keyboard.add_hotkey('esc', self.should_exit.set, suppress=True)
        except Exception:
            keyboard.unhook_all()
            keyboard.add_hotkey('esc', self.should_exit.set, suppress=True)
 
        try:
            while not self.should_exit.is_set():
                check_interval = 0.01 if self.state_manager.current_state in (FishState.FISHING, FishState.SPEAR_FISH) else 0.05
                time.sleep(check_interval)
                # sleep 后重新取最新 state，避免用旧状态算出错误截图区域
                current_state = self.state_manager.current_state
                region = self._get_state_check_region(current_state)
                current_img = ImageProcessor.get_screenshot(region)
                self.state_manager.update_state(current_img)
        except Exception as e:
            self.state_check_error = e
            logging.error(f"状态检测线程异常: {e}")
            self.should_exit.set()
        finally:
            try:
                keyboard.unhook_all()
            except Exception:
                pass
            self.state_manager.current_state = FishState.EXIT
    
    def _handle_state(self) -> None:
        """处理当前状态"""
        match self.state_manager.current_state:
            case FishState.START_FISHING if self.state_manager.first_start_fishing:
                if not self.config.start_fishing_pos:
                    self.position_detector.detect_start_fishing_pos()
                self.action_executor.handle_default_state()
                self.state_manager.first_start_fishing = False
            
            case FishState.CAST_ROD if self.state_manager.first_cast_rod:
                self.action_executor.handle_cast_rod_state()
                self.state_manager.first_cast_rod = False
                self.state_manager.first_retry = True
            
            case FishState.NO_BAIT if self.state_manager.first_no_bait:
                if not self.config.use_bait_button_pos:
                    self.position_detector.detect_use_button_pos()
                self.action_executor.handle_no_bait_state()
                self.state_manager.first_no_bait = False
                self.state_manager.first_cast_rod = True
            
            case FishState.SPEAR_FISH:
                if not self.config.tijian_pos:
                    self.position_detector.detect_tijian_pos()
                self.action_executor.handle_spear_fish()
            
            case FishState.CATCH_FISH:
                self.action_executor.handle_catch_fish_state()
            
            case FishState.FISHING:
                if not self.config.rod_position or not self.config.pressure_indicator_pos:
                    self.position_detector.detect_fishing_positions()
                self.action_executor.handle_ongoing_fishing()
            
            case FishState.END_FISHING if self.state_manager.first_retry:
                if not self.config.retry_button_center:
                    self.position_detector.detect_retry_button_pos()
                self.action_executor.handle_end_fishing_state()
                self.state_manager.reset_state_flags()
                self.state_manager.first_retry = False
            
            case FishState.INSTANT_KILL if self.state_manager.first_instant_kill:
                if not self.config.direction_icon_positions:
                    self.position_detector.detect_direction_icons()
                self.action_executor.handle_direction_sequence()
                self.state_manager.first_instant_kill = False
 
    def run(self) -> None:
        """运行游戏主循环"""
        try:
            pyautogui.PAUSE = Config.FISHING_CLICK_INTERVAL / 2
            self.should_exit.clear()
            WindowManager.handle_window(self.config)
            self.state_check_thread = Thread(target=self.check_current_UI, daemon=True)
            self.state_check_thread.start()
            
            while self.state_manager.current_state != FishState.EXIT:
                if self.state_check_error:
                    raise RuntimeError("状态检测线程异常退出") from self.state_check_error
                self._handle_state()
                time.sleep(0.01)
            
            ConfigManager.write_yaml(self.config.__dict__)
            logging.info("游戏结束")
            
        except Exception as e:
            logging.error(f"游戏运行出错: {str(e)}")
            raise
        finally:
            self.should_exit.set()
            if self.state_check_thread and self.state_check_thread.is_alive():
                self.state_check_thread.join(timeout=2)
 
 
def resolve_runtime_window_config(args: argparse.Namespace) -> Tuple[str, Tuple[int, int, int, int]]:
    """解析最终窗口配置（默认 < 配置 < 命令行）。"""
    window_title = Config.WINDOW_TITLE
    window_size: Tuple[int, int, int, int] = Config.WINDOW_SIZE
 
    if args.profile:
        profiles = ConfigManager.read_profiles()
        profile_data = profiles.get(args.profile)
        if not isinstance(profile_data, dict):
            available = ", ".join(sorted(profiles.keys()))
            raise ValueError(f"未找到配置: {args.profile}，可用配置: {available or '无'}")
 
        title_from_profile = profile_data.get("window_title")
        if isinstance(title_from_profile, str) and title_from_profile.strip():
            window_title = title_from_profile
 
        size_from_profile = profile_data.get("window_size")
        if isinstance(size_from_profile, (list, tuple)) and len(size_from_profile) == 4:
            window_size = tuple(int(v) for v in size_from_profile)
 
    if args.window_title:
        window_title = args.window_title
    if args.window_size:
        window_size = args.window_size
 
    return window_title, window_size
 
 
def run_check_mode(args: argparse.Namespace) -> bool:
    """运行启动前体检。"""
    print("== 检查模式 ==")
    all_ok = True
 
    try:
        Config.ensure_runtime_ready()
        print("[通过] 资源文件检查通过")
    except Exception as e:
        all_ok = False
        print(f"[失败] 资源文件检查失败: {e}")
 
    try:
        window_title, window_size = resolve_runtime_window_config(args)
        print(f"[通过] 窗口配置解析通过: 标题={window_title}, 区域={window_size}")
    except Exception as e:
        all_ok = False
        print(f"[失败] 窗口配置解析失败: {e}")
        return all_ok
 
    try:
        hwnd = WindowManager.find_window(window_title)
        if not hwnd:
            all_ok = False
            print(f"[失败] 未找到窗口: {window_title}")
        else:
            rect = WindowManager.get_window_rect(hwnd)
            print(f"[通过] 找到窗口句柄: {hwnd}, 区域={rect}")
    except Exception as e:
        all_ok = False
        print(f"[失败] 窗口检查失败: {e}")
 
    print("检查结果:", "通过" if all_ok else "失败")
    return all_ok
 
 
def main():
    """主函数"""
    try:
        args = parse_args()
 
        if args.save_profile:
            window_title, window_size = resolve_runtime_window_config(args)
            ConfigManager.save_profile(args.save_profile, window_title, window_size)
            print(f"已保存配置: {args.save_profile}")
            print(f"- 窗口标题: {window_title}")
            print(f"- 窗口区域: {window_size}")
            if not args.check_mode:
                return
 
        if args.check_mode:
            is_ok = run_check_mode(args)
            if not is_ok:
                raise SystemExit(1)
            return
 
        Config.ensure_runtime_ready()
        game = FishingGame(
            window_title=args.window_title,
            window_size=args.window_size,
            profile=args.profile,
        )
        game.run()
    except Exception as e:
        logging.error(f"程序运行出错: {str(e)}")
        raise
 
 
def parse_window_size(value: str) -> Tuple[int, int, int, int]:
    """解析窗口区域参数：x,y,width,height。"""
    parts = [item.strip() for item in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("窗口区域格式错误，应为 x,y,width,height")
    try:
        x, y, w, h = (int(part) for part in parts)
    except ValueError as e:
        raise argparse.ArgumentTypeError("窗口区域必须全部为整数") from e
    if w <= 0 or h <= 0:
        raise argparse.ArgumentTypeError("窗口区域的 width/height 必须大于 0")
    return (x, y, w, h)
 
 
def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="TKAutoFisher 自动钓鱼脚本")
    parser.add_argument(
        "--窗口标题",
        "--window-title",
        dest="window_title",
        help="模拟器窗口标题（默认读取配置或内置默认值）",
    )
    parser.add_argument(
        "--窗口区域",
        "--window-size",
        dest="window_size",
        type=parse_window_size,
        help="窗口区域，格式为 x,y,width,height",
    )
    parser.add_argument(
        "--配置",
        "--profile",
        dest="profile",
        help="运行配置名称（来自 generate/profiles.yaml）",
    )
    parser.add_argument(
        "--保存配置",
        "--save-profile",
        dest="save_profile",
        help="保存当前参数到指定配置并退出（默认只保存不启动）",
    )
    parser.add_argument(
        "--检查模式",
        "--check-mode",
        dest="check_mode",
        action="store_true",
        help="执行启动前检查（资源、配置、窗口）并退出",
    )
    return parser.parse_args()
 
 
if __name__ == '__main__':
    main()
