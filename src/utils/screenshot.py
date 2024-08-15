import os
import pyautogui
import pygetwindow as gw
from PIL import Image
import numpy as np
import time
import re

def capture_screenshot(window_title=None):
    """根据是否提供窗口标题截取指定窗口的截图，如果没有提供窗口标题则截取全屏"""
    if window_title:
        title = get_matching_window_title(window_title)
        if title is None:
            return None, None, None

        # 获取窗口
        window = gw.getWindowsWithTitle(title)[0]

        # 确保窗口是可见的
        if window.isMinimized:
            window.restore()

        # 确保窗口在前台
        window.activate()

        # 确保窗口未被隐藏
        if not window.isActive:
            window.activate()
            time.sleep(1)

        # 获取窗口的位置和大小
        left, top, right, bottom = window.left, window.top, window.right, window.bottom

        # 截取整个屏幕的截图
        screenshot = pyautogui.screenshot()

        # 使用 Pillow 裁剪出窗口的区域
        screenshot_pil = Image.fromarray(np.array(screenshot))
        window_screenshot = screenshot_pil.crop((left, top, right, bottom))

        return window_screenshot, left, top
    else:
        # 截取全屏
        screenshot = pyautogui.screenshot()
        screenshot_pil = Image.fromarray(np.array(screenshot))
        return screenshot_pil, 0, 0

def remove_invisible_chars(text):
    """移除字符串中的控制字符和不可见字符"""
    return re.sub(
        r'[\u200b\u200c\u200d\u200e\u200f\u202a\u202b\u202c\u202d\u2060\u2061\u2062\u2063\u2064\u206a\u206b\u206c\u206d\ufeff]',
        '', text)

def get_matching_window_title(partial_title):
    """获取包含指定部分标题的窗口标题"""
    all_titles = gw.getAllTitles()
    partial_title_pattern = re.compile(re.escape(partial_title), re.IGNORECASE)

    for title in all_titles:
        clean_title = remove_invisible_chars(title)
        if partial_title_pattern.search(clean_title):
            return title  # 返回第一个匹配的窗口标题
    print(f"未找到包含 '{partial_title}' 的窗口。")
    return None
