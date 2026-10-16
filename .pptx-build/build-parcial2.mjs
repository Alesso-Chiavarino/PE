import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const W = 1280;
const H = 720;
const FONT = "Helvetica Neue";
const C = {
  navy: "#00264F",
  ink: "#1D2B36",
  body: "#44515C",
  muted: "#70808D",
  blue: "#3D8DFF",
  blueSoft: "#EAF3FF",
  teal: "#20A98A",
  tealSoft: "#E8F7F3",
  coral: "#F67576",
  coralSoft: "#FFF0F0",
  yellow: "#FFCC5C",
  yellowSoft: "#FFF7DD",
  panel: "#F4F7F9",
  line: "#DDE4E9",
  white: "#FFFFFF",
  code: "#102332",
};

const workspaceDir = "/Users/alesso/dev/ubp/PE";
const skillDir = "/Users/alesso/.codex/plugins/cache/openai-primary-runtime/presentations/26.1013.11914/skills/presentations";
const runtimePython = "/Users/alesso/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";
const buildDir = path.join(workspaceDir, ".pptx-build", "parcial2-v1");
const candidatePath = path.join(buildDir, "Parcial-2-Mejoras-candidate.pptx");
const finalPath = path.join(workspaceDir, "parcial_2", "presentacion", "Parcial-2-Mejoras-Programacion-Eficiente.pptx");
const coverImage = path.join(workspaceDir, "parcial_2", "presentacion", "assets", "portada-transacciones.png");
const coverBytes = await fs.readFile(coverImage);

await fs.mkdir(buildDir, { recursive: true });
await fs.mkdir(path.dirname(finalPath), { recursive: true });

function shape(slide, geometry, x, y, w, h, fill = "none", lineFill = "none", radius) {
  return slide.shapes.add({
    geometry,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: lineFill, width: lineFill === "none" ? 0 : 1 },
    ...(radius ? { borderRadius: radius } : {}),
  });
}

function textBox(slide, text, x, y, w, h, options = {}) {
  const box = shape(slide, "textbox", x, y, w, h, options.fill ?? "none", options.line ?? "none");
  box.text = text;
  box.text.style = {
    typeface: options.typeface ?? FONT,
    fontSize: options.size ?? 24,
    bold: options.bold ?? false,
    color: options.color ?? C.body,
    alignment: options.align ?? "left",
    verticalAlignment: options.valign ?? "top",
    lineSpacing: options.lineSpacing ?? 1.08,
    insets: options.insets ?? 0,
    autoFit: options.autoFit ?? "none",
  };
  return box;
}

function richText(slide, paragraphs, x, y, w, h, options = {}) {
  const box = shape(slide, "textbox", x, y, w, h, options.fill ?? "none", options.line ?? "none");
  box.text.set(paragraphs);
  box.text.style = {
    typeface: options.typeface ?? FONT,
    fontSize: options.size ?? 22,
    color: options.color ?? C.body,
    verticalAlignment: options.valign ?? "top",
    lineSpacing: options.lineSpacing ?? 1.12,
    insets: options.insets ?? 0,
    autoFit: options.autoFit ?? "none",
  };
  return box;
}

function sectionTitle(slide, kicker, title, number) {
  textBox(slide, kicker.toUpperCase(), 68, 44, 650, 24, { size: 14, bold: true, color: C.blue });
  textBox(slide, title, 68, 77, 1080, 62, { size: 42, bold: true, color: C.navy, lineSpacing: 0.98 });
  shape(slide, "rect", 68, 151, 64, 5, C.coral);
}

function footer(slide, number, label = "Programación Eficiente · Parcial 2") {
  shape(slide, "rect", 68, 674, 1144, 1, C.line);
  textBox(slide, label, 68, 683, 500, 18, { size: 13, color: C.muted });
  textBox(slide, String(number).padStart(2, "0"), 1152, 683, 60, 18, { size: 13, bold: true, color: C.navy, align: "right" });
}

function pill(slide, label, x, y, w, fill, color) {
  shape(slide, "roundRect", x, y, w, 32, fill, "none", "rounded-xl");
  textBox(slide, label, x, y + 6, w, 20, { size: 14, bold: true, color, align: "center", valign: "middle" });
}

function card(slide, x, y, w, h, title, body, accent = C.blue, soft = C.blueSoft) {
  shape(slide, "roundRect", x, y, w, h, C.white, C.line, "rounded-xl");
  shape(slide, "roundRect", x + 20, y + 20, 42, 8, accent, "none", "rounded-xl");
  textBox(slide, title, x + 20, y + 44, w - 40, 38, { size: 23, bold: true, color: C.navy });
  textBox(slide, body, x + 20, y + 90, w - 40, h - 108, { size: 18, color: C.body, lineSpacing: 1.13 });
  shape(slide, "roundRect", x + w - 54, y + 18, 34, 34, soft, "none", "rounded-xl");
  shape(slide, "ellipse", x + w - 43, y + 29, 12, 12, accent);
}

function metric(slide, x, y, w, value, label, color = C.blue) {
  shape(slide, "roundRect", x, y, w, 112, C.panel, "none", "rounded-xl");
  textBox(slide, value, x + 18, y + 16, w - 36, 46, { size: 38, bold: true, color });
  textBox(slide, label, x + 18, y + 67, w - 36, 32, { size: 16, color: C.body });
}

function codeBox(slide, lines, x, y, w, h, label) {
  shape(slide, "roundRect", x, y, w, h, C.code, "none", "rounded-xl");
  if (label) pill(slide, label, x + 18, y + 16, 94, "#21415A", C.white);
  textBox(slide, lines.join("\n"), x + 22, y + (label ? 62 : 24), w - 44, h - (label ? 78 : 42), {
    size: 17,
    color: "#E7F0F7",
    typeface: FONT,
    lineSpacing: 1.22,
  });
}

function addNotes(slide, sourceLines, talkTrack) {
  slide.speakerNotes.text = [
    talkTrack,
    "",
    ...sourceLines.map((source) => `Fuente: ${source}`),
  ];
}

function arrow(slide, x, y, w = 46) {
  textBox(slide, "→", x, y, w, 42, { size: 33, bold: true, color: C.blue, align: "center", valign: "middle" });
}

const presentation = Presentation.create({ slideSize: { width: W, height: H } });

// 1 — Portada
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  slide.images.add({ blob: coverBytes, contentType: "image/png", alt: "Ilustración del detector de transacciones", fit: "cover", position: { left: 690, top: 0, width: 590, height: 720 } });
  shape(slide, "rect", 0, 0, 720, 720, C.white);
  pill(slide, "SEGUNDO PARCIAL", 70, 72, 176, C.blueSoft, C.blue);
  textBox(slide, "Mejoras sobre el\ndetector de transacciones", 70, 133, 585, 180, { size: 50, bold: true, color: C.navy, lineSpacing: 0.94 });
  textBox(slide, "Refactorización · archivos grandes · calidad · testing", 72, 337, 540, 66, { size: 24, color: C.body, lineSpacing: 1.15 });
  shape(slide, "rect", 72, 436, 72, 6, C.coral);
  textBox(slide, "Python · Proyecto parcial_2", 72, 465, 440, 30, { size: 18, bold: true, color: C.navy });
  textBox(slide, "La misma funcionalidad, con una arquitectura más mantenible y preparada para mayor volumen.", 72, 518, 520, 86, { size: 20, color: C.muted, lineSpacing: 1.14 });
  textBox(slide, "Programación Eficiente", 72, 666, 360, 20, { size: 14, color: C.muted });
  addNotes(slide, [
    "Proyecto local parcial_2.",
    "Material de clase Programacion-eficiente.pptx.",
  ], "Presentar el trabajo como una evolución del primer parcial: se mantiene el dominio y se mejora la ingeniería del código.");
}

// 2 — Punto de partida
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  sectionTitle(slide, "Punto de partida", "Del parcial 1 al parcial 2", 2);
  card(slide, 68, 190, 350, 214, "Parcial 1", "Comparó cinco estrategias, midió tiempos y memoria, y justificó estructuras como dict, deque, set y cache LRU.", C.muted, C.panel);
  arrow(slide, 429, 270, 56);
  card(slide, 494, 190, 350, 214, "Problema nuevo", "El programa funcionaba, pero necesitaba menos duplicación, procesamiento de archivos grandes y controles automáticos de calidad.", C.coral, C.coralSoft);
  arrow(slide, 855, 270, 56);
  card(slide, 920, 190, 292, 214, "Parcial 2", "La lógica pasa a módulos reutilizables, se procesa por streaming y el comportamiento queda protegido por pruebas.", C.teal, C.tealSoft);
  metric(slide, 68, 445, 244, "15", "pruebas automatizadas", C.teal);
  metric(slide, 330, 445, 244, "94%", "cobertura del núcleo", C.blue);
  metric(slide, 592, 445, 244, "1 MB", "buffer de E/S", C.coral);
  metric(slide, 854, 445, 358, "--transacciones", "volumen configurable desde CLI", C.navy);
  addNotes(slide, [
    "parcial_2/README.md.",
    "Resultados verificados localmente con pytest y pytest-cov.",
  ], "Aclarar que el objetivo no fue reescribir todo: se conservó lo que funcionaba y se atacaron límites concretos del primer parcial.");
}

// 3 — Concepto de refactorización
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  sectionTitle(slide, "Etapa 1", "Refactorizar sin cambiar el comportamiento", 3);
  shape(slide, "roundRect", 68, 190, 1144, 112, C.navy, "none", "rounded-xl");
  textBox(slide, "Refactorización", 96, 217, 255, 38, { size: 27, bold: true, color: C.white });
  textBox(slide, "Reorganizar la estructura interna del código sin modificar su funcionalidad observable.", 365, 210, 806, 62, { size: 26, color: C.white, lineSpacing: 1.05 });
  card(slide, 68, 336, 350, 258, "1. Detectar", "Código repetido, funciones extensas, constantes dispersas y responsabilidades mezcladas.", C.coral, C.coralSoft);
  card(slide, 465, 336, 350, 258, "2. Transformar", "Extraer métodos y clases, mover responsabilidades y centralizar configuración.", C.blue, C.blueSoft);
  card(slide, 862, 336, 350, 258, "3. Verificar", "Correr pruebas de regresión para comprobar que las alertas continúan siendo las mismas.", C.teal, C.tealSoft);
  addNotes(slide, [
    "Material de clase, diapositivas 243–245: reestructurar sin cambiar funcionalidad, simplificar y eliminar duplicación.",
    "Material de clase, diapositivas 253–254: Long Method y Extract Method.",
  ], "Usar esta diapositiva para definir el concepto antes de mostrar los cambios del proyecto.");
}

// 4 — Tipos aplicados
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  sectionTitle(slide, "Refactorizaciones aplicadas", "Cuatro cambios concretos en el proyecto", 4);
  card(slide, 68, 184, 536, 196, "Extract Class", "EstadoDeteccionUsuario encapsula colas, contadores y alertas emitidas. La detección deja de depender de una lista completa.", C.blue, C.blueSoft);
  card(slide, 628, 184, 584, 196, "Extract Method", "_agregar_datos_generados concentra argumentos comunes; _guardar_filas_csv y _cargar_pyplot eliminan lógica repetida.", C.teal, C.tealSoft);
  card(slide, 68, 406, 536, 196, "Encapsulate Configuration", "ConfiguracionDeteccion reúne ventanas, mínimos y límites en un dataclass inmutable y fácil de reemplazar en pruebas.", C.coral, C.coralSoft);
  card(slide, 628, 406, 584, 196, "Remove Duplication", "La escritura CSV y la configuración de gráficos tienen un único punto de mantenimiento: se aplica DRY.", C.yellow, C.yellowSoft);
  addNotes(slide, [
    "parcial_2/CAMBIOS_PARCIAL_2.md.",
    "parcial_2/detectores.py y parcial_2/configuracion.py.",
    "Material de clase, diapositivas 246–247: Rename, Extract Method/Variable/Constant, Move e Inline.",
  ], "Nombrar los patrones en inglés porque son los nombres habituales de catálogo y vincular cada uno con un archivo real.");
}

// 5 — Arquitectura
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  sectionTitle(slide, "Arquitectura", "La lógica ahora está separada por responsabilidad", 5);
  pill(slide, "ENTRADA", 75, 190, 112, C.blueSoft, C.blue);
  pill(slide, "DOMINIO", 447, 190, 124, C.tealSoft, C.teal);
  pill(slide, "SALIDA", 987, 190, 112, C.coralSoft, C.coral);
  card(slide, 68, 242, 290, 122, "main.py", "CLI y coordinación", C.blue, C.blueSoft);
  arrow(slide, 368, 280, 56);
  card(slide, 434, 242, 330, 122, "generador.py", "Transacciones con yield", C.teal, C.tealSoft);
  arrow(slide, 774, 280, 56);
  card(slide, 840, 242, 372, 122, "archivos.py", "CSV, buffer y batching", C.coral, C.coralSoft);
  shape(slide, "rect", 590, 386, 3, 44, C.line);
  card(slide, 312, 430, 390, 128, "detectores.py", "Estado por usuario + reglas", C.navy, C.blueSoft);
  card(slide, 722, 430, 490, 128, "configuracion.py", "Umbrales centralizados e inmutables", C.yellow, C.yellowSoft);
  textBox(slide, "Capas transversales", 68, 585, 190, 24, { size: 16, bold: true, color: C.muted });
  pill(slide, "pytest", 276, 579, 108, C.tealSoft, C.teal);
  pill(slide, "flake8", 400, 579, 108, C.blueSoft, C.blue);
  pill(slide, "Sphinx", 524, 579, 108, C.yellowSoft, C.navy);
  pill(slide, "psutil", 648, 579, 108, C.coralSoft, C.coral);
  addNotes(slide, [
    "parcial_2/main.py, generador.py, archivos.py, detectores.py y configuracion.py.",
  ], "Explicar el recorrido de izquierda a derecha y remarcar que cada módulo tiene una responsabilidad clara.");
}

// 6 — Antes y después
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  sectionTitle(slide, "Código redundante", "Antes y después: menos repetición, más intención", 6);
  textBox(slide, "ANTES", 68, 185, 150, 26, { size: 16, bold: true, color: C.coral });
  textBox(slide, "DESPUÉS", 660, 185, 150, 26, { size: 16, bold: true, color: C.teal });
  codeBox(slide, [
    "demo.add_argument(--transacciones)",
    "benchmark.add_argument(--transacciones)",
    "perfilado.add_argument(--transacciones)",
    "# misma definición en cada comando",
  ], 68, 222, 526, 204);
  codeBox(slide, [
    "def _agregar_datos_generados(parser):",
    "    parser.add_argument(--transacciones)",
    "    parser.add_argument(--semilla)",
    "# una sola fuente de verdad",
  ], 660, 222, 552, 204);
  shape(slide, "roundRect", 68, 458, 1144, 124, C.panel, "none", "rounded-xl");
  richText(slide, [
    [{ run: "Resultado: ", style: { bold: true, color: C.navy } }, "si cambia un argumento, un formato CSV o la configuración de Matplotlib, se modifica un solo lugar."],
    [{ run: "Impacto: ", style: { bold: true, color: C.navy } }, "menos inconsistencias y menor costo de mantenimiento; la interfaz pública se conserva."],
  ], 92, 481, 1096, 78, { size: 21, lineSpacing: 1.2 });
  addNotes(slide, [
    "parcial_2/main.py: _agregar_datos_generados.",
    "parcial_2/CAMBIOS_PARCIAL_2.md.",
  ], "Este es el ejemplo más fácil de defender: tres bloques repetidos pasan a una función compartida.");
}

// 7 — SnakeViz
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  sectionTitle(slide, "Optimización", "cProfile + SnakeViz: encontrar dónde se va el tiempo", 7);
  card(slide, 68, 196, 250, 180, "1. Medir", "cProfile ejecuta la versión inicial y la optimizada.", C.navy, C.blueSoft);
  arrow(slide, 326, 262, 42);
  card(slide, 376, 196, 250, 180, "2. Guardar", "El proyecto genera archivos .prof reproducibles.", C.blue, C.blueSoft);
  arrow(slide, 634, 262, 42);
  card(slide, 684, 196, 250, 180, "3. Visualizar", "SnakeViz convierte el perfil en vistas interactivas.", C.teal, C.tealSoft);
  arrow(slide, 942, 262, 42);
  card(slide, 992, 196, 220, 180, "4. Decidir", "Se prioriza el cuello de botella real.", C.coral, C.coralSoft);
  codeBox(slide, [
    "python main.py perfilado --transacciones 5000",
    "python -m snakeviz resultados/perfilado_optimizado.prof",
  ], 68, 422, 700, 128, "COMANDOS");
  shape(slide, "roundRect", 792, 422, 420, 128, C.yellowSoft, "none", "rounded-xl");
  textBox(slide, "¿Por qué SnakeViz?", 816, 444, 370, 30, { size: 22, bold: true, color: C.navy });
  textBox(slide, "Aprovecha los .prof existentes, es visual y requiere menos configuración que incorporar un profiler nuevo.", 816, 482, 370, 52, { size: 18, color: C.body, lineSpacing: 1.12 });
  addNotes(slide, [
    "parcial_2/perfilado.py y parcial_2/README.md.",
    "Material de clase, diapositiva 178: SnakeViz visualiza perfiles de cProfile; diapositiva 291: cProfile + SnakeViz.",
  ], "Aclarar que SnakeViz no optimiza automáticamente: muestra evidencia para decidir qué optimizar.");
}

// 8 — psutil
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  sectionTitle(slide, "Herramienta general", "psutil: observabilidad simple para un proceso local", 8);
  shape(slide, "roundRect", 68, 188, 466, 390, C.navy, "none", "rounded-xl");
  textBox(slide, "medir_recursos()", 100, 220, 400, 38, { size: 28, bold: true, color: C.white });
  metric(slide, 100, 286, 190, "RSS", "memoria máxima", C.blue);
  metric(slide, 310, 286, 190, "CPU", "segundos usados", C.teal);
  metric(slide, 100, 420, 190, "I/O", "bytes leídos", C.coral);
  metric(slide, 310, 420, 190, "I/O", "bytes escritos", C.yellow);
  textBox(slide, "Por qué no New Relic o Elastic APM", 580, 195, 580, 40, { size: 27, bold: true, color: C.navy });
  richText(slide, [
    { bulletCharacter: "•", marginLeft: 24, indent: -12, runs: ["El proyecto es una aplicación CLI/batch local, no un servicio desplegado."] },
    { bulletCharacter: "•", marginLeft: 24, indent: -12, runs: ["psutil mide exactamente los recursos solicitados sin servidor, agente ni cuenta externa."] },
    { bulletCharacter: "•", marginLeft: 24, indent: -12, runs: ["La medición queda integrada en analizar-archivo y se imprime al finalizar."] },
    { bulletCharacter: "•", marginLeft: 24, indent: -12, runs: ["Trade-off: no ofrece trazas distribuidas ni paneles históricos."] },
  ], 580, 258, 600, 238, { size: 22, lineSpacing: 1.15 });
  pill(slide, "Elección proporcional al alcance", 580, 522, 306, C.tealSoft, C.teal);
  addNotes(slide, [
    "parcial_2/monitoreo.py y parcial_2/main.py.",
    "Material de clase, diapositivas 182, 184 y 185: YourKit, New Relic y Elastic APM.",
  ], "Defender psutil como la alternativa permitida por el enunciado. Es adecuada para observar un proceso local y evita infraestructura innecesaria.");
}

// 9 — archivos grandes
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  sectionTitle(slide, "Archivos grandes", "Dos pasadas, memoria acotada y estado correcto", 9);
  card(slide, 68, 190, 250, 160, "CSV ordenado", "Entrada leída línea por línea.", C.blue, C.blueSoft);
  arrow(slide, 326, 247, 42);
  card(slide, 376, 190, 250, 160, "Pasada 1", "Promedio y varianza incremental por usuario.", C.teal, C.tealSoft);
  arrow(slide, 634, 247, 42);
  card(slide, 684, 190, 250, 160, "Pasada 2", "Reglas por lotes con ventanas persistentes.", C.coral, C.coralSoft);
  arrow(slide, 942, 247, 42);
  card(slide, 992, 190, 220, 160, "Alertas CSV", "Salida progresiva.", C.navy, C.blueSoft);
  shape(slide, "roundRect", 68, 391, 1144, 175, C.panel, "none", "rounded-xl");
  richText(slide, [
    [{ run: "La clave de corrección: ", style: { bold: true, color: C.navy } }, "EstadoDeteccionUsuario no se reinicia al cambiar de lote."],
    [{ run: "Consecuencia: ", style: { bold: true, color: C.navy } }, "una ráfaga que empieza al final de un lote y termina al inicio del siguiente sigue siendo detectada."],
    [{ run: "Memoria: ", style: { bold: true, color: C.navy } }, "no se carga el archivo completo; sólo se conservan perfiles, estados y el lote actual."],
  ], 96, 423, 1088, 112, { size: 22, lineSpacing: 1.16 });
  addNotes(slide, [
    "parcial_2/archivos.py: calcular_perfiles_csv e iterar_alertas_csv.",
    "Material de clase, diapositivas 187–209: E/S, buffers, batching y archivos grandes.",
  ], "Remarcar que batching por sí solo no alcanza: hay que conservar estado para no perder alertas en los límites.");
}

// 10 — buffer batching parallel
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  sectionTitle(slide, "E/S y concurrencia", "Buffer, batching y paralelismo", 10);
  card(slide, 68, 190, 350, 262, "Buffer · 1 MB", "Reduce llamadas pequeñas al sistema operativo durante lectura y escritura. Se aplica al abrir los CSV.", C.blue, C.blueSoft);
  card(slide, 465, 190, 350, 262, "Batching · 10.000", "Agrupa un número limitado de transacciones. El tamaño se puede cambiar con --lote.", C.teal, C.tealSoft);
  card(slide, 862, 190, 350, 262, "Paralelismo · por usuario", "ProcessPoolExecutor reparte grupos independientes. No se dividen ventanas temporales arbitrariamente.", C.coral, C.coralSoft);
  codeBox(slide, [
    "python main.py generar-archivo --transacciones 100000",
    "python main.py analizar-archivo datos/transacciones.csv --lote 10000",
  ], 68, 486, 1144, 116, "EJEMPLO");
  addNotes(slide, [
    "parcial_2/archivos.py: TAMANIO_BUFFER_PREDETERMINADO y agrupar_en_lotes.",
    "parcial_2/detectores.py: ProcessPoolExecutor por grupos de usuario.",
    "Material de clase, diapositivas 205–209: batching y procesamiento paralelo.",
  ], "Explicar que paralelizar no siempre acelera: la versión final conserva la estrategia secuencial optimizada porque el overhead de procesos fue mayor con estos volúmenes.");
}

// 11 — legibilidad
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  sectionTitle(slide, "Mantenibilidad", "Código que explica su intención", 11);
  card(slide, 68, 190, 350, 192, "Nombres descriptivos", "tamanio_lote, memoria_rss_maxima_mb y ventana_repeticion reemplazan abreviaturas ambiguas.", C.blue, C.blueSoft);
  card(slide, 465, 190, 350, 192, "Docstrings útiles", "Los módulos, clases y funciones públicas describen propósito, entradas, salida y restricciones relevantes.", C.teal, C.tealSoft);
  card(slide, 862, 190, 350, 192, "Organización", "CLI, dominio, archivos, monitoreo, pruebas y documentación viven en módulos separados.", C.coral, C.coralSoft);
  shape(slide, "roundRect", 68, 421, 1144, 151, C.navy, "none", "rounded-xl");
  textBox(slide, "PEP 8 como regla automática", 94, 446, 360, 32, { size: 25, bold: true, color: C.white });
  textBox(slide, "flake8 revisa formato, nombres, imports y errores frecuentes. Resultado actual: sin observaciones.", 94, 492, 720, 58, { size: 21, color: "#E4EDF4", lineSpacing: 1.12 });
  pill(slide, "python -m flake8 .", 896, 473, 270, "#21415A", C.white);
  addNotes(slide, [
    "parcial_2/*.py y parcial_2/.flake8.",
    "Material de clase, diapositiva 216: docstrings; diapositiva 235 y 420: flake8.",
  ], "Diferenciar comentarios de docstrings: el comentario explica decisiones no obvias; el docstring documenta la interfaz de un módulo, clase o función.");
}

// 12 — Sphinx
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  sectionTitle(slide, "Documentación", "Sphinx: documentación desde docstrings", 12);
  card(slide, 68, 198, 282, 170, "Código Python", "Docstrings junto a la implementación.", C.blue, C.blueSoft);
  arrow(slide, 360, 258, 42);
  card(slide, 412, 198, 282, 170, "Autodoc", "Importa firmas y descripciones.", C.teal, C.tealSoft);
  arrow(slide, 704, 258, 42);
  card(slide, 756, 198, 282, 170, "Sphinx", "Organiza guías y referencia API.", C.coral, C.coralSoft);
  arrow(slide, 1048, 258, 42);
  card(slide, 1100, 198, 112, 170, "HTML", "Sitio", C.navy, C.blueSoft);
  codeBox(slide, ["python -m sphinx -b html docs docs/_build/html"], 68, 410, 760, 112, "COMANDO");
  shape(slide, "roundRect", 856, 410, 356, 112, C.yellowSoft, "none", "rounded-xl");
  textBox(slide, "Contenido generado", 880, 430, 300, 28, { size: 21, bold: true, color: C.navy });
  textBox(slide, "Uso · API · refactorización", 880, 470, 300, 28, { size: 18, color: C.body });
  textBox(slide, "Ventaja: si cambia una firma o un docstring, la próxima compilación actualiza la referencia.", 68, 553, 1010, 42, { size: 20, color: C.muted });
  addNotes(slide, [
    "parcial_2/docs/index.rst, uso.rst, api.rst y refactorizacion.rst.",
    "Material de clase, diapositivas 240–241 y 331–338: Sphinx.",
  ], "Mostrar la cadena código-docstring-HTML. La documentación deja de ser un archivo aislado y se genera desde la fuente.");
}

// 13 — calidad
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  sectionTitle(slide, "Calidad", "flake8 como alternativa liviana a SonarQube", 13);
  shape(slide, "roundRect", 68, 191, 455, 370, C.panel, "none", "rounded-xl");
  textBox(slide, "SonarQube", 96, 220, 240, 34, { size: 28, bold: true, color: C.navy });
  richText(slide, [
    { bulletCharacter: "•", marginLeft: 24, indent: -12, runs: ["Panel central y métricas históricas"] },
    { bulletCharacter: "•", marginLeft: 24, indent: -12, runs: ["Bugs, vulnerabilidades y code smells"] },
    { bulletCharacter: "•", marginLeft: 24, indent: -12, runs: ["Muy útil en equipos y CI/CD"] },
    { bulletCharacter: "•", marginLeft: 24, indent: -12, runs: ["Requiere más infraestructura"] },
  ], 96, 279, 390, 210, { size: 21, lineSpacing: 1.16 });
  textBox(slide, "Referencia del enunciado", 96, 512, 280, 24, { size: 15, bold: true, color: C.muted });
  shape(slide, "roundRect", 553, 191, 659, 370, C.navy, "none", "rounded-xl");
  textBox(slide, "flake8", 584, 220, 240, 34, { size: 28, bold: true, color: C.white });
  richText(slide, [
    { bulletCharacter: "•", marginLeft: 24, indent: -12, runs: ["Chequeo local inmediato"] },
    { bulletCharacter: "•", marginLeft: 24, indent: -12, runs: ["PEP 8, errores sintácticos e imports"] },
    { bulletCharacter: "•", marginLeft: 24, indent: -12, runs: ["Sin servicio externo"] },
    { bulletCharacter: "•", marginLeft: 24, indent: -12, runs: ["Se integra con un solo comando"] },
  ], 584, 279, 590, 210, { size: 21, color: "#E4EDF4", lineSpacing: 1.16 });
  pill(slide, "0 observaciones", 584, 506, 190, C.teal, C.white);
  textBox(slide, "Criterio de elección: aplicar una herramienta simple y reproducible para el alcance del proyecto.", 68, 590, 1090, 38, { size: 20, color: C.body });
  addNotes(slide, [
    "parcial_2/.flake8 y verificación local python -m flake8 .",
    "Material de clase, diapositiva 242: capacidades de SonarQube; diapositivas 235 y 420: flake8.",
  ], "No afirmar que flake8 reemplaza todas las capacidades de SonarQube. Presentarlo como alternativa proporcionada para estilo y análisis estático básico.");
}

// 14 — pytest
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  sectionTitle(slide, "Testing y framework", "pytest protege la refactorización", 14);
  metric(slide, 68, 190, 238, "15", "tests aprobados", C.teal);
  metric(slide, 326, 190, 238, "94%", "cobertura del núcleo", C.blue);
  metric(slide, 584, 190, 238, "3", "módulos de pruebas", C.coral);
  metric(slide, 842, 190, 370, "pytest", "framework utilizado", C.navy);
  card(slide, 68, 336, 350, 216, "Unitarias", "Reglas del detector y acumuladores se prueban de forma aislada.", C.blue, C.blueSoft);
  card(slide, 465, 336, 350, 216, "Integración", "Generar, leer, procesar y escribir CSV se valida como flujo completo.", C.teal, C.tealSoft);
  card(slide, 862, 336, 350, 216, "Regresión", "La detección en streaming produce las mismas alertas que la versión en memoria.", C.coral, C.coralSoft);
  codeBox(slide, ["python -m pytest", "python -m pytest --cov=archivos --cov=configuracion --cov=detectores"], 68, 568, 1144, 86);
  addNotes(slide, [
    "parcial_2/tests/test_archivos.py, test_detectores.py y test_monitoreo.py.",
    "Resultados verificados localmente: 15 tests y 94% de cobertura del núcleo.",
    "Material de clase, diapositivas 272–275: tipos de testing y características de pytest.",
  ], "Responder explícitamente la duda: pytest sí cuenta como framework, específicamente un framework de testing para Python.");
}

// 15 — checklist
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  sectionTitle(slide, "Cierre", "Cada tema del enunciado quedó aplicado", 15);
  const rows = [
    ["Refactorización", "EstadoDeteccionUsuario · ConfiguracionDeteccion · DRY", C.blue],
    ["Optimización", "cProfile + SnakeViz", C.teal],
    ["Herramienta general", "psutil: CPU · RSS · E/S", C.coral],
    ["Archivos grandes", "yield · buffer 1 MB · batching · estado entre lotes", C.yellow],
    ["Mantenibilidad", "nombres · docstrings · módulos · PEP 8", C.blue],
    ["Documentación", "Sphinx + autodoc", C.teal],
    ["Calidad y testing", "flake8 · pytest · pytest-cov", C.coral],
  ];
  rows.forEach(([label, value, color], index) => {
    const y = 177 + index * 61;
    shape(slide, "roundRect", 68, y, 1144, 48, index % 2 === 0 ? C.panel : C.white, index % 2 === 0 ? "none" : C.line, "rounded-xl");
    shape(slide, "ellipse", 88, y + 15, 18, 18, color);
    textBox(slide, label, 124, y + 10, 270, 28, { size: 18, bold: true, color: C.navy, valign: "middle" });
    textBox(slide, value, 410, y + 10, 760, 28, { size: 18, color: C.body, valign: "middle" });
  });
  shape(slide, "roundRect", 68, 620, 1144, 38, C.navy, "none", "rounded-xl");
  textBox(slide, "Resultado: mismo detector, mejor preparado para cambiar, medir y escalar.", 88, 628, 1104, 22, { size: 19, bold: true, color: C.white, align: "center" });
  addNotes(slide, [
    "parcial_2/CAMBIOS_PARCIAL_2.md y parcial_2/README.md.",
  ], "Cerrar volviendo a la idea central: no se agregaron herramientas de forma decorativa; cada una resuelve un límite concreto del primer parcial.");
}

for (const [index, slide] of presentation.slides.items.entries()) {
  if (index > 0) footer(slide, index + 1);
  const png = await presentation.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(path.join(buildDir, `slide-${String(index + 1).padStart(2, "0")}.png`), new Uint8Array(await png.arrayBuffer()));
}

const montage = await presentation.export({ format: "webp", montage: true, scale: 0.35 });
await fs.writeFile(path.join(buildDir, "montage.webp"), new Uint8Array(await montage.arrayBuffer()));

await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

const { finalizePresentation } = await import(pathToFileURL(path.join(skillDir, "container_tools", "artifact_tool_utils.mjs")).href);
const requirements = {
  explicitTotalSlideCount: 15,
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [],
};
const fontPolicy = {
  basis: "reference",
  families: [FONT],
  referencePath: path.join(workspaceDir, "parcial_2", "presentacion", "Parcial-1-Programacion-Eficiente.pptx"),
  referenceSha256: "2f3ea18de2f4d833eb4d036435c55444da6b64764ef1dec2ff1fb3aee4c826ce",
};
const result = await finalizePresentation({
  ...requirements,
  workspaceDir,
  candidatePath,
  finalPath,
  pythonExecutable: runtimePython,
  integrityValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_layout_geometry.py"),
  layoutArgs: [
    "--expected-slide-size-emu", "12192000,6858000",
    "--validate-bullet-geometry",
    "--validate-heading-fit",
  ],
  requiredNativeTableOwnerSlides: [],
  fontPolicy,
  verifyArtifactToolImport: true,
  receiptPath: path.join(buildDir, "Parcial-2-Mejoras.validation.json"),
});

console.log(JSON.stringify({ slides: presentation.slides.items.length, candidatePath, finalPath, result }, null, 2));
