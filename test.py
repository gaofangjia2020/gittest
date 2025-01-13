import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import qrcode
from PIL import Image, ImageTk, ImageGrab
import pyperclip
import cv2
import numpy as np
from io import BytesIO

class QRCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("二维码生成器 & 识别器 v0.2.1 作者：高芳嘉 2025-01-13")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        self.root.resizable(False, False)

        # 默认值
        self.data = ""
        self.size = 10
        self.qr_image = None
        self.foreground_color = "#000000"
        self.background_color = "#FFFFFF"

        self.create_widgets()

    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # 生成器选项卡
        generator_frame = ttk.Frame(notebook, padding="10")
        notebook.add(generator_frame, text="二维码生成")

        # 识别器选项卡
        scanner_frame = ttk.Frame(notebook, padding="10")
        notebook.add(scanner_frame, text="二维码识别")

        # === 生成器部分 ===
        # 输入框架
        input_frame = ttk.LabelFrame(generator_frame, text="输入数据", padding="10")
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.entry_data = ttk.Entry(input_frame, width=50)
        self.entry_data.pack(fill=tk.X, padx=5, pady=5)

        # 设置框架
        settings_frame = ttk.LabelFrame(generator_frame, text="生成设置", padding="10")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)

        # 大小设置
        size_frame = ttk.Frame(settings_frame)
        size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(size_frame, text="二维码大小:").pack(side=tk.LEFT)
        self.size_scale = ttk.Scale(size_frame, from_=5, to=20, orient="horizontal")
        self.size_scale.set(self.size)
        self.size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 颜色选择框架
        colors_frame = ttk.Frame(settings_frame)
        colors_frame.pack(fill=tk.X, pady=5)

        # 前景色
        fg_frame = ttk.Frame(colors_frame)
        fg_frame.pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Label(fg_frame, text="前景色:").pack(side=tk.LEFT)
        self.fg_button = tk.Button(
            fg_frame, 
            text="选择颜色", 
            command=self.choose_foreground_color,
            bg=self.foreground_color,
            fg='white' if self.foreground_color == "#000000" else 'black',
            width=10
        )
        self.fg_button.pack(side=tk.LEFT, padx=5)

        # 背景色
        bg_frame = ttk.Frame(colors_frame)
        bg_frame.pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Label(bg_frame, text="背景色:").pack(side=tk.LEFT)
        self.bg_button = tk.Button(
            bg_frame, 
            text="选择颜色", 
            command=self.choose_background_color,
            bg=self.background_color,
            fg='black',
            width=10
        )
        self.bg_button.pack(side=tk.LEFT, padx=5)

        # 按钮框架
        button_frame = ttk.Frame(generator_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="生成二维码", command=self.generate_qrcode).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存二维码", command=self.save_qrcode).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="复制数据", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)

        # 预览框架
        preview_frame = ttk.LabelFrame(generator_frame, text="二维码预览", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.qr_preview_label = ttk.Label(preview_frame)
        self.qr_preview_label.pack(expand=True)

        # === 识别器部分 ===
        # 识别按钮框架
        scan_buttons_frame = ttk.Frame(scanner_frame)
        scan_buttons_frame.pack(fill=tk.X, pady=10)

        ttk.Button(scan_buttons_frame, text="从图片文件识别", 
                  command=self.scan_from_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(scan_buttons_frame, text="从屏幕截图识别", 
                  command=self.scan_from_screen).pack(side=tk.LEFT, padx=5)

        # 识别结果框架
        result_frame = ttk.LabelFrame(scanner_frame, text="识别结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.result_text = tk.Text(result_frame, height=10, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 复制结果按钮
        ttk.Button(scanner_frame, text="复制识别结果", 
                  command=self.copy_scan_result).pack(pady=5)

    def choose_foreground_color(self):
        color = colorchooser.askcolor(
            title="选择前景色",
            color=self.foreground_color
        )
        if color[1]:
            self.foreground_color = color[1]
            self.fg_button.configure(
                bg=self.foreground_color,
                fg='white' if self.foreground_color == "#000000" else 'black'
            )

    def choose_background_color(self):
        color = colorchooser.askcolor(
            title="选择背景色",
            color=self.background_color
        )
        if color[1]:
            self.background_color = color[1]
            self.bg_button.configure(
                bg=self.background_color,
                fg='black'
            )

    def generate_qrcode(self):
        self.data = self.entry_data.get()
        if not self.data:
            messagebox.showerror("错误", "请输入要生成的二维码数据！")
            return

        self.size = self.size_scale.get()

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=self.size,
            border=4,
        )
        qr.add_data(self.data)
        qr.make(fit=True)

        # 创建 QRCode 图像，确保使用正确的颜色格式
        self.qr_image = qr.make_image(
            fill_color=self.foreground_color,  # 使用 fill_color 而不是 fill
            back_color=self.background_color
        )
        
        # 调整图像大小以适应显示区域
        display_size = (300, 300)
        self.qr_image.thumbnail(display_size, Image.Resampling.LANCZOS)
        
        # 显示图像
        img_tk = ImageTk.PhotoImage(self.qr_image)
        self.qr_preview_label.config(image=img_tk)
        self.qr_preview_label.image = img_tk

    def save_qrcode(self):
        if not hasattr(self, 'qr_image') or not self.qr_image:
            messagebox.showerror("错误", "请先生成二维码！")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            self.qr_image.save(file_path)
            messagebox.showinfo("成功", "二维码已保存！")

    def copy_to_clipboard(self):
        if not self.data:
            messagebox.showerror("错误", "没有数据可复制！")
            return
        pyperclip.copy(self.data)
        messagebox.showinfo("成功", "数据已复制到剪贴板！")

    def scan_from_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            try:
                image = cv2.imread(file_path)
                self.decode_and_display(image)
            except Exception as e:
                messagebox.showerror("错误", f"无法读取图片: {str(e)}")

    def scan_from_screen(self):
        self.root.iconify()  # 最小化窗口
        self.root.after(1000, self.capture_screen)  # 等待1秒后截图

    def capture_screen(self):
        try:
            screenshot = ImageGrab.grab()
            # 将PIL图像转换为OpenCV格式
            opencv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            self.decode_and_display(opencv_image)
        finally:
            self.root.deiconify()  # 恢复窗口

    def decode_and_display(self, image):
        try:
            # 创建QR码检测器
            qr_detector = cv2.QRCodeDetector()
            
            # 检测和解码QR码
            retval, decoded_info, points, _ = qr_detector.detectAndDecodeMulti(image)
            
            # 清空文本框
            self.result_text.delete(1.0, tk.END)
            
            if retval:
                # 显示所有检测到的QR码信息
                for info in decoded_info:
                    if info:  # 确保信息不为空
                        self.result_text.insert(tk.END, f"识别结果: {info}\n")
                        self.result_text.insert(tk.END, "-" * 50 + "\n")
            else:
                messagebox.showinfo("提示", "未检测到二维码")

        except Exception as e:
            messagebox.showerror("错误", f"识别过程出错: {str(e)}")

    def copy_scan_result(self):
        result = self.result_text.get(1.0, tk.END).strip()
        if result:
            pyperclip.copy(result)
            messagebox.showinfo("成功", "识别结果已复制到剪贴板！")
        else:
            messagebox.showwarning("警告", "没有可复制的识别结果！")

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeApp(root)
    root.mainloop()
