import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cocina Scout Pro", layout="wide")

# --- CONEXIÓN AL EXCEL ---
# Sustituye este ID por el tuyo de Google Sheets
SHEET_ID = "TU_ID_DE_GOOGLE_SHEETS_AQUI"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1UDTY__cuqBq7SZ6qKcsKJ3CQ_KcKUZALUBm86E_b8-o/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=60)
def cargar_datos():
    df = pd.read_csv(SHEET_URL)
    df.columns = [c.strip() for c in df.columns]
    return df

# --- FUNCIÓN PARA GENERAR PDF ---
def generar_pdf(df_calculado, plato_nombre, total_personas):
    pdf = FPDF()
    pdf.add_page()
    
    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="LISTA DE LA COMPRA - SCOUTS", ln=True, align="C")
    
    # Info del plato
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, txt=f"Plato: {plato_nombre}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Fecha: {datetime.date.today()}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Raciones Equivalentes Totales: {total_personas:.2f}", ln=True, align="L")
    pdf.ln(10)
    
    # Tabla - Cabecera
    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 10, "Ingrediente", 1)
    pdf.cell(60, 10, "Cantidad Total", 1)
    pdf.ln()
    
    # Tabla - Datos
    pdf.set_font("Arial", "", 12)
    for _, fila in df_calculado.iterrows():
        pdf.cell(80, 10, str(fila['Ingrediente']), 1)
        pdf.cell(60, 10, str(fila['TOTAL COMPRA']), 1)
        pdf.ln()
        
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.title("⚜️ Gestión de Cocina y Lista de Compra")

try:
    df = cargar_datos()
    
    # --- BARRA LATERAL (CENSO) ---
    with st.sidebar:
        st.header("1. Censo")
        c = st.number_input("Castores (x0.6)", value=5)
        l = st.number_input("Lobatos (x0.8)", value=8)
        r = st.number_input("Rangers (x1.0)", value=10)
        p = st.number_input("Pioneros (x1.2)", value=10)
        m = st.number_input("Monitores (x1.1)", value=4)
        
        re_total = (c*0.6) + (l*0.8) + (r*1.0) + (p*1.2) + (m*1.1)
        st.metric("Raciones Totales", f"{re_total:.2f}")

    # --- CALCULADORA ---
    plato_sel = st.selectbox("Selecciona el plato para la lista:", df['A: Plato'].unique())
    items = df[df['A: Plato'] == plato_sel]

    lista_para_tabla = []
    for _, fila in items.iterrows():
        g_base = fila['C: Gramos_Persona']
        unidad = fila['D: Unidad']
        
        # Cálculos por rama
        ramos = {
            "Castores": g_base * c * 0.6,
            "Lobatos": g_base * l * 0.8,
            "Rangers": g_base * r * 1.0,
            "Pioneros": g_base * p * 1.2,
            "Monitores": g_base * m * 1.1
        }
        total_ing = sum(ramos.values())

        # Formateo de texto
        def fmt(v, u):
            if u == 'uds': return f"{v/g_base:.1f} uds"
            return f"{v/1000:.2f} kg" if v >= 1000 else f"{int(v)} {u}"

        resumen = {"Ingrediente": fila['B: Ingrediente']}
        for nombre, valor in ramos.items():
            resumen[nombre] = fmt(valor, unidad)
        resumen["TOTAL COMPRA"] = fmt(total_ing, unidad)
        lista_para_tabla.append(resumen)

    df_final = pd.DataFrame(lista_para_tabla)
    
    st.subheader(f"Desglose de Ingredientes: {plato_sel}")
    st.table(df_final)

    # --- BOTÓN DE PDF ---
    st.divider()
    pdf_data = generar_pdf(df_final, plato_sel, re_total)
    
    st.download_button(
        label="📥 Descargar Lista de la Compra en PDF",
        data=pdf_data,
        file_name=f"lista_compra_{plato_sel.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )

    # --- ENLACE DE EDICIÓN ---
    st.sidebar.divider()
    st.sidebar.link_button("📝 Editar Excel", f"https://docs.google.com/spreadsheets/d/1UDTY__cuqBq7SZ6qKcsKJ3CQ_KcKUZALUBm86E_b8-o/edit")

except Exception as e:
    st.error("Error al cargar datos. Revisa el ID de Google Sheets.")
    st.write(e)