from PyQt5.QtWidgets import QErrorMessage


def show_error(title: str, message: str) -> None:
    error_dialog = QErrorMessage()
    error_dialog.setWindowTitle(title)
    error_dialog.showMessage(message)
    error_dialog.exec()
