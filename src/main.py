import os
from src.utils.__init__ import capture_screenshot
from src.utils.__init__ import click_image_in_screenshot

if __name__ == "__main__":
    # 获取当前文件（main.py）所在的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建相对于 public 文件夹的路径
    public_folder = os.path.join(script_dir, '..', 'public', 'images')
    template_image_path = os.path.join(public_folder, 'bili.png')
    # 规范化路径
    template_image_path = os.path.normpath(template_image_path)

    # 选择窗口标题或全屏
    window_title = "Google Chrome"  # 如果不需要特定窗口，设置为 None

    screenshot, offset_left, offset_top = capture_screenshot()

    click_image_in_screenshot(template_image_path, screenshot, offset_left, offset_top)
