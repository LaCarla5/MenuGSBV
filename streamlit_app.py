import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime

# --- CONFIGURACIÓN DE PÁGINA Y ESTILOS ---
st.set_page_config(page_title="Menu Scout", layout="wide", page_icon="⚜️")

# Inyectar CSS personalizado para cambiar colores y fuentes
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { 
        background-color: #1b45b4; 
        color: white; 
        border-radius: 10px; 
        height: 3em; 
        width: 100%;
        font-weight: bold;
    }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    h1 { color: #1b45b4; }
    h3 { color: #1b45b4; border-bottom: 2px solid #1b45b4; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
SHEET_ID = "1UDTY__cuqBq7SZ6qKcsKJ3CQ_KcKUZALUBm86E_b8-o"
URL_ING = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"


@st.cache_data(ttl=5)
def cargar_ingredientes():
    try:
        df = pd.read_csv(URL_ING)
        df.columns = [str(c).strip() for c in df.columns]
        df = df.dropna(how='all')
        return df
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame()


DIAS_SEMANA = ["Lunes", "Martes", "Miércoles",
               "Jueves", "Viernes", "Sábado", "Domingo"]

# --- FUNCIÓN GENERAR PDF ---


def generar_pdf(df_final, total_pax, re_total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="LISTA DE LA COMPRA", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Fecha: {datetime.date.today()}", ln=True)
    pdf.cell(
        200, 10, txt=f"Total Personas: {total_pax} | Raciones Eq: {re_total:.2f}", ln=True)
    pdf.ln(5)

    # Cabecera tabla
    pdf.set_fill_color(27, 69, 180)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(100, 10, " Ingrediente", 1, 0, 'L', True)
    pdf.cell(60, 10, " Cantidad Total", 1, 1, 'L', True)

    # Cuerpo tabla
    pdf.set_text_color(0, 0, 0)
    for _, fila in df_final.iterrows():
        pdf.cell(100, 10, f" {fila['Ingrediente']}", 1)
        pdf.cell(60, 10, f" {fila['Compra Final']}", 1)
        pdf.ln()

    return pdf.output(dest='S').encode('latin-1')


df_recetas = cargar_ingredientes()

if not df_recetas.empty:
    c_plat, c_ing, c_gram, c_uni = df_recetas.columns[0], df_recetas.columns[
        1], df_recetas.columns[2], df_recetas.columns[3]

    with st.sidebar:
        st.header("👥 Personas y Fechas")
        f_ini = st.date_input("Inicio", datetime.date.today())
        f_fin = st.date_input(
            "Fin", datetime.date.today() + datetime.timedelta(days=3))
        st.markdown("<hr style='border-top: 2px solid #1b45b4;'>",
                    unsafe_allow_html=True)
        cas = st.number_input("Castores", 0, 100, 5)
        lob = st.number_input("Lobatos", 0, 100, 8)
        ran = st.number_input("Rangers", 0, 100, 10)
        pio = st.number_input("Pioneros", 0, 100, 10)
        mon = st.number_input("Monitores", 0, 100, 8)

        total_pax = cas + lob + ran + pio + mon
        re_total = (cas*0.6) + (lob*0.8) + (ran*1.0) + (pio*1.1) + (mon*1.2)
        st.info(f"Personas Totales: {total_pax}")

    st.title("⚜️ Planificador Scout")

    lista_limpia = df_recetas[c_plat].dropna().unique()
    platos_lista = ["Ninguno"] + sorted([str(p) for p in lista_limpia])

    num_dias = (f_fin - f_ini).days + 1
    momentos = ["Desayuno", "Almuerzo", "Comida", "Merienda", "Cena"]

# 1. Cargar la pestaña de plantillas (asumiendo que es la segunda pestaña gid=12345)
# Tienes que buscar el GID de la pestaña 'Plantillas' en la URL de tu Google Sheet
GID_PLANTILLAS = "908771195" 
URL_PLAN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_PLANTILLAS}"

@st.cache_data(ttl=5)
def cargar_plantillas():
    try:
        df = pd.read_csv(URL_PLAN)
        return df
    except:
        return pd.DataFrame()

df_plantillas = cargar_plantillas()

# 2. Selector de Plantilla en la Interfaz
if not df_plantillas.empty:
    with st.expander("📂 Reutilizar Menús Guardados"):
        nombres_plantillas = ["Ninguna"] + list(df_plantillas["Nombre_Plantilla"].unique())
        plantilla_sel = st.selectbox("Selecciona una plantilla para autorrellenar:", nombres_plantillas)
        
        if st.button("Aplicar esta Plantilla"):
            datos_p = df_plantillas[df_plantillas["Nombre_Plantilla"] == plantilla_sel]
            
            # Recorremos los días actuales y buscamos su equivalente en la plantilla
            for i in range(num_dias):
                fecha_p = f_ini + datetime.timedelta(days=i)
                dia_rel = i + 1 # Día 1, Día 2...
                
                for m in momentos:
                    # Buscamos si hay un plato guardado para este día y momento
                    match = datos_p[(datos_p["Dia_Relativo"] == dia_rel) & (datos_p["Momento"] == m)]
                    if not match.empty:
                        plato_guardado = match.iloc[0]["Plato"]
                        # Guardamos en el session_state para que el selectbox lo coja
                        st.session_state[f"sel_{fecha_p}_{m}"] = plato_guardado
            
            st.rerun() # Refrescamos la página para que se vean los cambios


    # CALENDARIO
    for i in range(num_dias):
        fecha = f_ini + datetime.timedelta(days=i)
        st.subheader(
            f"📅 {DIAS_SEMANA[fecha.weekday()]} {fecha.strftime('%d/%m')}")
        cols = st.columns(len(momentos))
        for j, momento in enumerate(momentos):
            key = f"sel_{fecha}_{momento}"
            cols[j].selectbox(f"{momento}", platos_lista, key=key)

    st.markdown("<hr style='border-top: 2px solid #1b45b4;'>",
                unsafe_allow_html=True)

    # CÁLCULO Y PDF
    if st.button("📦 CALCULAR COMPRA TOTAL"):
        acumulado = []
        for i in range(num_dias):
            f_loop = f_ini + datetime.timedelta(days=i)
            for m in momentos:
                k = f"sel_{f_loop}_{m}"
                if k in st.session_state and st.session_state[k] != "Ninguno":
                    p_sel = st.session_state[k]
                    ingreds = df_recetas[df_recetas[c_plat] == p_sel]
                    for _, row in ingreds.iterrows():
                        try:
                            val = str(row[c_gram]).replace(',', '.').strip()
                            g_p = float(val)
                        except:
                            g_p = 0.0
                        acumulado.append(
                            {"Ingrediente": row[c_ing], "Unidad": row[c_uni], "Cant": g_p * re_total})

        if acumulado:
            df_c = pd.DataFrame(acumulado)
            df_f = df_c.groupby(['Ingrediente', 'Unidad'])[
                'Cant'].sum().reset_index()

            def formatear(v, u):
                u_str = str(u).lower()
                if 'uds' in u_str:
                    return f"{int(v)} uds"
                return f"{v/1000:.2f} kg/l" if v >= 1000 else f"{int(v)} {u}"

            df_f['Compra Final'] = df_f.apply(
                lambda x: formatear(x['Cant'], x['Unidad']), axis=1)

            st.table(df_f[['Ingrediente', 'Compra Final']])

            # Generar PDF
            pdf_data = generar_pdf(df_f, total_pax, re_total)
            st.download_button(label="📥 Descargar Lista en PDF", data=pdf_data,
                               file_name="compra_scout.pdf", mime="application/pdf")
        else:
            st.warning("⚠️ No has seleccionado platos.")


