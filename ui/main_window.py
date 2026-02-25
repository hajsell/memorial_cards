from PySide6.QtWidgets import (
    QMainWindow, QWidget, QFormLayout,
    QLineEdit, QComboBox, QDateEdit,
    QPushButton, QSplitter
)
from PySide6.QtCore import Qt, QDate, QLocale, QUrl
from ui.pdf_preview_widget import PdfPreviewWidget
from pdf_generator import generate_single_card_pdf, generate_a4_sheet_pdf
from pathlib import Path
from datetime import datetime
from PySide6.QtGui import QDesktopServices, QIcon
import os
import json
import sys

polish_locale = QLocale(
    QLocale.Language.Polish,
    QLocale.Country.Poland
)

def resource_path(relative_path: str) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path.cwd()))
    return base_path / relative_path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Generator Kart")
        self.resize(1000, 720)
        self.setWindowIcon(QIcon(str(resource_path("assets/icon.ico"))))

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        form_widget = QWidget()
        form_layout = QFormLayout()

        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Mężczyzna", "Kobieta"])

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Imię i nazwisko")

        self.death_date = QDateEdit()
        self.death_date.setCalendarPopup(True)
        self.death_date.setDate(QDate.currentDate())

        self.burial_date = QDateEdit()
        self.burial_date.setCalendarPopup(True)
        self.burial_date.setDate(QDate.currentDate())

        self.burial_place = QLineEdit()
        self.burial_place.setPlaceholderText("Miejsce pochówku")

        self.prayer_combo = QComboBox()
        self.prayers = self.load_prayers()

        form_layout.addRow("Płeć:", self.gender_combo)
        form_layout.addRow("Imię i nazwisko:", self.name_input)
        form_layout.addRow("Data śmierci:", self.death_date)
        form_layout.addRow("Data pochowówku:", self.burial_date)
        form_layout.addRow("Miejsce pochówku:", self.burial_place)
        form_layout.addRow("Modlitwa:", self.prayer_combo)

        self.generate_button = QPushButton("Generuj arkusz A4")
        form_layout.addRow(self.generate_button)

        self.open_folder_button = QPushButton("Folder z dokumentami")
        form_layout.addRow(self.open_folder_button)

        form_widget.setLayout(form_layout)

        self.preview = PdfPreviewWidget()

        splitter.addWidget(form_widget)
        splitter.addWidget(self.preview)
        splitter.setSizes([350, 650])

        self.connect_signals()
        self.update_preview()

    def load_prayers(self):
        prayers = {}

        prayers_path = resource_path("assets/prayers")

        if not prayers_path.exists():
            print("Nie znaleziono folderu:", prayers_path)
            return prayers

        for file in prayers_path.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    prayers[data["title"]] = data["text"]
            except Exception as e:
                print(f"Błąd w pliku {file.name}: {e}")

        self.prayer_combo.addItems(list(prayers.keys()))
        return prayers

    def connect_signals(self):
        self.gender_combo.currentIndexChanged.connect(self.update_preview)
        self.name_input.textChanged.connect(self.update_preview)
        self.death_date.dateChanged.connect(self.update_preview)
        self.burial_date.dateChanged.connect(self.update_preview)
        self.burial_place.textChanged.connect(self.update_preview)
        self.prayer_combo.currentIndexChanged.connect(self.update_preview)
        self.generate_button.clicked.connect(self.generate_a4)
        self.open_folder_button.clicked.connect(open_output_folder)

    def build_data(self):
        gender = self.gender_combo.currentText()
        name = self.name_input.text()

        death_date = polish_locale.toString(
            self.death_date.date(),
            "dd MMMM yyyy"
        )

        burial_date = polish_locale.toString(
            self.burial_date.date(),
            "dd MMMM yyyy"
        )

        burial_place = self.burial_place.text()

        prayer_title = self.prayer_combo.currentText()
        prayer_text = self.prayers.get(prayer_title, "")

        if gender == "Mężczyzna":
            dynamic = (
                f"zmarły {death_date} r.\n"
                f"pochowany {burial_date} r.\n"
                f"na {burial_place}"
            )
        else:
            dynamic = (
                f"zmarła {death_date} r.\n"
                f"pochowana {burial_date} r.\n"
                f"na {burial_place}"
            )

        return {
            "name": name,
            "dynamic_text": dynamic,
            "prayer": prayer_text
        }

    def update_preview(self):
        data = self.build_data()

        os.makedirs("temp", exist_ok=True)
        temp_path = "temp/preview.pdf"

        generate_single_card_pdf(temp_path, data)
        self.preview.load_pdf(temp_path)

    def generate_a4(self):
        data = self.build_data()

        output_folder = get_output_folder()
        filename = generate_filename(data["name"])
        output_path = output_folder / filename

        config = load_config()

        generate_a4_sheet_pdf(
            str(output_path),
            data,
            show_card_border=config["show_card_border"]
        )

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(output_path)))

def generate_filename(name):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    safe_name = name.replace(" ", "_")
    return f"{timestamp}_{safe_name}.pdf"

def load_config():
    default_config = {
        "output_folder": "Documents/GeneratorKart",
        "show_card_border": False
    }

    config_path = Path("config.json")

    if not config_path.exists():
        return default_config

    with open(config_path, "r", encoding="utf-8") as f:
        user_config = json.load(f)

    default_config.update(user_config)
    return default_config

def get_output_folder():
    config = load_config()
    base_path = Path.home() / config["output_folder"]
    base_path.mkdir(parents=True, exist_ok=True)

    return base_path

def open_output_folder():
    folder = get_output_folder()
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))
