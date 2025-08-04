import os
import sys
import re
from typing import List
from pathvalidate import sanitize_filename

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QFileDialog
from datetime import datetime

from ui.FrmMain import Ui_FrmMain


kStrNewEntry: str = "newEntry"
kStrModified: str = "originEntryHasBeenModified"

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
            try:  # 在oldOrigin中查找词条
                trans = self.dict_old_trans[key]
            except KeyError:  # 在oldOrigin中找不到, 标记为新词条
                trans = self.ignore_old_jobs(key, value, kStrNewEntry)
            finally:
                self.dict_new_origin[key] = trans

    def check_entry_with_old_origin(self):
        for key, value in self.dict_new_origin.items():
            try:
                origin_value = self.dict_old_origin[key]  # 在oldOrigin中查找词条
                if origin_value == value:
                    trans = self.dict_old_trans[key]
                else:  # oldOrigin和newOrigin词条中的内容不一致, 标记为原文已修改
                    trans = self.ignore_old_jobs(key, self.dict_old_trans[key], kStrModified)
            except KeyError:  # 在oldOrigin中找不到, 标记为新词条
                trans = self.ignore_old_jobs(key, value, kStrNewEntry)
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

    def ignore_old_jobs(self, key_text: str, trans_text: str, symbol_text: str):
        if key_text == 'Abil/Name/MorphZerglingToSwarmling222324':
            Test: int = 0

        try:
            trans = self.dict_old_trans[key_text]
            if self.check_symbol_and_datatime(trans, symbol_text):
                pass
            else:
                current_datetime = datetime.now()
                str_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                trans = f'{trans_text} // {symbol_text}_{str_datetime} :{key_text}'
        except KeyError:  # 在 oldTrans中找不到, 标记为新词条
            current_datetime = datetime.now()
            str_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            trans = f'{trans_text} // {kStrNewEntry}_{str_datetime} :{key_text}'
        finally:
            return trans

    def check_symbol_and_datatime(self, trans_text: str, symbol_text:str):
        # pattern = f"// {symbol_text}_" + r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
        patternNewEntry = r"// newEntry_(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})" #Todo 修改为配置上文项目
        matchNewEntry = re.search(patternNewEntry, trans_text)

        patternModified = r"// originEntryHasBeenModified_(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
        matchModified = re.search(patternModified, trans_text);

        if  matchNewEntry or matchModified:
            return True
        else:
            return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("pySC2Translator")

    frm = FrmMain()
    frm.show()

    sys.exit(app.exec())
