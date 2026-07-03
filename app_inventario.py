import streamlit as st
import pandas as pd
import os
from PIL import Image

st.set_page_config(page_title="Control de Inventarios", page_icon="📦", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #1a1a1a; }
    h1 { color: #ffffff; text-align: center; font-family: Arial; }
    p { color: #aaaaaa; }
    div[data-testid="stDecoration"] { display: none; }
    </style>
""", unsafe_allow_html=True)

if "codigo_procesado" not in st.session_state:
    st.session_state.codigo_procesado = ""

def limpiar_y_procesar():
    st.session_state.codigo_procesado = st.session_state.input_codigo
    st.session_state.input_codigo = ""

ruta_logo = "logo_empresa.png"
if os.path.exists(ruta_logo):
    img_logo = Image.open(ruta_logo)
    col1, col2, col3 = st.columns(3)
    with col2:
        st.image(img_logo, use_container_width=True)

st.title("SISTEMA CONTROL DE INVENTARIOS PRINDEL")
st.markdown("<p style='text-align: center; font-style: italic; color: #aaaaaa;'>Modo: Listo para Escaneo Continuo</p>", unsafe_allow_html=True)
st.markdown("<hr style='border-top: 1px dashed #444;'>", unsafe_allow_html=True)

st.text_input(
    "[ESCANEAR CAJA AQUÍ] -> ", 
    key="input_codigo", 
    placeholder="Leer código de barras o digita el ID de Caja...",
    on_change=limpiar_y_procesar
)

codigo_actual = st.session_state.codigo_procesado

if codigo_actual:
    codigo_actual = codigo_actual.replace("'", "-")
    try:
        df = pd.read_csv("inventario_licores.csv", sep="|", encoding="latin-1", keep_default_na=False)
        df.columns = df.columns.str.strip()
        df["id_caja"] = df["id_caja"].astype(str).str.strip()
        df["cantidad_botellas"] = pd.to_numeric(df["cantidad_botellas"], errors="coerce").fillna(0).astype(int)
        
        resultado = df[df["id_caja"] == codigo_actual]
        
        if not resultado.empty:
            fila = resultado.iloc[0]
            ref_licor = fila["referencia_licor"]
            
            # === CÁLCULOS DEL INVENTARIO CONSOLIDADO ===
            mismo_producto = df[df["referencia_licor"] == ref_licor]
            total_cajas_ref = len(mismo_producto)
            total_unidades_ref = mismo_producto["cantidad_botellas"].sum()
            
            st.markdown(f"""
                <div style="border: 3px solid #2ecc71; padding: 25px; border-radius: 10px; background-color: #f9f9f9; font-family: Arial, sans-serif; margin-top: 20px;">
                    <h2 style="color: #27ae60; margin-top: 0; text-align: left; font-family: Arial;">✅ CAJA VERIFICADA</h2>
                    <hr style="border-top: 1px solid #ccc; margin: 10px 0;">
                    <p style="font-size: 16px; color: #2c3e50; margin: 8px 0; font-family: Arial;"><strong>📦 ID de Caja:</strong> <span style="font-size: 18px; color: #2c3e50;">{fila['id_caja']}</span></p>
                    <p style="font-size: 18px; color: #d35400; margin: 8px 0; font-family: Arial;"><strong>🍾 Contenido:</strong> {ref_licor}</p>
                    <p style="font-size: 20px; color: #2980b9; margin: 8px 0; font-family: Arial;"><strong>🔢 Cantidad en ESTA Caja:</strong> {fila['cantidad_botellas']} Unidades</p>
                    <p style="font-size: 14px; color: #7f8c8d; margin: 8px 0; font-family: Arial;"><strong>📝 Notas:</strong> {fila['detalles_producto']}</p>
                    <hr style="border-top: 2px solid #34495e; margin: 15px 0;">
                    <h3 style="color: #2c3e50; margin-top: 0; font-size: 16px; font-family: Arial;">📊 CONSOLIDADO EN BODEGA (Misma Referencia)</h3>
                    <div style="display: flex; gap: 10px; margin-bottom: 15px; font-family: Arial;">
                        <div style="flex: 1; background-color: #eaf2f8; padding: 10px; border-radius: 5px; border-left: 5px solid #2980b9;"><strong>📦 Cajas Totales:</strong><br><span style="font-size: 20px; color: #1f618d;">{total_cajas_ref} Cajas</span></div>
                        <div style="flex: 1; background-color: #fef9e7; padding: 10px; border-radius: 5px; border-left: 5px solid #f39c12;"><strong>🍾 Unidades Totales:</strong><br><span style="font-size: 20px; color: #b7950b;">{total_unidades_ref} Botellas</span></div>
                    </div>
                    <div style="font-size: 15px; color: #2c3e50; background-color: #e8f8f5; padding: 10px; border-radius: 5px; border-left: 5px solid #1abc9c; font-family: Arial;">
                        <strong>👤 Responsable Inventario:</strong> {fila['operario_conteo']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="border: 3px solid #e74c3c; padding: 25px; border-radius: 10px; background-color: #fdf2f2; font-family: Arial, sans-serif; margin-top: 20px;">
                    <h2 style="color: #c0392b; margin-top: 0; text-align: left; font-family: Arial;">❌ CAJA NO ENCONTRADA</h2>
                    <hr style="border-top: 1px solid #ccc; margin: 10px 0;">
                    <p style="font-size: 16px; text-align: center; color: #2c3e50; font-family: Arial;">El código <strong>\\"{codigo_actual}\\"</strong> no existe en el sistema.</p>
                </div>
            """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("No se encontró el archivo 'inventario_licores.csv'.")
