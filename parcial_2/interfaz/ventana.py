from __future__ import annotations

import threading
import time
import tkinter as tk
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from tkinter import ttk
from typing import Any

from detectores import detectar_final
from generador import generar_transacciones
from medicion import ResultadoMedicion, ejecutar_comparacion, guardar_csv
from modelos import Alerta


COLOR_FONDO = "#f2f5f7"
COLOR_PANEL = "#ffffff"
COLOR_TEXTO = "#17202a"
COLOR_SECUNDARIO = "#657383"
COLOR_BORDE = "#d4dce3"
COLOR_CABECERA = "#17324d"
COLOR_PRINCIPAL = "#0f766e"
CARPETA_RESULTADOS = Path(__file__).parent.parent / "resultados"


class VentanaDetector:
    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        self.raiz.title("Detector de transacciones sospechosas")
        self.raiz.geometry("1180x720")
        self.raiz.minsize(850, 600)
        self.raiz.configure(background=COLOR_FONDO)

        self.cantidad = tk.IntVar(value=5000)
        self.trabajadores = tk.IntVar(value=2)
        self.total_transacciones = tk.StringVar(value="0")
        self.total_alertas = tk.StringVar(value="0")
        self.tiempo = tk.StringVar(value="0,000 s")
        self.estrategia = tk.StringVar(value="-")
        self.estado = tk.StringVar(value="Listo para analizar")
        self.datos_alertas: list[tuple[str, float, str]] = []
        self.datos_rendimiento: list[tuple[str, float, str]] = []

        self._configurar_estilos()
        self._crear_interfaz()
        self.raiz.after(250, self.analizar)

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("TFrame", background=COLOR_FONDO)
        estilo.configure(
            "TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO, font=("Arial", 11)
        )
        estilo.configure(
            "TButton",
            padding=(14, 8),
            font=("Arial", 11, "bold"),
            foreground=COLOR_CABECERA,
            background=COLOR_PANEL,
            bordercolor="#9eabb7",
        )
        estilo.map("TButton", background=[("active", "#e8eef2")])
        estilo.configure(
            "Principal.TButton",
            foreground="white",
            background=COLOR_PRINCIPAL,
            bordercolor=COLOR_PRINCIPAL,
        )
        estilo.map(
            "Principal.TButton",
            background=[("active", "#0b625b"), ("disabled", "#8db9b4")],
        )
        estilo.configure("TNotebook", background=COLOR_FONDO, borderwidth=0)
        estilo.configure(
            "TNotebook.Tab", padding=(18, 9), font=("Arial", 11, "bold")
        )
        estilo.map(
            "TNotebook.Tab",
            foreground=[("selected", COLOR_PRINCIPAL)],
            background=[("selected", COLOR_PANEL)],
        )
        estilo.configure(
            "Treeview",
            background=COLOR_PANEL,
            fieldbackground=COLOR_PANEL,
            foreground=COLOR_TEXTO,
            rowheight=30,
            borderwidth=0,
            font=("Arial", 10),
        )
        estilo.configure(
            "Treeview.Heading",
            background="#e9eef2",
            foreground="#4d5965",
            padding=(8, 7),
            font=("Arial", 9, "bold"),
        )
        estilo.map("Treeview", background=[("selected", "#d7ebe8")])

    def _crear_interfaz(self) -> None:
        self._crear_cabecera()

        contenido = ttk.Frame(self.raiz, padding=(24, 18, 24, 12))
        contenido.pack(fill=tk.BOTH, expand=True)
        self._crear_controles(contenido)
        self._crear_metricas(contenido)
        self._crear_pestanas(contenido)

        estado = tk.Label(
            self.raiz,
            textvariable=self.estado,
            anchor="w",
            padx=24,
            pady=8,
            background=COLOR_PANEL,
            foreground=COLOR_SECUNDARIO,
            font=("Arial", 10),
            relief=tk.SOLID,
            borderwidth=1,
        )
        estado.pack(fill=tk.X, side=tk.BOTTOM)

    def _crear_cabecera(self) -> None:
        cabecera = tk.Frame(self.raiz, background=COLOR_CABECERA, padx=26, pady=15)
        cabecera.pack(fill=tk.X)

        marca = tk.Label(
            cabecera,
            text="PE",
            width=3,
            height=2,
            background="white",
            foreground=COLOR_CABECERA,
            font=("Arial", 12, "bold"),
        )
        marca.pack(side=tk.LEFT, padx=(0, 14))

        textos = tk.Frame(cabecera, background=COLOR_CABECERA)
        textos.pack(side=tk.LEFT)
        tk.Label(
            textos,
            text="Detector de transacciones sospechosas",
            background=COLOR_CABECERA,
            foreground="white",
            font=("Arial", 17, "bold"),
        ).pack(anchor="w")
        tk.Label(
            textos,
            text="Programacion Eficiente · Parcial 1",
            background=COLOR_CABECERA,
            foreground="#c8d8e6",
            font=("Arial", 10),
        ).pack(anchor="w", pady=(2, 0))

    def _crear_controles(self, padre: ttk.Frame) -> None:
        controles = ttk.Frame(padre)
        controles.pack(fill=tk.X, pady=(0, 16))

        self._crear_campo(controles, "Transacciones", self.cantidad, 0)
        self._crear_campo(controles, "Procesos (comparacion)", self.trabajadores, 1)
        controles.columnconfigure(2, weight=1)

        acciones = ttk.Frame(controles)
        acciones.grid(row=0, column=4, sticky="se")
        self.boton_analizar = ttk.Button(
            acciones,
            text="Analizar",
            style="Principal.TButton",
            command=self.analizar,
        )
        self.boton_analizar.pack(side=tk.LEFT, padx=(0, 8))
        self.boton_comparar = ttk.Button(
            acciones, text="Comparar versiones", command=self.comparar
        )
        self.boton_comparar.pack(side=tk.LEFT)

    def _crear_campo(
        self, padre: ttk.Frame, titulo: str, variable: tk.IntVar, columna: int
    ) -> None:
        grupo = ttk.Frame(padre)
        grupo.grid(row=0, column=columna, sticky="w", padx=(0, 14))
        ttk.Label(grupo, text=titulo, foreground=COLOR_SECUNDARIO).pack(anchor="w")
        ttk.Spinbox(
            grupo,
            from_=1,
            to=100_000,
            textvariable=variable,
            width=13,
            font=("Arial", 11),
        ).pack(anchor="w", pady=(4, 0))

    def _crear_metricas(self, padre: ttk.Frame) -> None:
        borde = tk.Frame(padre, background=COLOR_BORDE, padx=1, pady=1)
        borde.pack(fill=tk.X, pady=(0, 16))
        metricas = tk.Frame(borde, background=COLOR_PANEL)
        metricas.pack(fill=tk.X)

        datos = [
            ("Transacciones", self.total_transacciones),
            ("Alertas", self.total_alertas),
            ("Tiempo", self.tiempo),
            ("Estrategia", self.estrategia),
        ]
        for columna, (titulo, variable) in enumerate(datos):
            panel = tk.Frame(metricas, background=COLOR_PANEL, padx=18, pady=12)
            panel.grid(row=0, column=columna, sticky="nsew")
            if columna:
                tk.Frame(panel, width=1, background="#e2e7eb").pack(
                    side=tk.LEFT, fill=tk.Y, padx=(0, 16)
                )
            tk.Label(
                panel,
                text=titulo,
                background=COLOR_PANEL,
                foreground=COLOR_SECUNDARIO,
                font=("Arial", 9),
            ).pack(anchor="w")
            tk.Label(
                panel,
                textvariable=variable,
                background=COLOR_PANEL,
                foreground=COLOR_TEXTO,
                font=("Arial", 16, "bold"),
            ).pack(anchor="w", pady=(3, 0))
            metricas.columnconfigure(columna, weight=1)

    def _crear_pestanas(self, padre: ttk.Frame) -> None:
        self.pestanas = ttk.Notebook(padre)
        self.pestanas.pack(fill=tk.BOTH, expand=True)

        pestaña_alertas = ttk.Frame(self.pestanas, padding=10)
        pestaña_rendimiento = ttk.Frame(self.pestanas, padding=10)
        self.pestanas.add(pestaña_alertas, text="Alertas")
        self.pestanas.add(pestaña_rendimiento, text="Rendimiento")

        self.tabla_alertas = self._crear_tabla(
            pestaña_alertas,
            (
                ("transaccion", "Transaccion", 95),
                ("usuario", "Usuario", 110),
                ("tipo", "Tipo", 180),
                ("detalle", "Detalle", 360),
            ),
        )
        self.grafico_alertas = self._crear_grafico(pestaña_alertas)
        self.grafico_alertas.bind(
            "<Configure>", lambda _: self._dibujar_alertas()
        )

        self.tabla_rendimiento = self._crear_tabla(
            pestaña_rendimiento,
            (
                ("version", "Version", 170),
                ("tiempo", "Tiempo", 90),
                ("memoria", "Memoria", 90),
                ("alertas", "Alertas", 70),
                ("observacion", "Observacion", 330),
            ),
        )
        self.grafico_rendimiento = self._crear_grafico(pestaña_rendimiento)
        self.grafico_rendimiento.bind(
            "<Configure>", lambda _: self._dibujar_rendimiento()
        )

    def _crear_tabla(
        self, padre: ttk.Frame, columnas: tuple[tuple[str, str, int], ...]
    ) -> ttk.Treeview:
        contenedor = tk.Frame(padre, background=COLOR_BORDE, padx=1, pady=1)
        contenedor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        nombres = tuple(columna[0] for columna in columnas)
        tabla = ttk.Treeview(contenedor, columns=nombres, show="headings")
        for nombre, titulo, ancho in columnas:
            tabla.heading(nombre, text=titulo)
            tabla.column(nombre, width=ancho, minwidth=70, stretch=True)

        scroll_y = ttk.Scrollbar(contenedor, orient=tk.VERTICAL, command=tabla.yview)
        scroll_x = ttk.Scrollbar(contenedor, orient=tk.HORIZONTAL, command=tabla.xview)
        tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        tabla.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        contenedor.rowconfigure(0, weight=1)
        contenedor.columnconfigure(0, weight=1)
        return tabla

    def _crear_grafico(self, padre: ttk.Frame) -> tk.Canvas:
        grafico = tk.Canvas(
            padre,
            width=340,
            background=COLOR_PANEL,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1,
        )
        grafico.pack(side=tk.RIGHT, fill=tk.BOTH)
        return grafico

    def _leer_parametros(self, limite: int) -> tuple[int, int] | None:
        try:
            cantidad = self.cantidad.get()
            trabajadores = self.trabajadores.get()
        except tk.TclError:
            self._mostrar_error("Los parametros deben ser numeros enteros")
            return None

        if not 100 <= cantidad <= limite:
            self._mostrar_error(f"La cantidad debe estar entre 100 y {limite:,}")
            return None
        if not 1 <= trabajadores <= 8:
            self._mostrar_error("Los procesos deben estar entre 1 y 8")
            return None
        return cantidad, trabajadores

    def analizar(self) -> None:
        parametros = self._leer_parametros(100_000)
        if parametros is None:
            return
        cantidad, trabajadores = parametros

        def tarea() -> tuple[int, list[Alerta], str, float]:
            transacciones = generar_transacciones(cantidad, semilla=42)
            inicio = time.perf_counter()
            alertas, estrategia = detectar_final(transacciones, trabajadores)
            return len(transacciones), alertas, estrategia, time.perf_counter() - inicio

        self._ejecutar(
            "Analizando transacciones...", tarea, self._mostrar_analisis
        )

    def comparar(self) -> None:
        parametros = self._leer_parametros(10_000)
        if parametros is None:
            return
        cantidad, trabajadores = parametros

        def tarea() -> list[ResultadoMedicion]:
            resultados = ejecutar_comparacion(cantidad, trabajadores, semilla=42)
            guardar_csv(resultados, CARPETA_RESULTADOS / "comparacion.csv")
            return resultados

        self._ejecutar(
            "Midiendo las cinco versiones...", tarea, self._mostrar_comparacion
        )

    def _ejecutar(
        self,
        mensaje: str,
        tarea: Callable[[], Any],
        completar: Callable[[Any], None],
    ) -> None:
        self._bloquear(True)
        self.estado.set(mensaje)

        def trabajo() -> None:
            try:
                resultado = tarea()
            except Exception as error:
                self.raiz.after(0, lambda texto=str(error): self._mostrar_error(texto))
            else:
                self.raiz.after(0, lambda: completar(resultado))

        threading.Thread(target=trabajo, daemon=True).start()

    def _mostrar_analisis(
        self, resultado: tuple[int, list[Alerta], str, float]
    ) -> None:
        cantidad, alertas, estrategia, tiempo = resultado
        self.total_transacciones.set(f"{cantidad:,}".replace(",", "."))
        self.total_alertas.set(str(len(alertas)))
        self.tiempo.set(f"{tiempo:.4f} s")
        self.estrategia.set(estrategia)

        self._limpiar_tabla(self.tabla_alertas)
        for alerta in alertas:
            self.tabla_alertas.insert(
                "",
                tk.END,
                values=(
                    alerta.transaccion_id,
                    alerta.usuario,
                    alerta.tipo.replace("_", " "),
                    alerta.detalle,
                ),
            )

        resumen = Counter(alerta.tipo for alerta in alertas)
        self.datos_alertas = [
            (tipo.replace("_", " "), float(total), str(total))
            for tipo, total in resumen.items()
        ]
        self._dibujar_alertas()
        self.pestanas.select(0)
        self.estado.set(f"Analisis completado: {len(alertas)} alertas detectadas")
        self._bloquear(False)

    def _mostrar_comparacion(self, resultados: list[ResultadoMedicion]) -> None:
        self._limpiar_tabla(self.tabla_rendimiento)
        for resultado in resultados:
            self.tabla_rendimiento.insert(
                "",
                tk.END,
                values=(
                    resultado.version,
                    f"{resultado.tiempo_segundos:.4f} s",
                    f"{resultado.memoria_mb:.2f} MB",
                    resultado.cantidad_alertas,
                    resultado.observacion,
                ),
            )

        self.datos_rendimiento = [
            (
                resultado.version,
                resultado.tiempo_segundos,
                f"{resultado.tiempo_segundos:.4f} s",
            )
            for resultado in resultados
        ]
        self._dibujar_rendimiento()
        self.pestanas.select(1)
        self.estado.set(
            "Comparacion completada y guardada en resultados/comparacion.csv"
        )
        self._bloquear(False)

    def _dibujar_alertas(self) -> None:
        self._dibujar_barras(self.grafico_alertas, "Alertas por tipo", self.datos_alertas)

    def _dibujar_rendimiento(self) -> None:
        self._dibujar_barras(
            self.grafico_rendimiento,
            "Tiempo por version",
            self.datos_rendimiento,
        )

    def _dibujar_barras(
        self,
        canvas: tk.Canvas,
        titulo: str,
        datos: list[tuple[str, float, str]],
    ) -> None:
        canvas.delete("all")
        ancho = max(canvas.winfo_width(), 320)
        canvas.create_text(
            16,
            20,
            anchor="w",
            text=titulo,
            fill=COLOR_TEXTO,
            font=("Arial", 12, "bold"),
        )
        if not datos:
            canvas.create_text(
                ancho / 2,
                100,
                text="Sin datos",
                fill=COLOR_SECUNDARIO,
                font=("Arial", 10),
            )
            return

        maximo = max(valor for _, valor, _ in datos) or 1
        inicio_x = 135
        ancho_barra = max(ancho - inicio_x - 60, 50)
        alto_disponible = max(canvas.winfo_height() - 70, 180)
        paso = min(62, alto_disponible / len(datos))

        for indice, (nombre, valor, texto_valor) in enumerate(datos):
            y = 62 + indice * paso
            canvas.create_text(
                16,
                y,
                anchor="w",
                width=112,
                text=nombre,
                fill=COLOR_TEXTO,
                font=("Arial", 9),
            )
            canvas.create_rectangle(
                inicio_x,
                y - 7,
                inicio_x + ancho_barra,
                y + 7,
                fill="#e5eaee",
                outline="",
            )
            canvas.create_rectangle(
                inicio_x,
                y - 7,
                inicio_x + max(2, ancho_barra * valor / maximo),
                y + 7,
                fill=COLOR_PRINCIPAL,
                outline="",
            )
            canvas.create_text(
                ancho - 12,
                y,
                anchor="e",
                text=texto_valor,
                fill=COLOR_SECUNDARIO,
                font=("Arial", 9),
            )

    def _limpiar_tabla(self, tabla: ttk.Treeview) -> None:
        tabla.delete(*tabla.get_children())

    def _bloquear(self, bloqueado: bool) -> None:
        estado = tk.DISABLED if bloqueado else tk.NORMAL
        self.boton_analizar.configure(state=estado)
        self.boton_comparar.configure(state=estado)

    def _mostrar_error(self, mensaje: str) -> None:
        self.estado.set(f"Error: {mensaje}")
        self._bloquear(False)


def iniciar_interfaz() -> None:
    raiz = tk.Tk()
    VentanaDetector(raiz)
    raiz.mainloop()
