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
import time

class ImageClickerApp:
    def __init__(self, root):
        self.root = root
        self.target_images_paths = []
        self.stop_event = threading.Event()
        self.stop_timer_duration = 3600  # 默认1小时
        self.click_interval = 1000
        self.current_image_index = 0
        self.running = False

        self.setup_gui()
        self.load_existing_images()
        self.setup_hotkeys()

    def setup_gui(self):
        self.root.title("目标图片匹配点击工具")
        self.root.geometry("800x800")

        # 设置窗口图标
        icon_path = Path(self.get_base_path()) / 'assets' / 'app_icon.ico'
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))
        else:
            print(f"图标文件未找到: {icon_path}")

        upload_button = tk.Button(self.root, text="上传目标图片", command=self.select_images)
        upload_button.pack(pady=10)

        self.images_frame = tk.Frame(self.root)
        self.images_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        label = tk.Label(self.root, text="可按Ctrl + c键强制停止程序",
                         font=("Arial", 16, "bold"), fg="red", bg="yellow", padx=10, pady=10)
        label.pack(pady=20)

        tk.Label(self.root, text="设置程序停止的倒计时(以秒为单位，默认1小时):").pack(pady=5)
        self.timer_entry = tk.Entry(self.root)
        self.timer_entry.insert(0, self.stop_timer_duration)
        self.timer_entry.pack(pady=5)

        tk.Label(self.root, text="设置点击间隔时间（毫秒）:").pack(pady=5)
        self.click_interval_entry = tk.Entry(self.root)
        self.click_interval_entry.insert(0, self.click_interval)
        self.click_interval_entry.pack(pady=5)

        start_button = tk.Button(self.root, text="开始", command=self.start_program_thread)
        start_button.pack(pady=10)

        stop_button = tk.Button(self.root, text="停止", command=self.stop_program)
        stop_button.pack(pady=10)

    def setup_hotkeys(self):
        keyboard.add_hotkey('ctrl+c', self.hotkey_stop_program)

    def load_existing_images(self):
        images_folder = Path(self.get_base_path()) / 'public' / 'images'
        if images_folder.exists():
            for image_path in images_folder.iterdir():
                if image_path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.bmp'}:
                    self.target_images_paths.append(str(image_path))
                    self.display_image(image_path)

    def select_images(self):
        file_paths = filedialog.askopenfilenames(
            title="选择目标图片",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        images_folder = Path(self.get_base_path()) / 'public' / 'images'
        images_folder.mkdir(parents=True, exist_ok=True)

        for path in file_paths:
            target_image_path = images_folder / Path(path).name
            try:
                with open(path, 'rb') as src_file:
                    with open(target_image_path, 'wb') as dst_file:
                        dst_file.write(src_file.read())
                self.target_images_paths.append(str(target_image_path))
                self.display_image(target_image_path)
            except IOError as e:
                print(f"Error copying file {path}: {e}")

    def display_image(self, image_path):
        try:
            image_frame = tk.Frame(self.images_frame)
            image_frame.pack(side=tk.LEFT, padx=5, pady=5)

            image = Image.open(image_path)
            image.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(image)

            img_label = tk.Label(image_frame, image=photo)
            img_label.image = photo
            img_label.pack(side=tk.LEFT)

            delete_button = tk.Button(image_frame, text="删除", command=lambda: self.delete_image(image_path, image_frame))
            delete_button.pack(side=tk.LEFT, padx=5)

        except Exception as e:
            print(f"Error displaying image {image_path}: {e}")

    def delete_image(self, image_path, image_frame):
        image_path = Path(image_path).resolve()
        if image_path in self.target_images_paths:
            self.target_images_paths.remove(str(image_path))
            os.remove(image_path)
            image_frame.destroy()
            print(f"Deleted image: {image_path}")
        else:
            print(f"Image not found or not in list: {image_path}")

    def click_target_in_screenshot_onshow(self, threshold):
        while not self.stop_event.is_set():
            if not self.target_images_paths:
                break

            if self.current_image_index >= len(self.target_images_paths):
                self.current_image_index = 0

            image_path = self.target_images_paths[self.current_image_index]
            screenshot, offset_left, offset_top = capture_screenshot()
            locations, w, h = find_image_in_screenshot(image_path, screenshot, threshold)

            if locations:
                for x, y in locations:
                    screen_x = x + offset_left + w // 2
                    screen_y = y + offset_top + h // 2
                    pyautogui.click(screen_x, screen_y)
                    print(f"点击位置 ({screen_x}, {screen_y})")
                    time.sleep(self.click_interval / 1000.0)
            else:
                print(f"未找到图像 {image_path}，等待下一次检查。")

            self.current_image_index += 1
        print("循环已停止。")

    def start_program(self):
        try:
            if not self.target_images_paths:
                raise ValueError("请上传目标图片！")

            timer_value = int(self.timer_entry.get().strip())
            click_interval_value = int(self.click_interval_entry.get().strip())

            if timer_value <= 0 or click_interval_value < 0:
                raise ValueError("倒计时时间必须是一个大于0的整数，点击间隔时间必须是一个非负整数！")

            self.running = True
            self.stop_event.clear()
            self.stop_timer_duration = timer_value
            self.click_interval = click_interval_value
            self.current_image_index = 0

            self.root.update_idletasks()
            self.root.state('iconic')

            stop_timer = threading.Timer(self.stop_timer_duration, self.stop_program)
            stop_timer.start()

            self.click_target_in_screenshot_onshow(0.8)

            stop_timer.cancel()
            self.running = False

        except ValueError as e:
            messagebox.showerror("错误", str(e))
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def start_program_thread(self):
        threading.Thread(target=self.start_program, daemon=True).start()

    def stop_program(self):
        if self.running:
            self.stop_event.set()
            print("Stopping the program.")
            messagebox.showinfo("停止", "程序已停止")
            self.root.deiconify()
            self.root.state('normal')
            self.running = False

    def hotkey_stop_program(self):
        if self.running:
            self.stop_program()

    def get_base_path(self):
        return sys._MEIPASS if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent.parent

def main():
    root = tk.Tk()
    app = ImageClickerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()