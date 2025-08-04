# 这是一个示例 Python 脚本。


# 按间距中的绿色按钮以运行脚本。
import sys

from PyQt5.QtWidgets import QApplication

from src.FrmMain import FrmMain

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("pySC2Translator")

    frm = FrmMain()
    frm.show()

    sys.exit(app.exec())

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
