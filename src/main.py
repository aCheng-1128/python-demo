import sys
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import pyautogui
from src.utils import capture_screenshot, find_image_in_screenshot
from PIL import Image, ImageTk
import keyboard

# 全局变量
target_images_paths = []
stop_timer_duration = 30
stop_flag = False
max_runtime_duration = 30
current_image_index = 0
click_interval = 1000  # 默认点击间隔时间为1000毫秒（1秒）

# 获取基础路径
base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent.parent

def stop_program():
    """停止程序"""
    global stop_flag
    stop_flag = True
    print("Stopping the program.")
    messagebox.showinfo("停止", "程序已停止")
    # 重新显示完整界面
    root.deiconify()  # 使窗口重新可见
    root.state('normal')  # 恢复窗口为正常状态

def stop_program_after_max_runtime():
    """在最大运行时间到达后强制停止程序"""
    global stop_flag
    if not stop_flag:
        print("最大运行时间到达，强制停止程序。")
        messagebox.showinfo("停止", "程序已强制停止")
        stop_program()

def select_images():
    """选择并复制目标图片到指定文件夹"""
    global target_images_paths
    file_paths = filedialog.askopenfilenames(
        title="选择目标图片",
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")]
    )

    images_folder = Path(base_path) / 'public' / 'images'
    images_folder.mkdir(parents=True, exist_ok=True)

    for path in file_paths:
        target_image_path = images_folder / Path(path).name
        try:
            with open(path, 'rb') as src_file, open(target_image_path, 'wb') as dst_file:
                dst_file.write(src_file.read())
            target_images_paths.append(str(target_image_path))
            display_image(target_image_path)
        except Exception as e:
            print(f"Error copying file {path}: {e}")

def display_image(image_path):
    """在GUI上显示图片"""
    try:
        image_frame = tk.Frame(images_frame)
        image_frame.pack(side=tk.LEFT, padx=5, pady=5)

        image = Image.open(image_path)
        image.thumbnail((100, 100))
        photo = ImageTk.PhotoImage(image)

        img_label = tk.Label(image_frame, image=photo)
        img_label.image = photo
        img_label.pack(side=tk.LEFT)

        delete_button = tk.Button(image_frame, text="删除", command=lambda: delete_image(image_path, image_frame))
        delete_button.pack(side=tk.LEFT, padx=5)

    except Exception as e:
        print(f"Error displaying image {image_path}: {e}")

def delete_image(image_path, image_frame):
    """删除图片并更新GUI"""
    try:
        image_path = str(Path(image_path).resolve())

        if os.path.exists(image_path) and image_path in target_images_paths:
            target_images_paths.remove(image_path)
            os.remove(image_path)
            image_frame.destroy()
            print(f"Deleted image: {image_path}")
        else:
            print(f"Image not found or not in list: {image_path}")

    except Exception as e:
        print(f"Error deleting image {image_path}: {e}")

def click_target_in_screenshot_onshow(template_path, threshold):
    """在截图中寻找目标图像并点击"""
    global stop_flag, current_image_index, click_interval
    while not stop_flag:
        if current_image_index >= len(target_images_paths):
            current_image_index = 0

        image_path = target_images_paths[current_image_index]
        screenshot, offset_left, offset_top = capture_screenshot()
        locations, w, h = find_image_in_screenshot(image_path, screenshot, threshold)
        if locations:
            for x, y in locations:
                screen_x = x + offset_left + w // 2
                screen_y = y + offset_top + h // 2
                pyautogui.click(screen_x, screen_y)
                print(f"点击位置 ({screen_x}, {screen_y})")
        else:
            print(f"未找到图像 {image_path}，等待下一次检查。")

        current_image_index += 1
        pyautogui.sleep(click_interval / 1000.0)  # 转换为秒

    print("循环已停止。")

def start_program():
    """开始程序执行"""
    global stop_timer_duration, stop_flag, current_image_index, click_interval
    stop_flag = False
    current_image_index = 0
    try:
        timer_value = timer_entry.get().strip()
        click_interval_value = click_interval_entry.get().strip()

        if not timer_value.isdigit() or int(timer_value) <= 0:
            raise ValueError("倒计时时间必须是一个大于0的整数！")
        if not click_interval_value.isdigit() or int(click_interval_value) < 0:
            raise ValueError("点击间隔时间必须是一个非负整数！")

        global stop_timer_duration
        stop_timer_duration = int(timer_value)
        click_interval = int(click_interval_value)

        # 最小化窗口
        root.update_idletasks()
        root.state('iconic')

        stop_timer = threading.Timer(stop_timer_duration, stop_program)
        stop_timer.start()

        max_runtime_timer = threading.Timer(max_runtime_duration, stop_program_after_max_runtime)
        max_runtime_timer.start()

        print("target_images_paths", target_images_paths)
        for image_path in target_images_paths:
            if stop_flag:
                break
            click_target_in_screenshot_onshow(image_path, 0.8)

        stop_timer.cancel()
        max_runtime_timer.cancel()

    except ValueError as e:
        messagebox.showerror("错误", str(e))
    except Exception as e:
        messagebox.showerror("错误", str(e))

def on_key_press(event):
    """按键事件处理"""
    if event.keysym == 'Escape':
        stop_program()

# 监听全局按键（需要安装 keyboard 库）
keyboard.add_hotkey('esc', stop_program)

# GUI 设置
root = tk.Tk()
root.title("目标图片匹配点击工具")
root.geometry("800x700")

upload_button = tk.Button(root, text="上传目标图片", command=select_images)
upload_button.pack(pady=10)

images_frame = tk.Frame(root)
images_frame.pack(pady=10, fill=tk.BOTH, expand=True)

# 提示文本
label = tk.Label(root, text="可按Esc键强制停止程序",
                 font=("Arial", 16, "bold"),
                 fg="red",
                 bg="yellow",
                 padx=10, pady=10)
label.pack(pady=20)

tk.Label(root, text="设置程序停止的倒计时时间（秒）:").pack(pady=5)
timer_entry = tk.Entry(root)
timer_entry.insert(0, stop_timer_duration)
timer_entry.pack(pady=5)

tk.Label(root, text="设置点击间隔时间（毫秒）:").pack(pady=5)
click_interval_entry = tk.Entry(root)
click_interval_entry.insert(0, click_interval)
click_interval_entry.pack(pady=5)

start_button = tk.Button(root, text="开始", command=lambda: threading.Thread(target=start_program).start())
start_button.pack(pady=10)

stop_button = tk.Button(root, text="停止", command=stop_program)
stop_button.pack(pady=10)

root.mainloop()
