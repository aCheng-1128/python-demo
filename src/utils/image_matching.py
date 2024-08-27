import cv2
import numpy as np
from PIL import Image

def find_image_in_screenshot(template_path, screenshot, threshold):
    print(f"尝试从以下路径加载模板图像: {template_path}")
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print("加载图像失败。请检查文件路径。")
        return None, None, None
    w, h = template.shape[::-1]

    # 将截图转换为灰度图像
    screenshot_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)

    # 模板匹配
    res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    # 收集所有匹配的位置
    locations = list(zip(*loc[::-1]))
    if locations:
        # 去重（根据模板图像的宽度和高度去重）
        unique_locations = filter_unique_locations(locations, w, h)
        # 按照x坐标（从左到右），然后按照y坐标（从上到下）排序
        sorted_locations = sorted(unique_locations, key=lambda x: (x[0], x[1]))
        return sorted_locations, w, h
    else:
        return None, w, h

def filter_unique_locations(locations, w, h, threshold=30):
    """根据模板图像的宽度和高度去除重复的位置"""
    unique_locations = []
    for loc in locations:
        x, y = loc
        if not any(abs(x - ux) < w and abs(y - uy) < h for ux, uy in unique_locations):
            unique_locations.append(loc)
    return unique_locations