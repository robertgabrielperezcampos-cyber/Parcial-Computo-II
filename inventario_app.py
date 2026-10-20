import sys
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit, QMessageBox
)


class InventarioApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Consultoria de Inventario")
        self.resize(1050, 720)

        try:
            self.df = pd.read_csv("datos.csv")
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "No se encontro el archivo datos.csv")
            sys.exit(1)

        self.iniciar_interfaz()
        self.mostrar_inspeccion()
        self.actualizar_grafico()

    def iniciar_interfaz(self):
        titulo = QLabel("ANALISIS DEL INVENTARIO POR SUCURSAL")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #17365D;")

        self.combo_sucursal = QComboBox()
        self.combo_sucursal.addItem("Todas las sucursales")
        self.combo_sucursal.addItems(sorted(self.df["Sucursal"].unique()))

        self.combo_grafico = QComboBox()
        self.combo_grafico.addItems([
            "Stock por sucursal",
            "Valor de inventario por sucursal",
            "Unidades vendidas por categoria",
            "Productos con menor stock"
        ])

        boton_actualizar = QPushButton("Actualizar grafico")
        boton_actualizar.clicked.connect(self.actualizar_grafico)

        boton_inspeccion = QPushButton("Mostrar inspeccion")
        boton_inspeccion.clicked.connect(self.mostrar_inspeccion)

        controles = QGridLayout()
        controles.addWidget(QLabel("Sucursal:"), 0, 0)
        controles.addWidget(self.combo_sucursal, 0, 1)
        controles.addWidget(QLabel("Grafico:"), 0, 2)
        controles.addWidget(self.combo_grafico, 0, 3)
        controles.addWidget(boton_actualizar, 0, 4)
        controles.addWidget(boton_inspeccion, 0, 5)

        self.figura, self.ax = plt.subplots(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figura)

        self.resumen = QTextEdit()
        self.resumen.setReadOnly(True)
        self.resumen.setMaximumHeight(190)

        layout = QVBoxLayout()
        layout.addWidget(titulo)
        layout.addLayout(controles)
        layout.addWidget(self.canvas)
        layout.addWidget(QLabel("Inspeccion y resumen de datos:"))
        layout.addWidget(self.resumen)
        self.setLayout(layout)

        self.combo_sucursal.currentIndexChanged.connect(self.actualizar_grafico)
        self.combo_grafico.currentIndexChanged.connect(self.actualizar_grafico)

    def datos_filtrados(self):
        sucursal = self.combo_sucursal.currentText()
        if sucursal == "Todas las sucursales":
            return self.df
        return self.df[self.df["Sucursal"] == sucursal]

    def mostrar_inspeccion(self):
        df = self.datos_filtrados()
        texto = "PRIMERAS CINCO FILAS:\n"
        texto += df.head().to_string(index=False)
        texto += "\n\nTIPOS DE DATOS:\n"
        texto += df.dtypes.to_string()
        texto += "\n\nESTADISTICAS BASICAS:\n"
        texto += df[["Stock", "Precio_Unitario", "Unidades_Vendidas", "Valor_Inventario"]].describe().round(2).to_string()
        texto += f"\n\nFilas: {df.shape[0]} | Columnas: {df.shape[1]}"
        self.resumen.setPlainText(texto)

    def actualizar_grafico(self):
        df = self.datos_filtrados()
        opcion = self.combo_grafico.currentText()
        self.ax.clear()

        if opcion == "Stock por sucursal":
            datos = df.groupby("Sucursal")["Stock"].sum().sort_values(ascending=False)
            barras = self.ax.bar(datos.index, datos.values, color="tab:blue")
            self.ax.bar_label(barras, fmt="%.0f")
            self.ax.set_ylabel("Unidades en existencia")

        elif opcion == "Valor de inventario por sucursal":
            datos = df.groupby("Sucursal")["Valor_Inventario"].sum().sort_values(ascending=False)
            barras = self.ax.bar(datos.index, datos.values, color="tab:green")
            self.ax.bar_label(barras, fmt="$%.0f")
            self.ax.set_ylabel("Valor en dolares")

        elif opcion == "Unidades vendidas por categoria":
            datos = df.groupby("Categoria")["Unidades_Vendidas"].sum().sort_values(ascending=False)
            self.ax.pie(datos.values, labels=datos.index, autopct="%1.1f%%", startangle=90)
            self.ax.axis("equal")

        else:
            datos = df.nsmallest(10, "Stock")
            etiquetas = datos["Producto"] + " - " + datos["Sucursal"]
            barras = self.ax.barh(etiquetas, datos["Stock"], color="tab:red")
            self.ax.bar_label(barras, fmt="%.0f")
            self.ax.set_xlabel("Unidades en existencia")

        self.ax.set_title(opcion)
        self.ax.tick_params(axis="x", rotation=20)
        self.figura.tight_layout()
        self.canvas.draw()
        self.mostrar_inspeccion()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = InventarioApp()
    ventana.show()
    sys.exit(app.exec_())
