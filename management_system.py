from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import database_functions as dbf
from telegram_bot import channel_create_lot, delete_lot
import shutil



class Ui_AdministratorMainWindow(object):
    def setupUi(self, AdministratorMainWindow, role=None, id=None):
        user_role = role, id
        admin_info = get_admin_info(user_role)

        AdministratorMainWindow.setObjectName("AdministratorMainWindow")
        AdministratorMainWindow.resize(800, 600)

        self.centralwidget = QtWidgets.QWidget(AdministratorMainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label_personal_info = QtWidgets.QLabel(self.centralwidget)
        self.label_personal_info.setGeometry(QtCore.QRect(20, 20, 311, 31))

        font = QtGui.QFont()
        font.setPointSize(12)

        self.label_personal_info.setFont(font)
        self.label_personal_info.setObjectName("label_personal_info")

        self.label_name = QtWidgets.QLabel(self.centralwidget)
        self.label_name.setGeometry(QtCore.QRect(30, 70, 71, 21))
        self.label_name.setObjectName("label_name")

        self.label_surname = QtWidgets.QLabel(self.centralwidget)
        self.label_surname.setGeometry(QtCore.QRect(30, 110, 71, 21))
        self.label_surname.setObjectName("label_surname")

        self.label_contact = QtWidgets.QLabel(self.centralwidget)
        self.label_contact.setGeometry(QtCore.QRect(30, 150, 131, 21))
        self.label_contact.setObjectName("label_contact")

        self.lineEdit_name = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_name.setGeometry(QtCore.QRect(160, 70, 181, 21))
        self.lineEdit_name.setObjectName("lineEdit_name")

        self.lineEdit_surname = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_surname.setGeometry(QtCore.QRect(160, 110, 181, 21))
        self.lineEdit_surname.setObjectName("lineEdit_surname")

        self.lineEdit_contact = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_contact.setGeometry(QtCore.QRect(160, 150, 181, 21))
        self.lineEdit_contact.setObjectName("lineEdit_contact")

        self.label_balance = QtWidgets.QLabel(self.centralwidget)
        self.label_balance.setGeometry(QtCore.QRect(400, 70, 71, 21))
        self.label_balance.setObjectName("label_balance")

        self.lineEdit_balance = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_balance.setGeometry(QtCore.QRect(530, 70, 181, 21))
        self.lineEdit_balance.setObjectName("lineEdit_balance")

        self.label_role = QtWidgets.QLabel(self.centralwidget)
        self.label_role.setGeometry(QtCore.QRect(400, 110, 71, 21))
        self.label_role.setObjectName("label_role")

        self.lineEdit_role = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_role.setGeometry(QtCore.QRect(530, 110, 181, 21))
        self.lineEdit_role.setObjectName("lineEdit_role")

        self.label_actions = QtWidgets.QLabel(self.centralwidget)
        self.label_actions.setGeometry(QtCore.QRect(20, 210, 231, 31))

        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_actions.setFont(font)
        self.label_actions.setObjectName("label_actions")

        if user_role[0] == "support":
            # Создаем кнопки только для системы поддержки
            self.pushButton_view_history = QtWidgets.QPushButton(self.centralwidget)
            self.pushButton_view_history.setGeometry(QtCore.QRect(20, 260, 191, 51))
            self.pushButton_view_history.setObjectName("pushButton_view_history")

            self.pushButton_view_processing_lots = QtWidgets.QPushButton(self.centralwidget)
            self.pushButton_view_processing_lots.setGeometry(QtCore.QRect(220, 260, 191, 51))
            self.pushButton_view_processing_lots.setObjectName("pushButton_view_processing_lots")

            self.pushButton_view_strikes = QtWidgets.QPushButton(self.centralwidget)
            self.pushButton_view_strikes.setGeometry(QtCore.QRect(420, 260, 191, 51))
            self.pushButton_view_strikes.setObjectName("pushButton_view_strikes")

            self.pushButton_view_strikes.clicked.connect(self.open_view_strikes)

            self.pushButton_view_processing_lots.clicked.connect(lambda: self.open_preview_lot_window(admin_info['contacts']))
        else:
            # Создаем все кнопки управления лотами
            self.pushButton_create_buffer = QtWidgets.QPushButton(self.centralwidget)
            self.pushButton_create_buffer.setGeometry(QtCore.QRect(20, 260, 191, 51))
            self.pushButton_create_buffer.setObjectName("pushButton_create_buffer")

            self.pushButton_create_lot = QtWidgets.QPushButton(self.centralwidget)
            self.pushButton_create_lot.setGeometry(QtCore.QRect(220, 260, 191, 51))
            self.pushButton_create_lot.setObjectName("pushButton_create_lot")

            self.pushButton_repeat_lot = QtWidgets.QPushButton(self.centralwidget)
            self.pushButton_repeat_lot.setGeometry(QtCore.QRect(420, 260, 191, 51))
            self.pushButton_repeat_lot.setObjectName("pushButton_repeat_lot")

            self.pushButton_view_history = QtWidgets.QPushButton(self.centralwidget)
            self.pushButton_view_history.setGeometry(QtCore.QRect(620, 260, 161, 51))
            self.pushButton_view_history.setObjectName("pushButton_view_history")

            self.pushButton_delete_lot = QtWidgets.QPushButton(self.centralwidget)
            self.pushButton_delete_lot.setGeometry(QtCore.QRect(20, 330, 191, 51))
            self.pushButton_delete_lot.setObjectName("pushButton_delete_lot")

            self.pushButton_view_finances = QtWidgets.QPushButton(self.centralwidget)
            self.pushButton_view_finances.setGeometry(QtCore.QRect(220, 330, 191, 51))
            self.pushButton_view_finances.setObjectName("pushButton_view_finances")

            self.pushButton_manage_participants = QtWidgets.QPushButton(self.centralwidget)
            self.pushButton_manage_participants.setGeometry(QtCore.QRect(420, 330, 191, 51))
            self.pushButton_manage_participants.setObjectName("pushButton_manage_participants")

            if user_role[0] == "super_admin":
                self.pushButton_refill_balance = QtWidgets.QPushButton(self.centralwidget)
                self.pushButton_refill_balance.setGeometry(QtCore.QRect(620, 330, 161, 51))
                self.pushButton_refill_balance.setObjectName("pushButton_refill_balance")

                self.pushButton_refill_balance.clicked.connect(self.open_refill_balance_window)

            self.create_lot_dialog = CreateLotDialog(user_role=user_role)
            self.create_buffer = CreateLotDialog(user_role=user_role, buffer=True)
            self.users_management_window = UsersManagementWindow(user_role)

            self.pushButton_view_finances.clicked.connect(self.open_view_finances_dialog)
            self.pushButton_create_lot.clicked.connect(self.open_create_lot_dialog)
            self.pushButton_create_buffer.clicked.connect(self.open_create_buffer)
            self.pushButton_delete_lot.clicked.connect(self.open_delete_lot_window)
            self.pushButton_repeat_lot.clicked.connect(lambda: self.open_recreate_lot_window(admin_info['contacts']))
            self.pushButton_view_history.clicked.connect(self.open_lots_history_window)
            self.pushButton_manage_participants.clicked.connect(self.open_users_management_window)

        self.lineEdit_name.setText(admin_info["first_name"])
        self.lineEdit_surname.setText(admin_info["second_name"])
        self.lineEdit_contact.setText(admin_info["contacts"])
        self.lineEdit_balance.setText(str(admin_info["balance"]))
        self.lineEdit_role.setText(str(admin_info["role"]))

        self.lineEdit_name.setReadOnly(True)
        self.lineEdit_surname.setReadOnly(True)
        self.lineEdit_contact.setReadOnly(True)
        self.lineEdit_balance.setReadOnly(True)
        self.lineEdit_role.setReadOnly(True)

        AdministratorMainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(AdministratorMainWindow, user_role=user_role)
        QtCore.QMetaObject.connectSlotsByName(AdministratorMainWindow)

    def retranslateUi(self, AdministratorMainWindow, user_role):
        _translate = QtCore.QCoreApplication.translate
        AdministratorMainWindow.setWindowTitle(_translate("AdministratorMainWindow", "Личный кабинет администратора"))

        self.label_personal_info.setText(_translate("AdministratorMainWindow", "Персональная информация"))
        self.label_name.setText(_translate("AdministratorMainWindow", "Имя:"))
        self.label_surname.setText(_translate("AdministratorMainWindow", "Фамилия:"))
        self.label_contact.setText(_translate("AdministratorMainWindow", "Контактная информация:"))
        self.label_balance.setText(_translate("AdministratorMainWindow", "Баланс:"))
        self.label_actions.setText(_translate("AdministratorMainWindow", "Действия"))
        self.label_role.setText(_translate("AdministratorMainWindow", "Роль:"))

        if user_role[0] == "support":
            self.pushButton_view_strikes.setText(_translate("AdministratorMainWindow", "Просмотреть страйки"))
            self.pushButton_view_processing_lots.setText(_translate("AdministratorMainWindow", "Лоты в обработке"))
        else:
            self.pushButton_create_buffer.setText(_translate("AdministratorMainWindow", "Создать лот в буфер"))
            self.pushButton_create_lot.setText(_translate("AdministratorMainWindow", "Создать лот"))
            self.pushButton_repeat_lot.setText(_translate("AdministratorMainWindow", "Повторно создать лот"))
            self.pushButton_delete_lot.setText(_translate("AdministratorMainWindow", "Удалить лот из аукциона"))
            self.pushButton_view_finances.setText(_translate("AdministratorMainWindow", "Просмотр финансов"))
            self.pushButton_manage_participants.setText(_translate("AdministratorMainWindow", "Управление участниками"))
        self.pushButton_view_history.setText(_translate("AdministratorMainWindow", "Просмотр истории торгов"))
        if user_role[0] == "super_admin":
            self.pushButton_refill_balance.setText(_translate("AdministratorMainWindow", "Пополнить баланс"))

    # Ниже методы открытия диалоговых окон для различных операций
    def open_users_management_window(self):
        self.users_management_window.update_users_table()
        self.users_management_window.show()

    def open_refill_balance_window(self):
        refil_balance = TopUpBalanceDialog()
        refil_balance.exec_()

    def open_delete_lot_window(self):
        active_lots = dbf.select("lots", "*", "WHERE status = ?", ("одобрен",))
        delete_lot = DeleteLotDialog(active_lots)
        delete_lot.exec_()

    def open_recreate_lot_window(self, approver_username):
        lots_for_recreate = dbf.select("lots", "*", "WHERE status = 'отклонен' OR status = 'снят с аукциона' OR status = 'завершен'", ())
        recreate_lot = RecreateLotDialog(lots_for_recreate, approver_username)
        recreate_lot.exec_()

    def open_lots_history_window(self):
        lots_history = AuctionHistoryDialog()
        lots_history.exec_()

    def open_view_finances_dialog(self):
        view_finances = FinancesViewer()
        view_finances.exec_()

    def open_preview_lot_window(self, approver_username):
        lots_info = dbf.select("lots", "*", "WHERE status = ?", ("обрабатывается",))
        preview_window = PreviewLotWindow(lots_info, approver_username)
        preview_window.exec_()

    def open_view_strikes(self):
        strikes_info = dbf.select("strikes", "*", "", ())
        strikes_viewer = StrikesViewerWindow(strikes_info)
        strikes_viewer.exec_()

    def open_create_lot_dialog(self):
        self.create_lot_dialog.exec_()

    def open_create_buffer(self):
        self.create_buffer.exec_()

def get_admin_info(user_role):
    # Получение информации об администраторе из базы данных
    admin_info = dbf.select("admin_users", "first_name, second_name, contacts, role", "WHERE id = ?", (user_role[1],))[0]
    try:
        admin_balance = dbf.select("finances", "current_balance", "WHERE id = (SELECT id FROM finances ORDER BY id DESC LIMIT 1)", ())[0][0]
    except:
        admin_balance = 0
    return {
        "first_name": admin_info[0],
        "second_name": admin_info[1],
        "contacts": admin_info[2],
        "balance": admin_balance,
        "role": admin_info[3]
    }


class DeleteLotDialog(QtWidgets.QDialog):
    def __init__(self, active_lots):
        super().__init__()
        self.setWindowTitle("Удаление лота")
        self.setGeometry(100, 100, 400, 300)

        self.active_lots = active_lots

        # Создаем виджет списка лотов пользователя
        self.lot_list = QtWidgets.QListWidget(self)
        self.lot_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)  # Режим выбора нескольких элементов
        for lot in self.active_lots:
            item = QtWidgets.QListWidgetItem(f"{lot[0]} - {lot[5]}")
            self.lot_list.addItem(item)

        # Создаем кнопку для удаления лота
        self.delete_button = QtWidgets.QPushButton("Удалить выбранные лоты", self)
        self.delete_button.clicked.connect(self.delete_lot)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Выберите лоты для удаления:", self))
        layout.addWidget(self.lot_list)
        layout.addWidget(self.delete_button)
        self.setLayout(layout)

    def delete_lot(self):
        # Получаем выбранные лоты
        selected_items = self.lot_list.selectedItems()
        if selected_items:
            for selected_item in selected_items:
                lot_id = selected_item.text().split('-')[0].strip()
                admin_balance = dbf.select("finances", "current_balance",
                                           "WHERE id = (SELECT id FROM finances ORDER BY id DESC LIMIT 1)", ())[0][0]
                lot_current_bet = dbf.select("lots", "current_bet, start_price", "WHERE id = ?", (lot_id,))[0]
                if lot_current_bet[0] == None:
                    lot_current_bet = lot_current_bet[1]
                else:
                    lot_current_bet = lot_current_bet[0]
                five_percent = int(lot_current_bet)*0.05
                if int(admin_balance) < five_percent:
                    QtWidgets.QMessageBox.information(self, "Недостаточный баланс", "Недостаточно денег на балансе.")
                    return
                new_current_balance = int(admin_balance)-five_percent
                delete_lot(lot_id=lot_id)
                dbf.update("lots", ("status", "снят с аукциона"), ('id', lot_id))
                dbf.insert("finances", "current_balance, lot_id, count, comment", (new_current_balance, lot_id,
                                                                                   f"-{five_percent}", "Удаление лота с аукциона."))
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Произошла ошибка при удалении лота.")
            QtWidgets.QMessageBox.information(self, "Успех", "Лоты успешно удалены.")
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Предупреждение", "Выберите лоты для удаления.")


class StrikesViewerWindow(QtWidgets.QDialog):
    def __init__(self, strikes_info):
        super().__init__()

        self.setWindowTitle("Просмотр страйков")
        # Создаем макет окна
        layout = QtWidgets.QVBoxLayout()

        # Отображаем информацию о страйках и кнопки для подтверждения или отклонения
        strikes_label = QtWidgets.QLabel("Страйки:")
        layout.addWidget(strikes_label)
        for strike_info in strikes_info:
            strike_layout = QtWidgets.QVBoxLayout()
            strike_label = QtWidgets.QLabel(f"Пользователь: {strike_info[1]}, Комментарий: {strike_info[2]}")
            strike_layout.addWidget(strike_label)
            approve_button = QtWidgets.QPushButton("Подтвердить")
            reject_button = QtWidgets.QPushButton("Отклонить")
            approve_button.clicked.connect(
                lambda _, strike_id=strike_info[0], strike_username=strike_info[1],
                       strike_value=strike_info[3]: self.approve_strike(strike_id, strike_username,
                                                                        strike_value, strikes_info))
            reject_button.clicked.connect(
                lambda _, strike_id=strike_info[0]: self.reject_strike(strike_id, strikes_info))
            strike_layout.addWidget(approve_button)
            strike_layout.addWidget(reject_button)
            layout.addLayout(strike_layout)

        self.setLayout(layout)
        self.resize(300, 50)

    def approve_strike(self, strike_id, strike_username, strike_value, strikes_info):
        dbf.update("users", ("strikes", strike_value+1),("username", strike_username))
        if strike_value+1 >= 3:
            dbf.update("users", ("status", "banned"), ("username", strike_username))
        dbf.delete("strikes", ("id", strike_id))
        dbf.update("strikes", ("value", strike_value+1), ("username", strike_username))
        for strike in strikes_info:
            if strike[0] == strike_id:
                strikes_info.remove(strike)
        self.accept()
        StrikesViewerWindow(strikes_info).exec_()

    def reject_strike(self, strike_id, strikes_info):
        dbf.delete("strikes", ("id", strike_id))
        for strike in strikes_info:
            if strike[0] == strike_id:
                strikes_info.remove(strike)
        self.accept()
        StrikesViewerWindow(strikes_info).exec_()


class PreviewLotWindow(QtWidgets.QDialog):
    def __init__(self, lots_info, approver_username):
        super().__init__()
        self.setWindowTitle("Предварительный просмотр лота")
        self.lots_info = lots_info

        # Создаем макет окна
        layout = QtWidgets.QVBoxLayout()

        # Создаем комбо-бокс для выбора лота
        self.lot_combo = QtWidgets.QComboBox()
        self.lot_combo.addItem("Выберите лот")
        for lot in lots_info:
            if lot[10] and lot[10] != None:
                add_item_text = f"Буффер! Лот ID: {lot[0]} - {lot[3]} - {lot[4]}"
            else:
                add_item_text = f"Лот ID: {lot[0]} - {lot[3]} - {lot[4]}"
            self.lot_combo.addItem(add_item_text)
        layout.addWidget(self.lot_combo)

        # Создаем кнопку для открытия просмотра выбранного лота
        view_button = QtWidgets.QPushButton("Просмотр")
        view_button.clicked.connect(lambda: self.open_preview(approver_username))
        layout.addWidget(view_button)

        self.setLayout(layout)

        self.resize(300, 100)

    def open_preview(self, approver_username):
        # Получаем выбранный лот из комбо-бокса
        selected_lot_index = self.lot_combo.currentIndex()
        if selected_lot_index != 0:
            selected_lot_info = self.lots_info[selected_lot_index - 1]
            preview_dialog = LotPreviewDialog(selected_lot_info, approver_username)
            preview_dialog.exec_()
            self.accept()


class RecreateLotDialog(QtWidgets.QDialog):
    def __init__(self, available_lots, approver_username):
        super().__init__()
        self.setWindowTitle("Выбор лота для повторного создания")
        self.setGeometry(100, 100, 400, 300)

        self.available_lots = available_lots

        # Создаем виджет списка лотов
        self.lot_list = QtWidgets.QListWidget(self)
        for lot in self.available_lots:
            item = QtWidgets.QListWidgetItem(f"{lot[0]} - {lot[5]}")
            self.lot_list.addItem(item)

        # Создаем кнопку для выбора лота
        self.select_button = QtWidgets.QPushButton("Выбрать", self)
        self.select_button.clicked.connect(lambda: self.select_lot(approver_username))

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Выберите лот для повторного создания:", self))
        layout.addWidget(self.lot_list)
        layout.addWidget(self.select_button)
        self.setLayout(layout)

    def select_lot(self, approver_username):
        selected_item = self.lot_list.currentItem()
        if selected_item:
            lot_id = selected_item.text().split('-')[0].strip()
            #лот в списке доступных лотов
            selected_lot = None
            for lot in self.available_lots:
                if str(lot[0]) == lot_id:
                    selected_lot = lot
                    break

            if selected_lot:
                preview_dialog = LotPreviewDialog(selected_lot, approver_username)
                preview_dialog.exec_()
                self.accept()  # Закрываем диалоговое окно после завершения операции
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось найти выбранный лот.")
        else:
            QtWidgets.QMessageBox.warning(self, "Предупреждение", "Выберите лот для повторного создания.")


class AuctionHistoryDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("История торгов")
        self.setGeometry(100, 100, 400, 300)

        # Создаем элементы управления для выбора статуса лотов
        self.status_combo = QtWidgets.QComboBox(self)
        self.status_combo.addItem("Завершенные")
        self.status_combo.addItem("Отклоненные")
        self.status_combo.addItem("Снятые с аукциона")
        self.status_combo.addItem("Одобренные")

        # Создаем кнопку для применения фильтра
        self.apply_button = QtWidgets.QPushButton("Применить", self)
        self.apply_button.clicked.connect(self.apply_filter)

        # Создаем список для хранения полученных лотов
        self.lots = []

        # Создаем список для отображения лотов
        self.lot_list = QtWidgets.QListWidget(self)
        self.lot_list.itemClicked.connect(self.show_lot_preview)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Выберите статус лотов:", self))
        layout.addWidget(self.status_combo)
        layout.addWidget(self.apply_button)
        layout.addWidget(self.lot_list)
        self.setLayout(layout)

    def apply_filter(self):
        selected_status = self.status_combo.currentText()
        # Получаем лоты из базы данных в зависимости от выбранного статуса
        if selected_status == "Завершенные":
            self.lots = dbf.select("lots", "*", "WHERE status = ?", ("завершен",))
        elif selected_status == "Отклоненные":
            self.lots = dbf.select("lots", "*", "WHERE status = ?", ("отклонен",))
        elif selected_status == "Снятые с аукциона":
            self.lots = dbf.select("lots", "*", "WHERE status = ?", ("снят с аукциона",))
        elif selected_status == "Одобренные":
            self.lots = dbf.select("lots", "*", "WHERE status = ?", ("одобрен",))

        # Отображаем лоты в списке
        self.show_lots_in_list()

    def show_lots_in_list(self):
        self.lot_list.clear()
        for lot_info in self.lots:
            item = QtWidgets.QListWidgetItem(f"Лот ID: {lot_info[0]} - {lot_info[5]}")
            item.lot_info = lot_info  # Сохраняем информацию о лоте в элемент списка
            self.lot_list.addItem(item)

    def show_lot_preview(self, item):
        # Отображаем предварительный просмотр выбранного лота
        preview_dialog = LotPreviewDialog(item.lot_info)
        preview_dialog.exec_()


class LotPreviewDialog(QtWidgets.QDialog):
    def __init__(self, lot_info, approver_username=None):
        super().__init__()
        self.setWindowTitle("Предварительный просмотр лота")
        # Создаем макет окна
        layout = QtWidgets.QVBoxLayout()

        # Отображаем информацию о лоте
        qlabel_text = f"ID лота: {lot_info[0]}\nКонтакты продавца: {lot_info[3]}\nОписание: {lot_info[5]}\nСтратовая цена: {lot_info[2]}\nНачало - Окончание торгов: {lot_info[6]} - {lot_info[7]}"
        if lot_info[10] and lot_info[10] != None:
            qlabel_text += f"\nДата публикации лота: {lot_info[10]}"
        lot_label = QtWidgets.QLabel(qlabel_text)
        layout.addWidget(lot_label)

        # Создаем виджет прокрутки для изображений
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Создаем область для содержимого
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QHBoxLayout(content_widget)

        # Отображаем изображения лота
        for image_path in lot_info[1].split(", "):
            image_label = QtWidgets.QLabel()
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaledToWidth(200)  # Изменяем размер изображения
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(image_label)

        # Добавляем область для содержимого в виджет прокрутки
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        if approver_username:
            # Создаем кнопки "Одобрить" и "Отклонить"
            approve_button = QtWidgets.QPushButton("Создать лот")
            reject_button = QtWidgets.QPushButton("Отклонить")
            approve_button.clicked.connect(lambda : self.approve_lot(lot_info, approver_username))
            reject_button.clicked.connect(lambda : self.reject_lot(lot_info, approver_username))
            layout.addWidget(approve_button)
            layout.addWidget(reject_button)

        self.setLayout(layout)

    def approve_lot(self, lot_info, approver_username):
        if not lot_info[10] or lot_info[10] == None:
            channel_create_lot(lot_info=lot_info)
            dbf.update("lots", ("status", "одобрен"), ("id", lot_info[0]))
            dbf.update("lots", ("approver", approver_username), ("id", lot_info[0]))
        else:
            dbf.update("lots", ("status", "одобрен"), ("id", lot_info[0]))
            dbf.update("lots", ("approver", approver_username), ("id", lot_info[0]))
        self.accept()

    def reject_lot(self, lot_info, approver_username):
        dbf.update("lots", ("status", "отклонен"), ("id", lot_info[0]))
        dbf.update("lots", ("approver", approver_username), ("id", lot_info[0]))
        self.reject()


class FinancesViewer(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Просмотр финансов")
        self.setGeometry(100, 100, 600, 400)

        # Создаем виджет таблицы для отображения данных о финансах
        self.table_widget = QtWidgets.QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Текущий баланс", "ID лота", "Сумма", "Комментарий"])

        # Получаем данные о финансовых операциях из базы данных
        finances_data = dbf.select("finances", "*", "", ())

        # Сортируем данные в обратном порядке
        finances_data.reverse()

        # Заполняем таблицу данными о финансах
        self.fill_table(finances_data)

        # Запрещаем редактирование ячеек в таблице
        self.table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.table_widget)
        self.setLayout(layout)

    def fill_table(self, data):
        self.table_widget.setRowCount(len(data))
        for row, record in enumerate(data):
            for col, value in enumerate(record):
                item = QtWidgets.QTableWidgetItem(str(value))
                self.table_widget.setItem(row, col, item)


class UsersManagementWindow(QtWidgets.QMainWindow):
    def __init__(self, user_role):
        super().__init__()
        self.user_role = user_role[0]

        self.setWindowTitle("Управление участниками")
        self.resize(800, 600)

        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.search_edit = QtWidgets.QLineEdit(self.central_widget)
        self.search_edit.setGeometry(QtCore.QRect(20, 20, 200, 30))
        self.search_edit.setPlaceholderText("Введите username")
        self.search_edit.textChanged.connect(self.search_user)

        self.table_view = QtWidgets.QTableView(self.central_widget)
        self.table_view.setGeometry(QtCore.QRect(20, 60, 760, 480))
        self.table_model = QtGui.QStandardItemModel()
        self.table_view.setModel(self.table_model)


    def update_users_table(self):
        users_data = dbf.select("users", "*", "", ())
        self.table_model.clear()
        self.table_model.setHorizontalHeaderLabels(["ID", "User ID", "Username", "Lots IDs", "Strikes", "Actions"])
        for row_num, user_info in enumerate(users_data):
            self.table_model.setRowCount(row_num + 1)
            for col_num, data in enumerate(user_info):
                item = QtGui.QStandardItem(str(data))
                self.table_model.setItem(row_num, col_num, item)
            combobox = QtWidgets.QComboBox()
            combobox.addItem("Действия")
            if user_info[6] == "banned":
                combobox.addItem("Разблокировать")
            elif user_info[6] == "unbanned":
                combobox.addItem("Заблокировать")
            combobox.addItem("Кинуть страйк")
            if self.user_role == "super_admin":
                combobox.addItem("Назначить роль")
            combobox.currentIndexChanged.connect(lambda index, user_data=user_info: self.handle_action(index, user_data))
            self.table_view.setIndexWidget(self.table_model.index(row_num, 5), combobox)

    def handle_action(self, index, user_data):
        action = {
            0: lambda: None,  # Пустое действие
            1: lambda: self.block_user(user_data),
            2: lambda: self.give_strike(user_data),
            3: lambda: self.assign_role(user_data)
        }.get(index)
        if action:
            action()

    def search_user(self):
        username = self.search_edit.text()
        if not username:
            self.update_users_table()
            return

        # Выполняем запрос к базе данных для поиска пользователя
        users_data = dbf.select("users", "*", "WHERE username LIKE ?", (f"%{username}%",))

        # Очищаем таблицу перед обновлением
        self.table_model.clear()
        self.table_model.setHorizontalHeaderLabels(["ID", "User ID", "Username", "Lots IDs", "Actions"])
        for row_num, user_info in enumerate(users_data):
            self.table_model.setRowCount(row_num + 1)
            for col_num, data in enumerate(user_info):
                item = QtGui.QStandardItem(str(data))
                self.table_model.setItem(row_num, col_num, item)
            combobox = QtWidgets.QComboBox()
            combobox.addItem("Действия")
            if user_info[6] == "banned":
                combobox.addItem("Разблокировать")
            elif user_info[6] == "unbanned":
                combobox.addItem("Заблокировать")
            combobox.addItem("Кинуть страйк")
            if self.user_role == "super_admin":
                combobox.addItem("Назначить роль")
            combobox.currentIndexChanged.connect(lambda index, user_data=user_info: self.handle_action(index, user_data))
            self.table_view.setIndexWidget(self.table_model.index(row_num, 5), combobox)

    def block_user(self, user_data):
        if user_data[6] == "unbanned":
            block_unblock = "заблокировать"
        else:
            block_unblock = "разблокировать"
        reply = QMessageBox.question(self, 'Подтверждение',
                                     f'Вы уверены, что хотите {block_unblock} пользователя {user_data[2]}',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if user_data[6] == "unbanned":
                dbf.update("users", ("status", "banned"), ("username", user_data[2]))
            else:
                dbf.update("users", ("status", "unbanned"), ("username", user_data[2]))
                dbf.update("users", ("strikes", 0), ("username", user_data[2]))
            self.update_users_table()
        else:
            self.update_users_table()

    def give_strike(self, user_data):
        comment_text, ok_pressed = QtWidgets.QInputDialog.getText(self, "Введите комментарий", "Комментарий:", QtWidgets.QLineEdit.Normal, "")
        if ok_pressed:
            reply = QMessageBox.question(self, 'Подтверждение',
                                         f'Вы уверены, что хотите выдать страйк пользователю {user_data[2]} с комментарием: {comment_text}?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                dbf.insert("strikes", "username, comment, value", (user_data[2], comment_text, user_data[4]))
                self.update_users_table()
            else:
                self.update_users_table()

    def assign_role(self, user_data):
        roles = ["admin", "support", "super_admin"]
        role, ok = QtWidgets.QInputDialog.getItem(self, "Выбор роли",
                                        f"Выберите роль для пользователя {user_data[2]}:",
                                        roles, 0, False)
        if ok:
            assign_role_dialog = AssignRoleDialog(user_data, role)
            assign_role_dialog.exec_()
            self.update_users_table()
        else:
            self.update_users_table()


class AssignRoleDialog(QtWidgets.QDialog):
    def __init__(self, user_data, selected_role):
        super().__init__()
        self.setWindowTitle("Назначение роли")
        self.setGeometry(100, 100, 400, 300)

        self.user_data = user_data
        self.selected_role = selected_role

        # Создаем виджеты для заполнения данных администратора
        self.first_name_label = QtWidgets.QLabel("Имя:", self)
        self.first_name_edit = QtWidgets.QLineEdit(self)
        self.second_name_label = QtWidgets.QLabel("Фамилия:", self)
        self.second_name_edit = QtWidgets.QLineEdit(self)
        self.contacts_label = QtWidgets.QLabel("Контакты:", self)
        self.contacts_edit = QtWidgets.QLineEdit(self)
        self.username_label = QtWidgets.QLabel("Имя пользователя:", self)
        self.username_edit = QtWidgets.QLineEdit(self)
        self.password_label = QtWidgets.QLabel("Пароль:", self)
        self.password_edit = QtWidgets.QLineEdit(self)
        self.role_label = QtWidgets.QLabel("Роль:", self)
        self.role_edit = QtWidgets.QLabel(self)
        self.role_edit.setText(selected_role)  # Устанавливаем выбранную роль

        # Создаем кнопки для сохранения и отмены
        self.save_button = QtWidgets.QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.save_data)
        self.cancel_button = QtWidgets.QPushButton("Отмена", self)
        self.cancel_button.clicked.connect(self.close)

        # Размещаем виджеты на макете
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.first_name_label, 0, 0)
        layout.addWidget(self.first_name_edit, 0, 1)
        layout.addWidget(self.second_name_label, 1, 0)
        layout.addWidget(self.second_name_edit, 1, 1)
        layout.addWidget(self.contacts_label, 2, 0)
        layout.addWidget(self.contacts_edit, 2, 1)
        layout.addWidget(self.username_label, 3, 0)
        layout.addWidget(self.username_edit, 3, 1)
        layout.addWidget(self.password_label, 4, 0)
        layout.addWidget(self.password_edit, 4, 1)
        layout.addWidget(self.role_label, 5, 0)
        layout.addWidget(self.role_edit, 5, 1)
        layout.addWidget(self.save_button, 6, 0)
        layout.addWidget(self.cancel_button, 6, 1)
        self.setLayout(layout)

    def save_data(self):
        # Получаем данные из полей ввода
        first_name = self.first_name_edit.text()
        second_name = self.second_name_edit.text()
        contacts = self.contacts_edit.text()
        username = self.username_edit.text()
        password = self.password_edit.text()
        role = self.selected_role

        success_text = f"Пользователь {self.user_data[2]} получил роль {role}"

        reply = QtWidgets.QMessageBox.question(self, 'Подтверждение',
                                               f'Вы уверены, что хотите назначить роль {self.selected_role} пользователю {self.user_data[2]}',
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QMessageBox.Yes:
            dbf.insert("admin_users", "user_id, first_name, second_name, contacts, username, password, role",
                       (self.user_data[1], first_name, second_name, contacts, username, password, role))
            QtWidgets.QMessageBox.information(self, "Успех", success_text)
            self.accept()
        else:
            return


class TopUpBalanceDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пополнение баланса")
        self.setGeometry(100, 100, 300, 150)

        self.amount_label = QtWidgets.QLabel("Сумма для пополнения:", self)
        self.amount_edit = QtWidgets.QLineEdit(self)

        self.confirm_button = QtWidgets.QPushButton("Подтвердить", self)
        self.confirm_button.clicked.connect(self.confirm_top_up)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.amount_label)
        layout.addWidget(self.amount_edit)
        layout.addWidget(self.confirm_button)
        self.setLayout(layout)

    def confirm_top_up(self):
        amount = self.amount_edit.text()
        try:
            admin_balance = dbf.select("finances", "current_balance",
                                       "WHERE id = (SELECT id FROM finances ORDER BY id DESC LIMIT 1)", ())[0][0]
        except:
            admin_balance = 0
        new_current_balance = int(admin_balance) + int(amount)
        dbf.insert("finances", "current_balance, count, comment", (new_current_balance, f"+{amount}", "Пополнение баланса."))
        self.close()


class CreateLotDialog(QtWidgets.QDialog):
    def __init__(self, user_role, buffer=None):
        super().__init__()
        self.lot_creator_info = get_admin_info(user_role)
        self.setWindowTitle("Создание лота в буфер")
        # Добавляем виджет для отображения информации об администраторе
        self.admin_info_label = QtWidgets.QLabel(f"Информация об администраторе:\n"
                                                 f"Имя: {self.lot_creator_info['first_name']}\n"
                                                 f"Фамилия: {self.lot_creator_info['second_name']}\n"
                                                 f"Username: {self.lot_creator_info['contacts']}", self)
        if buffer:
            self.setWindowTitle("Создание лота в буфер")

            self.date_of_lot = QtWidgets.QLabel("Дата публикации лота:", self)
            self.date_time_edit = QtWidgets.QDateTimeEdit(QtCore.QDateTime.currentDateTime(), self)
        else:
            self.setWindowTitle("Создание лота")
        self.setGeometry(100, 100, 600, 400)

        # Добавляем виджет для отображения выбранных файлов
        self.attached_files_label = QtWidgets.QLabel("Прикрепленные файлы:", self)
        self.attached_files_edit = QtWidgets.QLineEdit(self)
        self.attached_files_edit.setReadOnly(True)
        self.attach_button = QtWidgets.QPushButton("Прикрепить файлы", self)
        self.attach_button.clicked.connect(self.attach_files)

        self.image_label = QtWidgets.QLabel("Изображение(я):", self)
        self.image_edit = QtWidgets.QLineEdit(self)
        self.image_edit.setReadOnly(True)
        self.image_button = QtWidgets.QPushButton("Выбрать", self)
        self.image_button.clicked.connect(self.choose_images)

        self.start_price_label = QtWidgets.QLabel("Стартовая цена:", self)
        self.start_price_edit = QtWidgets.QLineEdit(self)

        self.seller_link_label = QtWidgets.QLabel("Ссылка на продавца:", self)
        self.seller_link_edit = QtWidgets.QLineEdit(self)

        self.location_label = QtWidgets.QLabel("Геолокация товара:", self)
        self.location_edit = QtWidgets.QLineEdit(self)

        self.description_label = QtWidgets.QLabel("Описание и дополнительная информация:", self)
        self.description_edit = QtWidgets.QTextEdit(self)

        self.start_end_time_label = QtWidgets.QLabel("Время старта и окончания:", self)
        self.start_time_edit = QtWidgets.QDateTimeEdit(QtCore.QDateTime.currentDateTime(), self)
        self.end_time_edit = QtWidgets.QDateTimeEdit(QtCore.QDateTime.currentDateTime().addDays(7), self)

        self.create_button = QtWidgets.QPushButton("Создать лот", self)
        self.create_button.clicked.connect(lambda: self.create_lot(self.lot_creator_info['contacts'], buffer))

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.admin_info_label)
        layout.addWidget(self.attached_files_label)
        layout.addWidget(self.attached_files_edit)
        layout.addWidget(self.attach_button)
        layout.addWidget(self.image_label)
        layout.addWidget(self.image_edit)
        layout.addWidget(self.image_button)
        layout.addWidget(self.start_price_label)
        layout.addWidget(self.start_price_edit)
        layout.addWidget(self.seller_link_label)
        layout.addWidget(self.seller_link_edit)
        layout.addWidget(self.location_label)
        layout.addWidget(self.location_edit)
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_edit)
        layout.addWidget(self.start_end_time_label)
        layout.addWidget(self.start_time_edit)
        layout.addWidget(self.end_time_edit)
        if buffer:
            layout.addWidget(self.date_of_lot)
            layout.addWidget(self.date_time_edit)
        layout.addWidget(self.create_button)
        self.setLayout(layout)

    def attach_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("All Files (*)")
        file_names, _ = file_dialog.getOpenFileNames(self, "Прикрепить файлы", "", "All Files (*)",
                                                     options=options)
        if file_names:
            new_file_names = []
            for file_name in file_names:
                # Перемещаем файлы в папку в директории проекта
                destination_folder = "attach_files"  # Имя папки для сохранения файлов
                try:
                    shutil.copy(file_name, destination_folder)
                except:
                    pass
                new_file_names.append(f"attach_files/{file_name.split('/')[::-1][0]}")
            # Обновляем текстовое поле с именами выбранных файлов
            self.attached_files_edit.setText(", ".join(new_file_names))

    def choose_images(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
        file_names, _ = file_dialog.getOpenFileNames(self, "Выберите изображения", "", "Images (*.png *.jpg *.jpeg)",
                                                     options=options)
        if file_names:
            new_file_names = []
            for file_name in file_names:
                # Перемещаем файлы в папку в директории проекта
                destination_folder = "images"  # Имя папки для сохранения изображений
                try:
                    shutil.copy(file_name, destination_folder)
                except:
                    pass
                new_file_names.append(f"images/{file_name.split('/')[::-1][0]}")
            # Обновляем текстовое поле с именами выбранных файлов
            self.image_edit.setText(", ".join(new_file_names))

    def clear_fields(self):
        # Очистка текстовых полей
        self.image_edit.clear()
        self.start_price_edit.clear()
        self.seller_link_edit.clear()
        self.location_edit.clear()
        self.description_edit.clear()

    def create_lot(self, creator_username, buffer=None):
        # Получаем значения полей из виджетов
        images = self.image_edit.text()
        attached_files = self.attached_files_edit.text()
        start_price = self.start_price_edit.text()
        seller_link = self.seller_link_edit.text()
        location = self.location_edit.text()
        description = self.description_edit.toPlainText()
        start_time = self.start_time_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        end_time = self.end_time_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        if buffer:
            date_of_lot = self.date_time_edit.dateTime().toString("yyyy-MM-dd hh:mm")

        # Проверяем, что все обязательные поля заполнены
        if not images or not start_price or not seller_link or not location or not description:
            QtWidgets.QMessageBox.warning(self, "Внимание", "Пожалуйста, заполните все обязательные поля.")
            return

        # Вставляем новый лот в базу данных
        try:
            if buffer:
                dbf.insert("lots",
                           ("images, start_price, seller_url, location, description, start_time, end_time, attached_files, buffer, lot_creator"),
                           (images, start_price, seller_link, location, description, start_time, end_time,
                            attached_files, date_of_lot, creator_username, ))
                success_text = f"Лот успешно создан в буфер. Дата публикации лота: {date_of_lot}"
            else:
                dbf.insert("lots",
                           ("images, start_price, seller_url, location, description, start_time, end_time, attached_files, lot_creator"),
                           (images, start_price, seller_link, location, description, start_time, end_time,
                            attached_files, creator_username))
                success_text = "Лот успешно создан."
            QtWidgets.QMessageBox.information(self, "Успех", success_text)
            self.clear_fields()
            self.close()  # Закрываем окно после успешного создания лота
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка", f"Произошла ошибка при создании лота: {str(e)}")

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_AdministratorMainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
