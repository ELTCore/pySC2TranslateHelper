import os
import sys
from typing import List
from pathvalidate import sanitize_filename

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QFileDialog

from ui.FrmMain import Ui_FrmMain


class FrmMain(QWidget, Ui_FrmMain):

    def __init__(self, *args, **kwargs):
        super(FrmMain, self).__init__()
        self.setupUi(self)

        self.dict_old_origin = {}
        self.dict_old_trans = {}
        self.dict_new_origin = {}

    def init(self):
        self.dict_old_origin = {}
        self.dict_old_trans = {}
        self.dict_new_origin = {}
        pass

    def fill_entry_dict(self, entry: dict, file_path):
        with open(file_path, "r", encoding='utf-8') as fileHandler:
            line = fileHandler.readline()
            while line:
                str_list: List[str] = line.strip().split("=", 1)
                length = len(str_list)
                if length == 1:
                    entry[str_list[0]] = ''
                elif length == 2:
                    entry[str_list[0]] = str_list[1]
                else:
                    print(f"unexpected entry:{line}")
                line = fileHandler.readline()

    @QtCore.pyqtSlot()
    def on_btnGenerate_clicked(self):
        print("Start Generate")
        filename = self.lEditOutputFileName.text()
        filename = sanitize_filename(filename, "_")

        if os.path.exists(f'./{filename}'):
            reply = QMessageBox.warning(self, '提示', f'{filename}已存在于文件目录下，是否覆盖？', QMessageBox.Yes | QMessageBox.Cancel)
            if reply != QMessageBox.Yes:
                return
            try:
                os.remove(f'./{filename}')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'覆盖文件出错:{e}')
                return

        self.init()
        try:
            self.fill_entry_dict(self.dict_old_origin, self.lEditOldOriginFilePath.text())
        except Exception as e:
            self.dict_old_origin = {}
        try:
            self.fill_entry_dict(self.dict_old_trans, self.lEditOldTransFilePath.text())
            self.fill_entry_dict(self.dict_new_origin, self.lEditNewOriginFilePath.text())
        except Exception as e:
            QMessageBox.warning(self, '错误', f'读取文件失败:{e}')
            return

        if len(self.dict_old_origin):
            self.check_entry_with_old_origin()
        else:
            self.check_entry_without_old_origin()

        self.output_entry_dict(self.dict_new_origin, f'./{filename}')
        QMessageBox.information(self, '搞定', '完事儿了')

    def output_entry_dict(self, entry: dict, file_path: str):
        try:
            with open(file_path, encoding="utf-8", mode="a") as f:
                for key, value in entry.items():
                    f.write(f'{key}={value}\n')
        except Exception as e:
            QMessageBox.warning(self, '出错', f'文件写入出错:{e}')

    def check_entry_without_old_origin(self):
        for key, value in self.dict_new_origin.items():
            try:
                trans = self.dict_old_trans[key]
            except KeyError:
                trans = f'{value} //newEntry:{key}'
            finally:
                self.dict_new_origin[key] = trans

    def check_entry_with_old_origin(self):
        for key, value in self.dict_new_origin.items():
            try:
                origin_value = self.dict_old_origin[key]
                if origin_value == value:
                    trans = self.dict_old_trans[key]
                else:
                    trans = f'{self.dict_old_trans[key]} // originEntryHasBeenModified:{key}'
            except KeyError:
                trans = f'{value} // newEntry:{key}'
            finally:
                self.dict_new_origin[key] = trans

    @QtCore.pyqtSlot()
    def on_btnFileExplorerOldOrigin_clicked(self):
        file_dialog = QFileDialog()
        # file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        if file_dialog.exec_() == QFileDialog.Accepted:
            selected_folder = file_dialog.selectedFiles()[0]
            self.lEditOldOriginFilePath.setText(selected_folder)

    @QtCore.pyqtSlot()
    def on_btnFileExplorerOldTrans_clicked(self):
        file_dialog = QFileDialog()
        # file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        if file_dialog.exec_() == QFileDialog.Accepted:
            selected_folder = file_dialog.selectedFiles()[0]
            self.lEditOldTransFilePath.setText(selected_folder)

    @QtCore.pyqtSlot()
    def on_btnFileExplorerNewOrigin_clicked(self):
        file_dialog = QFileDialog()
        # file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        if file_dialog.exec_() == QFileDialog.Accepted:
            selected_folder = file_dialog.selectedFiles()[0]
            self.lEditNewOriginFilePath.setText(selected_folder)

    @QtCore.pyqtSlot()
    def on_btnExit_clicked(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("pySC2Translator")

    frm = FrmMain()
    frm.show()

    sys.exit(app.exec())
