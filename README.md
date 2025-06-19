# ⚡ Zapdos 

**Optimización Inteligente de Consumo Energético Diario**

Una aplicación web desarrollada con Streamlit para optimizar el uso de equipos eléctricos, minimizando costos y maximizando el aprovechamiento de energía solar disponible.

## 🎯 Características

- 📊 **Análisis de datos horarios**: Procesa información de 24 horas de generación solar, tarifas y consumo base
- ⚡ **Optimización matemática**: Utiliza programación lineal (PuLP) para encontrar el plan óptimo
- 📈 **Reportes detallados**: Genera planes en Excel con formato profesional y códigos de colores
- 🎨 **Interfaz moderna**: UI intuitiva con métricas en tiempo real y visualización clara
- 💾 **Plantillas incluidas**: Archivos base para facilitar la entrada de datos
- 📸 **Ejemplos visuales**: Imágenes de referencia de facturas y curvas de potencia para guiar al usuario

## 🚀 Instalación y Uso

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación

1. **Clona o descarga el repositorio**

   ```bash
   git clone https://github.com/TantiE100/zapdos-io
   cd zapdos-io1
   ```

2. **Crea un entorno virtual (recomendado)**

   ```bash
   python -m venv .venv

   # En Windows
   .venv\Scripts\activate

   # En Linux/macOS
   source .venv/bin/activate
   ```

3. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

### Ejecución

```bash
streamlit run zapdos_optimizer.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📋 Modo de Uso

### Paso 1: Preparar los datos

1. **Revisa los ejemplos de referencia** 📸 en la aplicación:
   - Ejemplo de factura eléctrica (para obtener tarifas y potencia contratada)
   - Ejemplo de curva de potencia (patrón típico de consumo de 24 horas)
2. Descarga la plantilla Excel desde la aplicación
3. Completa las 24 filas con datos horarios:
   - **Generación solar disponible (kW)**: Potencia solar disponible cada hora
   - **Tarifa de compra (Bs/kWh)**: Costo de comprar energía de la red
   - **Tarifa de venta (Bs/kWh)**: Precio de venta de energía excedente
   - **Consumo base obligatorio (kW)**: Consumo fijo que no se puede optimizar

### Paso 2: Configurar el equipo

- **Nombre**: Identificador del equipo (ej: "Cafetera", "Bomba de agua")
- **Potencia nominal**: Consumo del equipo en Watts
- **Potencia contratada**: Límite máximo de la red en kW
- **Horas mínimas**: Tiempo mínimo de funcionamiento requerido

### Paso 3: Optimizar

1. Sube tu archivo de datos
2. Configura los parámetros del equipo
3. Haz clic en "🚀 Calcular plan óptimo"
4. Descarga los resultados en Excel y CSV

## 📸 Imágenes de Referencia

La aplicación incluye ejemplos visuales para facilitar la comprensión de los datos requeridos:

### 💡 Factura Eléctrica de Ejemplo

- **Ubicación**: `images/factura-ejemplo.png`
- **Propósito**: Muestra dónde encontrar las tarifas de compra/venta y la potencia contratada
- **Elementos clave**: Costo por kWh, potencia máxima contratada, estructura tarifaria

### ⚡ Curva de Potencia de Ejemplo

- **Ubicación**: `images/potencia-ejemplo.png`
- **Propósito**: Ilustra un patrón típico de consumo eléctrico de 24 horas
- **Elementos clave**: Picos de consumo, horarios de mayor/menor demanda, variación diaria

Estas imágenes se muestran en un expandible dentro de la aplicación para que los usuarios puedan consultarlas fácilmente mientras completan sus datos.

## 🔧 Estructura del Proyecto

```
zapdos-io1/
├── .streamlit/
│   └── config.toml          # Configuración de Streamlit
├── templates/
│   ├── diario_base.xlsx     # Plantilla de entrada de datos
│   └── plan_base.xlsx       # Plantilla para reportes
├── images/                  # Imágenes de referencia
│   ├── factura-ejemplo.png  # Ejemplo de factura eléctrica
│   ├── factura-ejemplo.jpeg # Ejemplo de factura (alternativo)
│   └── potencia-ejemplo.png # Ejemplo de curva de potencia
├── zapdos_optimizer.py      # Aplicación principal
├── requirements.txt         # Dependencias de Python
├── favicon.png             # Icono de la aplicación
└── README.md               # Este archivo
```

## 📊 Algoritmo de Optimización

El optimizador utiliza **programación lineal** para resolver el siguiente problema:

**Función Objetivo**: Minimizar

```
Σ(t=0 to 23) [Tarifa_compra(t) × Potencia_comprada(t) - Tarifa_venta(t) × Potencia_inyectada(t)]
```

**Restricciones**:

1. **Balance energético**: `Compra + Solar = Consumo_base + Consumo_equipo + Inyección`
2. **Límite de potencia**: `Compra ≤ Potencia_contratada`
3. **Tiempo mínimo**: `Σ Horas_encendido = Horas_mínimas`
4. **Variables binarias**: El equipo está encendido (1) o apagado (0)

## 🎨 Personalización

### Tema visual

Edita `.streamlit/config.toml` para personalizar colores:

```toml
[theme]
primaryColor="#FF9800"      # Color principal (naranja)
backgroundColor="#FFFFFF"    # Fondo blanco
secondaryBackgroundColor="#F7F8FA"  # Fondo secundario
textColor="#000000"         # Texto negro
font="sans serif"           # Fuente
```

### Configuración del servidor

```toml
[server]
headless = true
port = 8501

[browser]
gatherUsageStats = false
```

## 📈 Resultados

La aplicación genera:

1. **Resumen diario** (CSV):

   - Compra total de energía (kWh)
   - Inyección total a la red (kWh)
   - Ahorro económico total (Bs)
   - Porcentaje de ahorro vs. consumo base

2. **Plan detallado** (Excel):
   - Estado horario del equipo (ON/OFF)
   - Potencia comprada y vendida por hora
   - Ahorro acumulado
   - Formato con colores para fácil interpretación

## 🛠️ Dependencias

- **streamlit**: Framework web para aplicaciones de datos
- **pandas**: Manipulación y análisis de datos
- **openpyxl**: Lectura y escritura de archivos Excel
- **pulp**: Solver de optimización lineal

## 📝 Desarrollo

### Curso

**Investigación Operativa I** - Optimización de sistemas energéticos

### Tecnologías

- Python 3.8+
- Streamlit (UI web)
- PuLP (Optimización lineal)
- OpenPyXL (Manejo Excel)
- Pandas (Análisis de datos)

### Características técnicas

- Interfaz responsive y moderna
- Validación robusta de datos
- Manejo de errores elegante
- Exportación profesional a Excel
- Métricas en tiempo real

**© 2025 • Zapdos Optimizer**  
_Desarrollado para Investigación Operativa I_  
_Optimización inteligente de recursos energéticos_
