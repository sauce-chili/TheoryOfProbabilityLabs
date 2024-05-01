from PyQt5.QtWidgets import QFileDialog


def load_text_file(widget):
    filter = 'Текстовые файлы (*.txt);; Все файлы (*.*)'
    filename = QFileDialog.getOpenFileName(widget, 'Выберите файл', filter=filter)

    if filename[0] != '':
        widget.currentFile = filename[0]
        widget.selectedFile.setText(widget.currentFile)


def parse_statistic_file(filename):
    data = []
    current_token = ""
    with open(filename, encoding="utf-8") as fobj:
        while True:
            char = fobj.read(1)
            if not char:
                break

            if not char.isdigit() and char not in "-., " and not char.isspace():
                raise ValueError("Неверный символ в файле статистических данных")
            
            if not char.isspace():
                current_token += char
            else:
                if "," in current_token or "." in current_token:
                    data.append(float(current_token.replace(",", ".")))
                elif current_token:
                    data.append(int(current_token))
                current_token = ""
    if current_token:
        if "," in current_token or "." in current_token:
            data.append(float(current_token.replace(",", ".")))
        else:
            data.append(int(current_token))
    return data
        