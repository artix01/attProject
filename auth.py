from PyQt5 import QtWidgets, QtCore, QtGui
import database_functions as dbf
from management_system import Ui_AdministratorMainWindow

class LoginWindow(QtWidgets.QWidget):
    def setupUi(self):
        self.setWindowTitle("Authorization")
        self.resize(300, 150)

        # Создание и настройка виджетов интерфейса
        self.username_label = QtWidgets.QLabel("Username:")
        self.username_edit = QtWidgets.QLineEdit()
        self.password_label = QtWidgets.QLabel("Password:")
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login_button = QtWidgets.QPushButton("Login")

        # Создание и настройка макета
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_edit)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

        # Подключение сигнала нажатия кнопки к слоту
        self.login_button.clicked.connect(self.login)

    def login(self):
        # Получение введенного имени пользователя и пароля
        username = self.username_edit.text()
        password = self.password_edit.text()

        # Проверка пароля в базе данных
        result = dbf.select("admin_users", "role, id", "WHERE username=? AND password=?", (username, password))
        if result:
            # Если пароль верный, открываем главное окно администратора
            role = result[0][0]
            id = result[0][1]
            self.open_dashboard(role, id)
        else:
            # В случае неверного пароля выводим сообщение об ошибке
            QtWidgets.QMessageBox.warning(self, "Error", "Invalid username or password")

    def open_dashboard(self, role, id):
        # Создание и отображение главного окна администратора
        self.admin_window = QtWidgets.QMainWindow()
        self.admin_ui = Ui_AdministratorMainWindow()
        self.admin_ui.setupUi(self.admin_window, role=role, id=id)
        self.admin_window.show()
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    login_window = LoginWindow()
    login_window.setupUi()
    login_window.show()
    app.exec_()