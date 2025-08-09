# chess_assistant.py
import sys
import os
import time
import random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ChessEngineThread(QThread):
    analysis_updated = pyqtSignal(str, str, str, str, str)
    best_move = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
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
            book_moves = ["炮二平五", "马八进七", "车一进一", "兵七进一", "相三进五", 
                         "马二进三", "车九平八", "炮八平九", "士四进五", "炮五平六"]
            move = random.choice(book_moves)
            self.analysis_updated.emit(move, "+0.00", "0", "0", "0ms")
            self.best_move.emit(move)
            return
        
        # 模拟引擎思考过程
        start_time = time.time()
        depth = 0
        nodes = 0
        
        while self.running and depth <= self.max_depth:
            depth += 1
            if depth > 5:  # 深度5以上开始生成节点数
                nodes += random.randint(10000, 500000)
                
            # 模拟不同深度的评估变化
            eval_value = random.uniform(-3.0, 3.0)
            sign = "+" if eval_value >= 0 else "-"
            abs_eval = abs(eval_value)
            
            # 生成随机着法
            moves = ["炮二平五", "马八进七", "车一进一", "兵七进一", "相三进五", 
                    "马二进三", "车九平八", "炮八平九", "士四进五", "炮五平六"]
            move = random.choice(moves)
            
            # 计算思考时间
            elapsed = (time.time() - start_time) * 1000  # ms
            
            # 发送分析更新
            self.analysis_updated.emit(move, f"{sign}{abs_eval:.2f}", 
                                      str(depth), f"{nodes:,}", f"{elapsed:.0f}ms")
            
            # 检查是否超过思考时间
            if elapsed >= self.thinking_time:
                break
                
            # 模拟思考间隔
            self.msleep(300)
        
        # 发送最佳着法
        moves = ["炮二平五", "马八进七", "车一进一", "兵七进一", "相三进五"]
        self.best_move.emit(random.choice(moves))


class ChessAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("象棋连线大师 v1.0")
        self.setWindowIcon(QIcon(self.get_resource_path("chess_icon.png")))
        self.setGeometry(100, 100, 1100, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2D2D30;
            }
            QGroupBox {
                color: #F1F1F1;
                border: 1px solid #3F3F46;
                border-radius: 5px;
                margin-top: 16px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: transparent;
                color: #F1F1F1;
            }
            QLabel {
                color: #CCCCCC;
            }
            QPushButton {
                background-color: #3F3F46;
                color: #F1F1F1;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #505058;
            }
            QPushButton:pressed {
                background-color: #2A2A2E;
            }
            QPushButton:disabled {
                background-color: #2A2A2E;
                color: #888888;
            }
            QRadioButton {
                color: #CCCCCC;
            }
            QCheckBox {
                color: #CCCCCC;
            }
            QLineEdit {
                background-color: #252526;
                color: #F1F1F1;
                border: 1px solid #3F3F46;
                border-radius: 3px;
                padding: 5px;
            }
            QTextEdit {
                background-color: #252526;
                color: #CCCCCC;
                border: 1px solid #3F3F46;
                border-radius: 3px;
                font-family: Consolas, monospace;
                font-size: 12px;
            }
            QListWidget {
                background-color: #252526;
                color: #CCCCCC;
                border: 1px solid #3F3F46;
                border-radius: 3px;
            }
            QTabWidget::pane {
                border: 1px solid #3F3F46;
                background: #252526;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #2D2D30;
                color: #CCCCCC;
                padding: 8px 15px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid #3F3F46;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #252526;
                border-bottom-color: #252526;
            }
            QSpinBox, QComboBox {
                background-color: #252526;
                color: #F1F1F1;
                border: 1px solid #3F3F46;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        
        # 初始化布局
        self.init_ui()
        
        # 引擎线程
        self.engine_thread = ChessEngineThread()
        self.engine_thread.analysis_updated.connect(self.update_engine_info)
        self.engine_thread.best_move.connect(self.on_best_move)
        
        # 默认设置
        self.settings = {
            "engine_path": "",
            "opening_book": "",
            "hash_size": 512,
            "threads": 4,
            "search_time": 3000,
            "move_time": 5000,
            "ponder": True,
            "auto_restart": True,
            "book_enabled": True
        }
        
        # 启动状态
        self.connected = False
        
    def get_resource_path(self, filename):
        """获取资源文件的绝对路径"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, filename)
        
    def init_ui(self):
        # 创建主选项卡
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.setCentralWidget(self.tabs)
        
        # 主控制台
        self.tab_main = QWidget()
        self.tabs.addTab(self.tab_main, "主控制台")
        
        # 引擎设置
        self.tab_settings = QWidget()
        self.tabs.addTab(self.tab_settings, "引擎设置")
        
        # 开局库管理
        self.tab_openings = QWidget()
        self.tabs.addTab(self.tab_openings, "开局库管理")
        
        # 初始化各个选项卡
        self.init_main_tab()
        self.init_settings_tab()
        self.init_openings_tab()
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
    def init_main_tab(self):
        layout = QVBoxLayout(self.tab_main)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 上半部分：控制区
        control_layout = QHBoxLayout()
        
        # 平台选择
        platform_group = QGroupBox("游戏平台")
        platform_layout = QVBoxLayout()
        self.tt_radio = QRadioButton("天天象棋")
        self.jj_radio = QRadioButton("JJ象棋")
        self.tt_radio.setChecked(True)
        platform_layout.addWidget(self.tt_radio)
        platform_layout.addWidget(self.jj_radio)
        platform_group.setLayout(platform_layout)
        
        # 连接控制
        connect_group = QGroupBox("连接控制")
        connect_layout = QVBoxLayout()
        self.connect_btn = QPushButton("开始连接")
        self.connect_btn.setFixedHeight(40)
        self.connect_btn.setStyleSheet("font-weight: bold; background-color: #4CAF50;")
        self.disconnect_btn = QPushButton("断开连接")
        self.disconnect_btn.setFixedHeight(30)
        self.disconnect_btn.setEnabled(False)
        self.disconnect_btn.setStyleSheet("background-color: #F44336;")
        
        connect_layout.addWidget(self.connect_btn)
        connect_layout.addWidget(self.disconnect_btn)
        connect_group.setLayout(connect_layout)
        
        # 引擎控制
        engine_group = QGroupBox("引擎控制")
        engine_layout = QVBoxLayout()
        self.force_move_btn = QPushButton("强制出招")
        self.force_move_btn.setFixedHeight(30)
        self.stop_engine_btn = QPushButton("停止思考")
        self.stop_engine_btn.setFixedHeight(30)
        self.auto_restart_cb = QCheckBox("自动续盘")
        self.auto_restart_cb.setChecked(True)
        
        engine_layout.addWidget(self.force_move_btn)
        engine_layout.addWidget(self.stop_engine_btn)
        engine_layout.addWidget(self.auto_restart_cb)
        engine_group.setLayout(engine_layout)
        
        control_layout.addWidget(platform_group, 1)
        control_layout.addWidget(connect_group, 1)
        control_layout.addWidget(engine_group, 1)
        
        # 中间部分：棋盘和引擎信息
        middle_layout = QHBoxLayout()
        
        # 棋盘显示
        board_group = QGroupBox("棋盘状态")
        board_layout = QVBoxLayout()
        self.board_view = QLabel()
        self.board_view.setAlignment(Qt.AlignCenter)
        self.board_view.setFixedSize(400, 450)
        self.board_view.setPixmap(QPixmap(self.get_resource_path("chinese_chess_board.png")).scaled(400, 450, Qt.KeepAspectRatio))
        self.status_label = QLabel("未连接")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #FF9800;")
        
        board_layout.addWidget(self.board_view)
        board_layout.addWidget(self.status_label)
        board_group.setLayout(board_layout)
        
        # 引擎信息
        info_group = QGroupBox("引擎信息")
        info_layout = QGridLayout()
        info_layout.setColumnStretch(0, 1)
        info_layout.setColumnStretch(1, 2)
        
        info_layout.addWidget(QLabel("最佳着法:"), 0, 0)
        self.engine_move = QLabel("等待计算...")
        self.engine_move.setStyleSheet("color: #FFC107; font-weight: bold;")
        info_layout.addWidget(self.engine_move, 0, 1)
        
        info_layout.addWidget(QLabel("局面评估:"), 1, 0)
        self.engine_eval = QLabel("0.00")
        self.engine_eval.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(self.engine_eval, 1, 1)
        
        info_layout.addWidget(QLabel("搜索深度:"), 2, 0)
        self.engine_depth = QLabel("0")
        info_layout.addWidget(self.engine_depth, 2, 1)
        
        info_layout.addWidget(QLabel("搜索节点:"), 3, 0)
        self.engine_nodes = QLabel("0")
        info_layout.addWidget(self.engine_nodes, 3, 1)
        
        info_layout.addWidget(QLabel("思考时间:"), 4, 0)
        self.engine_time = QLabel("0ms")
        info_layout.addWidget(self.engine_time, 4, 1)
        
        # 引擎参数摘要
        param_label = QLabel("<b>当前引擎参数</b>")
        param_label.setStyleSheet("margin-top: 15px;")
        info_layout.addWidget(param_label, 5, 0, 1, 2)
        
        info_layout.addWidget(QLabel("哈希大小:"), 6, 0)
        self.param_hash = QLabel("512 MB")
        info_layout.addWidget(self.param_hash, 6, 1)
        
        info_layout.addWidget(QLabel("线程数:"), 7, 0)
        self.param_threads = QLabel("4")
        info_layout.addWidget(self.param_threads, 7, 1)
        
        info_layout.addWidget(QLabel("开局库:"), 8, 0)
        self.param_book = QLabel("已启用")
        info_layout.addWidget(self.param_book, 8, 1)
        
        info_layout.addWidget(QLabel("后台思考:"), 9, 0)
        self.param_ponder = QLabel("已启用")
        info_layout.addWidget(self.param_ponder, 9, 1)
        
        info_group.setLayout(info_layout)
        
        middle_layout.addWidget(board_group, 2)
        middle_layout.addWidget(info_group, 1)
        
        # 日志区域
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(150)
        clear_btn = QPushButton("清空日志")
        clear_btn.setFixedWidth(100)
        
        log_layout.addWidget(self.log_text)
        log_layout.addWidget(clear_btn, alignment=Qt.AlignRight)
        log_group.setLayout(log_layout)
        
        # 组合布局
        layout.addLayout(control_layout)
        layout.addLayout(middle_layout)
        layout.addWidget(log_group)
        
        # 连接信号
        self.connect_btn.clicked.connect(self.start_connection)
        self.disconnect_btn.clicked.connect(self.stop_connection)
        self.force_move_btn.clicked.connect(self.force_move)
        self.stop_engine_btn.clicked.connect(self.stop_engine)
        clear_btn.clicked.connect(self.clear_log)
        
    def init_settings_tab(self):
        layout = QVBoxLayout(self.tab_settings)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 引擎设置
        engine_group = QGroupBox("象棋引擎设置")
        engine_layout = QGridLayout()
        engine_layout.setColumnStretch(0, 1)
        engine_layout.setColumnStretch(1, 3)
        
        # 引擎路径
        engine_layout.addWidget(QLabel("引擎路径:"), 0, 0)
        self.engine_path = QLineEdit()
        browse_engine = QPushButton("浏览...")
        browse_engine.setFixedWidth(80)
        
        engine_path_layout = QHBoxLayout()
        engine_path_layout.addWidget(self.engine_path)
        engine_path_layout.addWidget(browse_engine)
        engine_layout.addLayout(engine_path_layout, 0, 1)
        
        # 开局库路径
        engine_layout.addWidget(QLabel("开局库路径:"), 1, 0)
        self.book_path = QLineEdit()
        browse_book = QPushButton("浏览...")
        browse_book.setFixedWidth(80)
        
        book_path_layout = QHBoxLayout()
        book_path_layout.addWidget(self.book_path)
        book_path_layout.addWidget(browse_book)
        engine_layout.addLayout(book_path_layout, 1, 1)
        
        engine_group.setLayout(engine_layout)
        
        # 引擎参数
        param_group = QGroupBox("引擎参数")
        param_layout = QGridLayout()
        param_layout.setColumnStretch(0, 1)
        param_layout.setColumnStretch(1, 1)
        
        # 哈希表大小
        param_layout.addWidget(QLabel("哈希表大小 (MB):"), 0, 0)
        self.hash_spin = QSpinBox()
        self.hash_spin.setRange(16, 2048)
        self.hash_spin.setValue(512)
        param_layout.addWidget(self.hash_spin, 0, 1)
        
        # 线程数
        param_layout.addWidget(QLabel("线程数:"), 1, 0)
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(1, 32)
        self.threads_spin.setValue(4)
        param_layout.addWidget(self.threads_spin, 1, 1)
        
        # 搜索时间
        param_layout.addWidget(QLabel("搜索时间 (ms):"), 2, 0)
        self.search_time = QSpinBox()
        self.search_time.setRange(100, 30000)
        self.search_time.setValue(3000)
        param_layout.addWidget(self.search_time, 2, 1)
        
        # 每步时间
        param_layout.addWidget(QLabel("每步时间 (ms):"), 3, 0)
        self.move_time = QSpinBox()
        self.move_time.setRange(1000, 60000)
        self.move_time.setValue(5000)
        param_layout.addWidget(self.move_time, 3, 1)
        
        # 开局库使用
        param_layout.addWidget(QLabel("开局库使用:"), 4, 0)
        self.book_cb = QCheckBox("启用开局库")
        self.book_cb.setChecked(True)
        param_layout.addWidget(self.book_cb, 4, 1)
        
        # 后台思考
        param_layout.addWidget(QLabel("后台思考:"), 5, 0)
        self.ponder_cb = QCheckBox("启用后台思考")
        self.ponder_cb.setChecked(True)
        param_layout.addWidget(self.ponder_cb, 5, 1)
        
        param_group.setLayout(param_layout)
        
        # 保存按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        save_btn = QPushButton("保存设置")
        save_btn.setFixedHeight(40)
        save_btn.setStyleSheet("background-color: #2196F3; font-weight: bold;")
        btn_layout.addWidget(save_btn)
        
        # 添加到主布局
        layout.addWidget(engine_group)
        layout.addWidget(param_group)
        layout.addLayout(btn_layout)
        
        # 连接信号
        browse_engine.clicked.connect(self.select_engine_file)
        browse_book.clicked.connect(self.select_book_file)
        save_btn.clicked.connect(self.save_settings)
    
    def init_openings_tab(self):
        layout = QVBoxLayout(self.tab_openings)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 开局库列表
        book_group = QGroupBox("开局库列表")
        book_layout = QVBoxLayout()
        
        self.book_list = QListWidget()
        self.book_list.addItems(["经典开局库", "竞技开局库", "残局库", "飞刀开局库"])
        self.book_list.setCurrentRow(0)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加开局库")
        remove_btn = QPushButton("移除开局库")
        update_btn = QPushButton("更新开局库")
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(update_btn)
        
        book_layout.addWidget(self.book_list)
        book_layout.addLayout(btn_layout)
        book_group.setLayout(book_layout)
        
        # 开局详情
        details_group = QGroupBox("开局详情：经典开局库")
        details_layout = QVBoxLayout()
        
        # 顶部信息
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel("开局数: 1,245"))
        info_layout.addWidget(QLabel("作者: 象棋大师"))
        info_layout.addWidget(QLabel("版本: 2024.1"))
        info_layout.addStretch()
        
        # 开局表格
        self.opening_table = QTableWidget(10, 4)
        self.opening_table.setHorizontalHeaderLabels(["序号", "着法", "使用次数", "胜率"])
        self.opening_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.opening_table.verticalHeader().setVisible(False)
        self.opening_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.opening_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # 填充示例数据
        opening_data = [
            (1, "炮二平五", 1245, "58.2%"),
            (2, "马八进七", 987, "54.7%"),
            (3, "车一进一", 845, "62.1%"),
            (4, "兵七进一", 763, "51.6%"),
            (5, "相三进五", 654, "56.8%"),
            (6, "马二进三", 589, "53.4%"),
            (7, "车九平八", 476, "59.7%"),
            (8, "炮八平九", 423, "49.3%"),
            (9, "士四进五", 387, "55.1%"),
            (10, "炮五平六", 321, "52.9%")
        ]
        
        for row, (num, move, count, win_rate) in enumerate(opening_data):
            self.opening_table.setItem(row, 0, QTableWidgetItem(str(num)))
            self.opening_table.setItem(row, 1, QTableWidgetItem(move))
            self.opening_table.setItem(row, 2, QTableWidgetItem(str(count)))
            self.opening_table.setItem(row, 3, QTableWidgetItem(win_rate))
        
        details_layout.addLayout(info_layout)
        details_layout.addWidget(self.opening_table)
        details_group.setLayout(details_layout)
        
        # 添加到主布局
        layout.addWidget(book_group, 1)
        layout.addWidget(details_group, 2)
        
        # 连接信号
        self.book_list.currentRowChanged.connect(self.update_opening_details)
        
    def select_engine_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "选择象棋引擎", "", "可执行文件 (*.exe)")
        if file:
            self.engine_path.setText(file)
            self.log(f"已选择引擎: {file}")
    
    def select_book_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "选择开局库", "", "开局库文件 (*.obk *.bin)")
        if file:
            self.book_path.setText(file)
            self.log(f"已选择开局库: {file}")
    
    def save_settings(self):
        self.settings = {
            "engine_path": self.engine_path.text(),
            "opening_book": self.book_path.text(),
            "hash_size": self.hash_spin.value(),
            "threads": self.threads_spin.value(),
            "search_time": self.search_time.value(),
            "move_time": self.move_time.value(),
            "ponder": self.ponder_cb.isChecked(),
            "book_enabled": self.book_cb.isChecked(),
            "auto_restart": True
        }
        
        # 更新参数显示
        self.param_hash.setText(f"{self.settings['hash_size']} MB")
        self.param_threads.setText(f"{self.settings['threads']}")
        self.param_book.setText("已启用" if self.settings['book_enabled'] else "已禁用")
        self.param_ponder.setText("已启用" if self.settings['ponder'] else "已禁用")
        
        self.log("引擎设置已保存")
        QMessageBox.information(self, "设置", "引擎参数已保存成功！")
    
    def start_connection(self):
        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(True)
        self.status_label.setText("连接中...")
        self.status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        self.log("开始连接游戏平台...")
        
        # 模拟连接过程
        QTimer.singleShot(2000, self.connection_success)
    
    def connection_success(self):
        platform = "天天象棋" if self.tt_radio.isChecked() else "JJ象棋"
        self.status_label.setText(f"已连接 - {platform}")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        self.log(f"{platform}连接成功")
        self.log("正在识别棋盘...")
        self.connected = True
        
        # 模拟加载棋盘
        QTimer.singleShot(1000, self.load_board)
        
    def load_board(self):
        self.board_view.setPixmap(QPixmap(self.get_resource_path("chinese_chess_board.png")).scaled(400, 450, Qt.KeepAspectRatio))
        self.log("棋盘识别成功")
        self.log("引擎开始思考...")
        
        # 启动引擎思考
        self.start_engine_analysis()
    
    def start_engine_analysis(self):
        # 设置引擎参数
        self.engine_thread.set_parameters(
            time=self.settings["search_time"],
            depth=25,
            hash_size=self.settings["hash_size"],
            threads=self.settings["threads"],
            book=self.settings["book_enabled"],
            ponder=self.settings["ponder"]
        )
        
        # 设置棋盘位置（这里用一个随机FEN位置）
        fen_position = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR"
        self.engine_thread.set_position(fen_position)
        
        # 启动引擎线程
        if not self.engine_thread.isRunning():
            self.engine_thread.start()
    
    def update_engine_info(self, move, eval_value, depth, nodes, time_spent):
        self.engine_move.setText(move)
        self.engine_eval.setText(eval_value)
        self.engine_depth.setText(depth)
        self.engine_nodes.setText(nodes)
        self.engine_time.setText(time_spent)
        
        # 根据评估值改变颜色
        try:
            eval_float = float(eval_value)
            if eval_float > 0:
                self.engine_eval.setStyleSheet("color: #4CAF50; font-weight: bold;")
            elif eval_float < 0:
                self.engine_eval.setStyleSheet("color: #F44336; font-weight: bold;")
            else:
                self.engine_eval.setStyleSheet("color: #FFC107; font-weight: bold;")
        except:
            self.engine_eval.setStyleSheet("color: #FFC107; font-weight: bold;")
    
    def on_best_move(self, move):
        self.log(f"引擎走棋: {move}")
        self.log("等待对手走棋...")
        
        # 模拟对手走棋
        QTimer.singleShot(4000, self.opponent_move)
    
    def opponent_move(self):
        moves = ["马8进7", "炮2平5", "卒3进1", "车9平8", "相7进5"]
        move = random.choice(moves)
        self.log(f"对手走棋: {move}")
        
        if self.connected:
            self.log("引擎开始思考...")
            self.start_engine_analysis()
    
    def stop_connection(self):
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.status_label.setText("未连接")
        self.status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        self.log("已断开游戏连接")
        self.connected = False
        self.stop_engine()
    
    def force_move(self):
        if self.connected:
            self.log("强制出招: " + self.engine_move.text())
            self.log("等待对手走棋...")
            self.stop_engine()
            QTimer.singleShot(3000, self.opponent_move)
    
    def stop_engine(self):
        if self.engine_thread.isRunning():
            self.engine_thread.stop()
            self.engine_thread.wait()
            self.log("引擎思考已停止")
    
    def update_opening_details(self, index):
        books = ["经典开局库", "竞技开局库", "残局库", "飞刀开局库"]
        if 0 <= index < len(books):
            group_box = self.tab_openings.findChild(QGroupBox, "开局详情")
            if group_box:
                group_box.setTitle(f"开局详情：{books[index]}")
    
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
        
        # 更新状态栏
        self.status_bar.showMessage(f"信息: {message}", 3000)
    
    def clear_log(self):
        self.log_text.clear()
        self.log("日志已清空")
    
    def closeEvent(self, event):
        # 停止引擎线程
        if self.engine_thread.isRunning():
            self.engine_thread.stop()
            self.engine_thread.wait(1000)
        
        # 确认退出
        reply = QMessageBox.question(self, '退出确认', 
                                    "确定要退出象棋连线大师吗？", 
                                    QMessageBox.Yes | QMessageBox.No, 
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    # 创建并显示主窗口
    window = ChessAssistant()
    window.show()
    
    # 记录启动日志
    window.log("象棋连线大师已启动")
    window.log("请选择游戏平台并点击'开始连接'")
    
    sys.exit(app.exec_())
