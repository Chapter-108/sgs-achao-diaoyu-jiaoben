import time
import logging
from typing import Any, Optional, Tuple

import win32con
import win32gui


class WindowManager:
    """窗口管理类，处理窗口相关操作。"""

    @staticmethod
    def find_window(title: str) -> int:
        return win32gui.FindWindow(None, title)

    @staticmethod
    def get_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
        return win32gui.GetWindowRect(hwnd)

    @staticmethod
    def bring_to_front(hwnd: int, retries: int = 5, retry_delay: float = 0.2) -> None:
        last_error: Optional[Exception] = None
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        for _ in range(retries):
            try:
                win32gui.SetForegroundWindow(hwnd)
                return
            except Exception as e:
                last_error = e
                time.sleep(retry_delay)
        logging.warning(f"窗口前置失败，继续执行: {last_error}")

    @staticmethod
    def handle_window(config: Any) -> None:
        hwnd = WindowManager.find_window(config.window_title)
        if not hwnd:
            raise ValueError(f"未找到标题为 {config.window_title} 的窗口")

        WindowManager.bring_to_front(hwnd)
        win32gui.SetWindowPos(hwnd, None, *config.window_size, win32con.SWP_SHOWWINDOW)
        time.sleep(0.5)
