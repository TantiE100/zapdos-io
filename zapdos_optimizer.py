import datetime, io, os
import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side, numbers
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, PULP_CBC_CMD

tmpl_dir     = "templates"
diario_input = os.path.join(tmpl_dir, "diario_base.xlsx")
plan_tmpl    = os.path.join(tmpl_dir, "plan_base.xlsx")

st.set_page_config(page_title="Zapdos", page_icon="favicon.png", layout="centered")
st.title("⚡ Zapdos — Plan Diario")

# 1. Descarga plantilla diaria
st.header("1. Descarga plantilla de 24 horas, y llena los datos")
with open(diario_input, "rb") as f:
    st.download_button("📥 Descargar plantilla 24 h", data=f,
                       file_name="plantilla_diaria.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       key="download_template")

# 2. Carga de datos
st.header("2. Sube tu archivo horario diario (.xlsx / .csv)")

uploaded = st.file_uploader("Archivo de 24 filas (.xlsx)", type=["xlsx"], key="upload_schedule")
if not uploaded:
    st.stop()

try:
    df = pd.read_excel(uploaded)
except Exception:
    st.error("El archivo no es un .xlsx válido.")
    st.stop()

req_cols = [
    "Generación solar disponible (kW)",
    "Tarifa de compra (Bs / kWh)",
    "Tarifa de venta (Bs / kWh)",
    "Consumo base obligatorio (kW)"
]
faltantes = [c for c in req_cols if c not in df.columns]
if faltantes:
    st.error(f"Faltan columnas: {', '.join(faltantes)}. Descarga y usa la plantilla.")
    st.stop()

# Limpieza
solar_col = "Generación solar disponible (kW)"
df[solar_col] = df[solar_col].replace("-", 0).fillna(0).astype(float)
df["Tarifa de compra (Bs / kWh)"]   = df["Tarifa de compra (Bs / kWh)"].astype(float)
df["Tarifa de venta (Bs / kWh)"]    = df["Tarifa de venta (Bs / kWh)"].astype(float)
df["Consumo base obligatorio (kW)"] = df["Consumo base obligatorio (kW)"].astype(float)

st.success("📊 Datos diarios cargados")
st.dataframe(df, width=1000, height=300)

# 3. Parámetros del equipo
st.header("3. Configura tu equipo")
nombre = st.text_input("Nombre del equipo", placeholder="cafetera, refrigerador, etc.", key="input_name")

col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("images/potencia-ejemplo.png", width=500, caption="Imagen de ejemplo: Potencia nominal")

pot_w = st.number_input(
    "Potencia nominal (W)",
    min_value=1,
    max_value=20000,
    value=50,
    key="input_power"
)
pot_kW = pot_w / 1000  # Definir pot_kW

col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("images/factura-ejemplo.png", width=500)

pot_contrat = st.number_input(
    "Potencia contratada (kW)",
    min_value=0.1,
    value=7.0,
    max_value=100.0,
    key="input_contract"
)

horas_min = st.number_input(
    "Horas mínimas de funcionamiento",
    min_value=1,
    max_value=24,
    value=3,
    key="input_horas"
)

# 4. Optimización
if st.button("🚀 Calcular plan diario óptimo", key="btn_optimize"):
    if not nombre.strip():
        st.error("Debes ingresar un nombre de equipo antes de optimizar.")
    else:
        # PROGRAMACION LINEAL
        T = range(24)
        Compra = LpVariable.dicts("Compra_kW", T, 0)
        Venta  = LpVariable.dicts("Inyeccion_kW", T, 0)
        ON     = LpVariable.dicts("ON", T, cat="Binary")

        model = LpProblem("ZapdosDiario", LpMinimize)
        model += lpSum(df["Tarifa de compra (Bs / kWh)"][t] * Compra[t] -
                    df["Tarifa de venta (Bs / kWh)"][t] * Venta[t] for t in T)

        for t in T:
            model += (Compra[t] + df[solar_col][t] ==
                    df["Consumo base obligatorio (kW)"][t] + pot_kW * ON[t] + Venta[t])
            model += Compra[t] <= pot_contrat
        model += lpSum(ON[t] for t in T) == horas_min
        model.solve(PULP_CBC_CMD(msg=False))

        # 5. Plan + métricas
        costo_base = (df["Tarifa de compra (Bs / kWh)"] *
                    df["Consumo base obligatorio (kW)"]).sum()
        costo_opt  = 0
        filas = []
        for t in T:
            comp = Compra[t].value(); iny = Venta[t].value()
            costo_opt += (df["Tarifa de compra (Bs / kWh)"][t] * comp -
                        df["Tarifa de venta (Bs / kWh)"][t] * iny)
            ahorro = costo_base - costo_opt
            pct    = ahorro / costo_base if costo_base else 0
            filas.append((t+1, int(ON[t].value()), comp, iny, ahorro, pct))

        plan = pd.DataFrame(filas, columns=[
            "Intervalo horario (h)", "Estado equipo (0/1)",
            "Potencia comprada a la red (kW)",
            "Potencia inyectada a la red (kW)",
            "Ahorro acumulado (Bs)", "Ahorro vs. Base (%)"
        ])

        # 7. Rellenar plantilla y descargar XLSX
        wb = load_workbook(plan_tmpl)
        ws = wb.active

        ws.insert_rows(1)
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=6)
        t = ws.cell(row=1, column=1, value=f"PLAN ÓPTIMO DIARIO - {nombre}".upper())
        t.font = Font(bold=True, size=16)
        t.alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 28

        header_fill = PatternFill(start_color='FFE6E6E6', end_color='FFE6E6E6', fill_type='solid')
        header_font = Font(bold=True)
        thin = Side(border_style='thin', color='FF000000')

        for cell in ws.iter_cols(min_row=2, max_row=2, min_col=1, max_col=6):
            for c in cell:
                c.fill = header_fill
                c.font = header_font
                c.alignment = Alignment(horizontal='center', vertical='center')
                c.border = Border(bottom=thin)

        start = 3
        
        lavender20 = PatternFill(start_color='FFEFE8FF', end_color='FFEFE8FF', fill_type='solid')
        pink20     = PatternFill(start_color='FFFFF2F2', end_color='FFFFF2F2', fill_type='solid')
        green20    = PatternFill(start_color='FFE8FFE8', end_color='FFE8FFE8', fill_type='solid')
        pink60     = PatternFill(start_color='FFFFC0C0', end_color='FFFFC0C0', fill_type='solid')
        green60    = PatternFill(start_color='FFC0FFC0', end_color='FFC0FFC0', fill_type='solid')

        start = 3
        for r, row in enumerate(plan.itertuples(index=False), start=start):
            hora_txt = f"{row[0]:02d}:00" if row[0] < 24 else "24:00"
            estado   = "ON" if row[1] == 1 else "OFF"

            c_hora = ws.cell(r, 1, hora_txt)
            c_hora.fill = lavender20

            c_status = ws.cell(r, 2, estado)
            c_status.fill = green20 if estado=='ON' else pink20

            c_compra = ws.cell(r, 3, row[2])
            c_compra.number_format = numbers.FORMAT_NUMBER_00
            c_compra.fill = pink60 if row[2] != 0 else green60

            if row[3] == 0:
                c_iny = ws.cell(r, 4, "Sin exposición solar")
                c_iny.fill = pink20
            else:
                c_iny = ws.cell(r, 4, row[3])
                c_iny.number_format = numbers.FORMAT_NUMBER_00

            c_ahorro = ws.cell(r, 5, row[4])
            c_ahorro.number_format = numbers.FORMAT_NUMBER_00

            c_pct = ws.cell(r, 6, row[5])
            c_pct.number_format = "0.00%"

        bd = Border(top=thin, left=thin, right=thin, bottom=thin)
        for row in ws.iter_rows(min_row=start, max_row=start+23, min_col=1, max_col=6):
            for cell in row:
                cell.border = bd

        green_scale = ColorScaleRule(start_type='min', start_color='FFE8FBE8',
                                    mid_type='percentile', mid_value=50, mid_color='FF8FD88F',
                                    end_type='max', end_color='FF008000')
        blue_scale = ColorScaleRule(start_type='min', start_color='FFEAF4FF',
                                    mid_type='percentile', mid_value=50, mid_color='FF7AB8FF',
                                    end_type='max', end_color='FF0066CC')

        ws.conditional_formatting.add(f'D{start}:D{start+23}', green_scale)
        ws.conditional_formatting.add(f'E{start}:E{start+23}', green_scale)
        ws.conditional_formatting.add(f'F{start}:F{start+23}', blue_scale)

        ws.freeze_panes = 'A3'
        if ws.tables:
            ws.tables.clear()

        buf = io.BytesIO(); wb.save(buf)
        fecha = datetime.datetime.now().strftime("%d-%m-%Y")
        file_name = f"plan_optimo_{nombre.lower()}_{horas_min}_{fecha}.xlsx"
        st.download_button("⬇️ Descargar plan (.xlsx)", buf.getvalue(),
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"download_xlsx_{horas_min}_{fecha}")

        st.success("✅ Plan diario generado")

st.markdown("---")
st.caption("© 2025 • Zapdos - Investigación Operativa I")