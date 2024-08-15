import pyautogui
from src.utils.image_matching import find_image_in_screenshot

def click_image_in_screenshot(template_path, screenshot, offset_left, offset_top, threshold=0.8):
    locations, w, h = find_image_in_screenshot(template_path, screenshot, threshold)
    if locations:
        for x, y in locations:
            # 将点击位置的坐标转换为屏幕坐标
            screen_x, screen_y = x + offset_left + w // 2, y + offset_top + h // 2
            pyautogui.click(screen_x, screen_y)
            print(f"点击位置 ({screen_x}, {screen_y})")
    else:
        print("未找到图像，未进行点击操作。")
