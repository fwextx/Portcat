from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel,
                             QPushButton, QHBoxLayout, QScrollArea, QFrame, QSizePolicy,
                             QMessageBox)
from PyQt5.QtCore import Qt, QPoint
from capture import ConnectionMonitor
from firewall import block_ip, unblock_ip

def styled_messagebox(title, text, icon=QMessageBox.Warning):
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setIcon(icon)
    msg.setStyleSheet("""
        QMessageBox {
            background-color: #2a2a3f;
            color: white;
            font-size: 13px;
        }
        QPushButton {
            background-color: #3a3a4f;
            color: white;
            border-radius: 8px;
            padding: 6px 14px;
        }
        QPushButton:hover {
            background-color: #555577;
        }
    """)
    return msg

class BubbleWidget(QFrame):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.is_blocked = False

        self.setStyleSheet("""
            background-color: #2a2a3f;
            border-radius: 10px;
            padding: 8px;
        """)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.status_label = QLabel("[UNBLOCKED]")
        self.status_label.setStyleSheet("color: #ffcc00; font-weight: bold;")
        layout.addWidget(self.status_label)

        info = f"PID: {connection['pid']} | {connection['proc']}\n{connection['laddr']} -> {connection['raddr']} | {connection['status']}"
        self.label = QLabel(info)
        self.label.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(self.label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.block_btn = QPushButton("Block")
        self.unblock_btn = QPushButton("Unblock")
        btn_layout.addWidget(self.block_btn)
        btn_layout.addWidget(self.unblock_btn)
        layout.addLayout(btn_layout)

        for btn in [self.block_btn, self.unblock_btn]:
            btn.setStyleSheet("""
                background-color: #3a3a4f;
                color: #e0e0e0;
                border: none;
                padding: 4px 8px;
                border-radius: 5px;
            """)
            btn.setCursor(Qt.PointingHandCursor)

        self.block_btn.clicked.connect(self.block)
        self.unblock_btn.clicked.connect(self.unblock)

    def block(self):
        raddr = self.connection['raddr'].split(":")[0]
        if raddr == "N/A":
            msg = styled_messagebox("Cannot Block", f"You cannot block {self.connection['proc']} because it has no remote IP.")
            msg.exec_()
            return

        reply = styled_messagebox("Confirm Block", f"Are you sure you want to block {self.connection['proc']} ({raddr})?", QMessageBox.Question)
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        ret = reply.exec_()
        if ret == QMessageBox.Yes:
            block_ip(raddr)
            self.is_blocked = True
            self.update_status_label()

    def unblock(self):
        raddr = self.connection['raddr'].split(":")[0]
        if raddr == "N/A":
            msg = styled_messagebox("Cannot Unblock", f"You cannot unblock {self.connection['proc']} because it has no remote IP.")
            msg.exec_()
            return

        reply = styled_messagebox("Confirm Unblock", f"Are you sure you want to unblock {self.connection['proc']} ({raddr})?", QMessageBox.Question)
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        ret = reply.exec_()
        if ret == QMessageBox.Yes:
            unblock_ip(raddr)
            self.is_blocked = False
            self.update_status_label()

    def update_status_label(self):
        if self.is_blocked:
            self.status_label.setText("[BLOCKED] " + self.connection['proc'])
        else:
            self.status_label.setText("[UNBLOCKED] " + self.connection['proc'])

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #1c1c2e; color: #e0e0e0;")
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10,0,10,0)
        self.setLayout(self.layout)

        self.title = QLabel("Portcat")
        self.layout.addWidget(self.title)
        self.layout.addStretch()

        self.min_btn = QPushButton("-")
        self.min_btn.clicked.connect(self.minimize)
        self.layout.addWidget(self.min_btn)

        self.close_btn = QPushButton("×")
        self.close_btn.clicked.connect(self.close)
        self.layout.addWidget(self.close_btn)

        for btn in [self.min_btn, self.close_btn]:
            btn.setStyleSheet("""
                background-color: #3a3a4f;
                color: #e0e0e0;
                border: none;
                padding: 5px 10px;
            """)
            btn.setCursor(Qt.PointingHandCursor)

        self.oldPos = None

    def minimize(self):
        self.parent.showMinimized()

    def close(self):
        self.parent.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.parent.move(self.parent.x() + delta.x(), self.parent.y() + delta.y())
            self.oldPos = event.globalPos()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #1e1e2f;")
        self.setFixedSize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        self.sort_layout = QHBoxLayout()
        self.sort_layout.addStretch()

        self.btn_time_sort = QPushButton("Newest → Oldest")
        self.btn_az_sort = QPushButton("A → Z")
        self.btn_status_sort = QPushButton("Status: Established First")
        self.btn_blocked_filter = QPushButton("Show Blocked Only")

        for btn in [self.btn_time_sort, self.btn_az_sort, self.btn_status_sort, self.btn_blocked_filter]:
            btn.setStyleSheet("""
                background-color: #3a3a4f;
                color: #e0e0e0;
                border: none;
                padding: 4px 10px;
                border-radius: 5px;
            """)
            btn.setCursor(Qt.PointingHandCursor)
            self.sort_layout.addWidget(btn)
        layout.addLayout(self.sort_layout)

        self.newest_first = True
        self.az_asc = True
        self.status_est_first = True
        self.last_sort_method = "time"
        self.blocked_filter_mode = "all"

        self.btn_time_sort.clicked.connect(self.toggle_time_sort)
        self.btn_az_sort.clicked.connect(self.toggle_az_sort)
        self.btn_status_sort.clicked.connect(self.toggle_status_sort)
        self.btn_blocked_filter.clicked.connect(self.toggle_blocked_filter)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background-color: #1e1e2f; border: none;")
        layout.addWidget(self.scroll)

        self.container = QWidget()
        self.scroll.setWidget(self.container)
        self.container_layout = QVBoxLayout()
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setSpacing(10)
        self.container_layout.setContentsMargins(10,10,10,10)
        self.container.setLayout(self.container_layout)

        scrollbar = self.scroll.verticalScrollBar()
        scrollbar.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: #1e1e2f;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #888888;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #555555;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        self.bubble_map = {}

        self.monitor = ConnectionMonitor()
        self.monitor.update_signal.connect(self.update_connections)
        self.monitor.start()

    def toggle_time_sort(self):
        self.newest_first = not self.newest_first
        self.btn_time_sort.setText("Newest → Oldest" if self.newest_first else "Oldest → Newest")
        self.last_sort_method = "time"
        self.sort_bubbles("time")

    def toggle_az_sort(self):
        self.az_asc = not self.az_asc
        self.btn_az_sort.setText("A → Z" if self.az_asc else "Z → A")
        self.last_sort_method = "az"
        self.sort_bubbles("az")

    def toggle_status_sort(self):
        self.status_est_first = not self.status_est_first
        self.btn_status_sort.setText("Status: Established First" if self.status_est_first else "Status: Established Last")
        self.last_sort_method = "status"
        self.sort_bubbles("status")

    def toggle_blocked_filter(self):
        if self.blocked_filter_mode == "all":
            self.blocked_filter_mode = "blocked"
            self.btn_blocked_filter.setText("Showing Blocked")
        elif self.blocked_filter_mode == "blocked":
            self.blocked_filter_mode = "unblocked"
            self.btn_blocked_filter.setText("Showing Unblocked")
        else:
            self.blocked_filter_mode = "all"
            self.btn_blocked_filter.setText("Showing All")

        self.apply_blocked_filter()

    def apply_blocked_filter(self):
        for bubble in self.bubble_map.values():
            if self.blocked_filter_mode == "all":
                bubble.show()
            elif self.blocked_filter_mode == "blocked":
                bubble.setVisible(bubble.is_blocked)
            elif self.blocked_filter_mode == "unblocked":
                bubble.setVisible(not bubble.is_blocked)

    def update_connections(self, connections):
        current_keys = set((c['pid'], c['laddr'], c['raddr']) for c in connections)
        existing_keys = set(self.bubble_map.keys())

        for key in existing_keys - current_keys:
            bubble = self.bubble_map[key]
            self.container_layout.removeWidget(bubble)
            bubble.setParent(None)
            del self.bubble_map[key]

        for conn in connections:
            key = (conn['pid'], conn['laddr'], conn['raddr'])
            if key not in self.bubble_map:
                bubble = BubbleWidget(conn)
                self.container_layout.addWidget(bubble)
                self.bubble_map[key] = bubble
            else:
                bubble = self.bubble_map[key]
                info = f"PID: {conn['pid']} | {conn['proc']}\n{conn['laddr']} -> {conn['raddr']} | {conn['status']}"
                bubble.label.setText(info)

        self.sort_bubbles(self.last_sort_method)
        self.apply_blocked_filter()

    def sort_bubbles(self, method):
        bubbles = list(self.bubble_map.items())
        if method == "time":
            bubbles.sort(key=lambda x: x[0][0], reverse=self.newest_first)
        elif method == "az":
            bubbles.sort(key=lambda x: x[1].connection['proc'].lower(), reverse=not self.az_asc)
        elif method == "status":
            bubbles.sort(key=lambda x: 0 if x[1].connection['status'] == "ESTABLISHED" else 1, reverse=not self.status_est_first)

        for i in reversed(range(self.container_layout.count())):
            self.container_layout.itemAt(i).widget().setParent(None)

        for key, bubble in bubbles:
            self.container_layout.addWidget(bubble)
