import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
import math

# --- CONFIGURACIÓN DE PÁGINA Y ESTILOS ---
st.set_page_config(page_title="Menu Scout GSBV", layout="wide", page_icon="⚜️")

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
    .stMetric { 
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1); 
        border-left: 5px solid #ffffff;
    }
    .stMetric div {
        color: #1b45b4 !important;
    }
    h1 { color: #ffffff; text-align: center; }
    h3 { color: #ffffff; border-bottom: 2px solid #ffffff; padding-bottom: 5px; margin-top: 30px; }
    hr { border-top: 2px solid #1b45b4 !important; }
    
    span[data-baseweb="tag"] {
        background-color: #1b45b4 !important;
    }
    div[data-baseweb="select"] {
        border-color: #1b45b4 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
SHEET_ID = "13jxaA8o2S0ORwAj_O7OtVzfhPKZfQT5IA7HV2K-M-hg"
URL_ING = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
GID_PLANTILLAS = "1660862399" 
URL_PLAN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_PLANTILLAS}"

@st.cache_data(ttl=5)
def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip() for c in df.columns]
        return df.dropna(how='all')
    except:
        return pd.DataFrame()

def generar_pdf(df_final, total_pax, re_total, resumen_menu, censo_dict):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- PÁGINA 1: PLANIFICACIÓN ---
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(27, 69, 180) 
    pdf.cell(w=200, h=10, txt="PLANIFICACION DE MENU - GSBV", border=0, ln=1, align="C")
    pdf.ln(10)
    
    pdf.set_text_color(0, 0, 0)
    for dia, momentos_dict in resumen_menu.items():
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(27, 69, 180) 
        pdf.set_text_color(255, 255, 255)
        pdf.cell(190, 8, f" {dia}", 1, 1, 'L', True)
        
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(0, 0, 0)
        for m, platos in momentos_dict.items():
            if platos:
                txt_platos = ", ".join(platos).encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(190, 6, f"{m}: {txt_platos}", border=1)
        pdf.ln(2)

    # --- PÁGINA 2: COMPRA ---
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(27, 69, 180)
    pdf.cell(200, 10, "LISTA DE LA COMPRA FINAL", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, f"Personas Totales: {total_pax}", ln=True)
    pdf.ln(5)
    
    # Cabecera: solo 2 columnas para que quepa bien el texto formateado
    pdf.set_fill_color(27, 69, 180) 
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(100, 10, " Ingrediente", 1, 0, 'L', True)
    pdf.cell(80, 10, " Cantidad Total", 1, 1, 'L', True)

    pdf.set_text_color(0, 0, 0)
    factores = {"Cas": 0.70, "Lob": 0.85, "Exp": 1.0, "Pio": 1.25, "Rut": 1.35, "Mon": 1.40}
    nombres_ramas = {"Cas": "Castores", "Lob": "Lobatos", "Exp": "Exploradores", "Pio": "Pioneros", "Rut": "Rutas", "Mon": "Kraal"}

    for _, fila in df_final.iterrows():
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(240, 240, 240)
        
        ing = str(fila['Ingrediente']).encode('latin-1', 'replace').decode('latin-1')
        # USAMOS 'Compra Final' que ya tiene el redondeo y los 2 decimales
        compra_txt = str(fila['Compra Final']).encode('latin-1', 'replace').decode('latin-1')
        
        pdf.cell(100, 10, f" {ing}", 1, 0, 'L', True)
        pdf.cell(80, 10, f" {compra_txt}", 1, 1, 'L', True)
        
        # Desglose por ramas
        pdf.set_font("Arial", "I", 8)
        pdf.set_text_color(100, 100, 100)
        
        cant_total_num = fila['Cantidad_Base']
        racion_base = cant_total_num / re_total if re_total > 0 else 0
        uni = str(fila['Unidad']).encode('latin-1', 'replace').decode('latin-1')

        desglose_txt = ""
        for cod, num in censo_dict.items():
            if num > 0:
                cant_rama = (racion_base * factores[cod]) * num
                # Aquí forzamos 2 decimales en el desglose
                desglose_txt += f"{nombres_ramas[cod]}: {cant_rama:.2f} {uni} | "
        
        pdf.multi_cell(180, 5, desglose_txt, border='LRB')
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1)

    return pdf.output(dest='S').encode('latin-1')


df_recetas = cargar_datos(URL_ING)
df_plantillas = cargar_datos(URL_PLAN)
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
momentos = ["Desayuno", "Almuerzo", "Comida", "Merienda", "Cena"]

with st.sidebar:
    st.header("👥 Personas y Fechas")
    f_ini = st.date_input("Fecha inicio", datetime.date.today())
    f_fin = st.date_input("Fecha fin", datetime.date.today() + datetime.timedelta(days=3))
    st.divider()
    cas = st.number_input("Castores", 0, 500, 0)
    lob = st.number_input("Lobatos", 0, 500, 0)
    exp = st.number_input("Exploradores", 0, 500, 0)
    pio = st.number_input("Pioneros", 0, 500, 0)
    rut = st.number_input("Rutas", 0, 500, 0)
    mon = st.number_input("Kraal + Staff", 0, 500, 0)

    total_pax = cas + lob + exp + pio + rut + mon
    re_total = (cas * 0.70) + (lob * 0.85) + (exp * 1.0) + (pio * 1.30) + (rut * 1.40) + (mon * 1.45)
    
    st.metric("Total Personas", f"{total_pax}")

st.title("⚜️ Planificador de Intendencia GSBV")

if not df_recetas.empty:
    c_plat, c_ing, c_gram, c_uni = df_recetas.columns[0], df_recetas.columns[1], df_recetas.columns[2], df_recetas.columns[3]

    if not df_plantillas.empty:
        with st.expander("📂 Cargar Menú desde Plantilla"):
            nombres_p = ["Ninguna"] + list(df_plantillas["Nombre_Plantilla"].unique())
            plantilla_sel = st.selectbox("Selecciona plantilla:", nombres_p)
            if st.button("Aplicar"):
                datos_p = df_plantillas[df_plantillas["Nombre_Plantilla"] == plantilla_sel]
                for i in range((f_fin - f_ini).days + 1):
                    fecha_p = f_ini + datetime.timedelta(days=i)
                    for m in momentos:
                        matches = datos_p[(datos_p["Dia_Relativo"] == (i+1)) & (datos_p["Momento"] == m)]
                        if not matches.empty:
                            st.session_state[f"sel_{fecha_p}_{m}"] = matches["Plato"].tolist()
                st.rerun()

    platos_opciones = sorted([str(p) for p in df_recetas[c_plat].dropna().unique()])
    num_dias = (f_fin - f_ini).days + 1
    for i in range(num_dias):
        fecha = f_ini + datetime.timedelta(days=i)
        st.subheader(f"📅 {DIAS_SEMANA[fecha.weekday()]} {fecha.strftime('%d/%m')}")
        cols = st.columns(len(momentos))
        for j, m in enumerate(momentos):
            key = f"sel_{fecha}_{m}"
            cols[j].multiselect(f"{m}", platos_opciones, key=key)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- VALIDACIÓN Y CÁLCULO ---
    if st.button("📦 PREPARAR LISTA DE COMPRA"):
        # Comprobar si hay niños introducidos
        if total_pax <= 0:
            st.error("⚠️ Error: Debes introducir el número de personas en la barra lateral.")
        else:
            acumulado = []
            resumen_menu = {}
            platos_seleccionados_total = 0

            for i in range(num_dias):
                fecha_loop = f_ini + datetime.timedelta(days=i)
                tag_dia = f"{DIAS_SEMANA[fecha_loop.weekday()]} {fecha_loop.strftime('%d/%m')}"
                resumen_menu[tag_dia] = {}
                for m in momentos:
                    seleccionados = st.session_state.get(f"sel_{fecha_loop}_{m}", [])
                    resumen_menu[tag_dia][m] = seleccionados
                    platos_seleccionados_total += len(seleccionados)
                    for plato in seleccionados:
                        ingreds = df_recetas[df_recetas[c_plat] == plato]
                        for _, row in ingreds.iterrows():
                            try: val = float(str(row[c_gram]).replace(',', '.').strip())
                            except: val = 0.0
                            acumulado.append({"Ingrediente": row[c_ing], "Cantidad_Base": val * re_total, "Unidad": row[c_uni]})
            
            # Comprobar si hay alimentos seleccionados
            if platos_seleccionados_total == 0:
                st.error("⚠️ Error: No has seleccionado ningún plato en el calendario.")
            elif acumulado:
                df_calculado = pd.DataFrame(acumulado).groupby(['Ingrediente', 'Unidad'])['Cantidad_Base'].sum().reset_index()
                df_calculado = df_calculado[['Ingrediente', 'Cantidad_Base', 'Unidad']]
                st.session_state["df_compra"] = df_calculado
                st.session_state["resumen_menu"] = resumen_menu
                st.success("✅ Lista generada con éxito. Revisa y ajusta las cantidades abajo.")

    if "df_compra" in st.session_state:
        st.info("💡 Puedes hacer doble clic en las cantidades para ajustarlas manualmente si lo necesitas.")
        df_editado = st.data_editor(
            st.session_state["df_compra"],
            column_config={
                "Cantidad_Base": st.column_config.NumberColumn("Cantidad (Editar aquí)", format="%.2f"),
                "Ingrediente": st.column_config.Column(disabled=True),
                "Unidad": st.column_config.Column(disabled=True)
            },
            hide_index=True,
            use_container_width=True
        )

        def fmt(v, u):
            # Redondeamos SIEMPRE hacia arriba
            v_redondeado = math.ceil(v) 
            
            u_str = str(u).lower()
            if 'uds' in u_str: 
                return f"{v_redondeado} uds"
            
            # Si son gramos/ml y pasan de 1000, convertimos a kg/l con 2 decimales
            if v >= 1000:
                return f"{v/1000:.2f} kg/l" 
            
            return f"{v_redondeado} {u}"
        
        df_editado['Compra Final'] = df_editado.apply(lambda x: fmt(x['Cantidad_Base'], x['Unidad']), axis=1)

       # Creamos el diccionario con los datos del censo (nombres que usaste en el sidebar)
        censo_para_pdf = {
            "Cas": cas, 
            "Lob": lob, 
            "Exp": exp, 
            "Pio": pio, 
            "Rut": rut, 
            "Mon": mon
        }

        # Llamamos a la función pasando los 5 argumentos en orden
        pdf_data = generar_pdf(
            df_editado, 
            total_pax, 
            re_total, 
            st.session_state["resumen_menu"], 
            censo_para_pdf
        )
        
        st.download_button("📥 Descargar Informe Final Ajustado (PDF)", pdf_data, f"compra_GSBV_{datetime.date.today()}.pdf")