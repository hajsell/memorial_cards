from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView


class PdfPreviewWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.pdf_document = QPdfDocument(self)
        self.pdf_view = QPdfView(self)

        self.pdf_view.setDocument(self.pdf_document)

        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitInView)

        self.pdf_view.setMaximumWidth(400)
        self.pdf_view.setMinimumWidth(400)

        self.pdf_view.setMinimumHeight(680)
        self.pdf_view.setMaximumHeight(680)

        self.layout.addWidget(self.pdf_view)

    def load_pdf(self, path):
        self.pdf_document.load(path)