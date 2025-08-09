import sys
import os
import time
import random
import subprocess
import cv2
import numpy as np
from abc import ABC, abstractmethod
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import win32gui
import win32ui
import win32con
import win32api


# ------------------------------
# 新增：资源路径处理函数（支持PyInstaller打包）
# ------------------------------
def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径（兼容开发环境与PyInstaller打包后的环境）
    - 开发环境：使用当前工作目录
    - 打包环境：使用PyInstaller的`sys._MEIPASS`目录（资源文件会被自动复制到此处）
    """
    try:
        # PyInstaller打包后，资源文件位于`sys._MEIPASS`目录
        base_path = sys._MEIPASS
    except AttributeError:
        # 未打包时，使用当前工作目录
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ------------------------------
# 1. 规则抽象与实现（核心逻辑）
# ------------------------------
class ChessRule(ABC):
    """象棋规则抽象基类（定义接口）"""
    @abstractmethod
    def is_legal_move(self, move: str, fen: str) -> bool:
        """判断走法是否合法（move: 中文走法，如"炮二平五"；fen: 当前局面）"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """返回规则名称（用于界面显示）"""
        pass


class ChineseRule(ChessRule):
    """中国象棋规则（示例：兵卒只能向前，过河后可左右）"""
    def is_legal_move(self, move: str, fen: str) -> bool:
        # 解析走法（如"炮二平五"→类型：炮，起点：二列，终点：五列）
        # 实际需完善坐标转换和规则判断（此处用占位符表示合法）
        return True  # 假设该走法符合中国规则

    def get_name(self) -> str:
        return "中国规则"


class AsianRule(ChessRule):
    """亚洲象棋规则（示例：允许兵卒过河后横向走，长将允许）"""
    def is_legal_move(self, move: str, fen: str) -> bool:
        # 亚洲规则更宽松（此处用占位符表示合法）
        return True

    def get_name(self) -> str:
        return "亚洲规则"


class TianTianRule(ChessRule):
    """天天象棋规则（示例：允许长将，兵卒可后退）"""
    def is_legal_move(self, move: str, fen: str) -> bool:
        # 天天象棋规则（此处用占位符表示合法）
        return True

    def get_name(self) -> str:
        return "天天规则"


# ------------------------------
# 2. 引擎线程（处理规则验证与思考）
# ------------------------------
class ChessEngineThread(QThread):
    analysis_updated = pyqtSignal(str, str, str, str, str)
    best_move = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  # 指向ChessAssistant主窗口
        self.running = False
        self.position = ""
        self.thinking_time = 3000  # ms
        self.max_depth = 18
        self.hash_size = 512
        self.threads = 4
        self.book_enabled = True
        self.ponder_enabled = True

    def set_position(self, fen):
        self.position = fen

    def set_parameters(self, time, depth, hash_size, threads, book, ponder):
        self.thinking_time = time
        self.max_depth = depth
        self.hash_size = hash_size
        self.threads = threads
        self.book_enabled = book
        self.ponder_enabled = ponder

    def stop(self):
        self.running = False

    def run(self):
        self.running = True

        # 模拟开局库使用
        if self.book_enabled and random.random() > 0.5:
            book_moves = ["炮二平五", "马八进七", "车一进一", "兵七进一", "相三进五"]
            move = random.choice(book_moves)
            self.analysis_updated.emit(move, "+0.00", "0", "0", "0ms")
            self._validate_move(move)  # 验证走法合法性
            return

        # 模拟引擎思考过程
        start_time = time.time()
        depth = 0
        nodes = 0

        # （此处原代码未完成，需根据实际逻辑补全，不影响打包）


# ------------------------------
# 3. 主窗口类（整合所有功能）
# ------------------------------
class ChessAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("象棋连线大师 v1.0")
        
        # 修改：使用`get_resource_path`加载图标（支持打包后环境）
        self.setWindowIcon(QIcon(get_resource_path("chess_icon.ico")))
        
        self.setGeometry(100, 100, 1100, 700)
        self.setStyleSheet("""
            QMainWindow { background-color: #2D2D30; }
            QGroupBox { color: #F1F1F1; border: 1px solid #3F3F46; border-radius: 5px; margin-top: 16px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 5px; background-color: transparent; color: #F1F1F1; }
            QComboBox { background-color: #3F3F46; color: #F1F1F1; border: 1px solid #5F5F66; border-radius: 3px; padding: 5px; }
            QComboBox::drop-down { border-left: 1px solid #5F5F66; background-color: #3F3F46; }
            QPushButton { background-color: #0078D7; color: white; border: none; border-radius: 3px; padding: 8px 16px; margin: 5px; }
            QPushButton:hover { background-color: #005A9E; }
            QTextEdit { background-color: #1E1E1E; color: #F1F1F1; border: none; padding: 10px; }
        """)

        # ------------------------------
        # 核心状态变量
        # ------------------------------
        self.current_fen = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"  # 初始局面
        self.current_rule = ChineseRule()  # 默认中国规则
        self.emulator_connected = False  # 模拟器连接状态
        self.tian
