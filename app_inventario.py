import streamlit as st
import pandas as pd
import os
from PIL import Image

ruta_logo = 'logo_empresa.png'
if os.path.exists(ruta_logo):
    icono_pestana = Image.open(ruta_logo)
else:
    icono_pestana = '📦'

st.set_page_config(page_title='Control de Inventarios', page_icon=icono_pestana, layout='centered')

st.markdown('<style>.stApp { background-color: #1a1a1a; } h1 { color: #ffffff; text-align: center; } p { color: #aaaaaa; } div[data-testid="stDecoration"] { display: none; }</style>', unsafe_allow_html=True)

if 'codigo_procesado' not in st.session_state:
    st.session_state.codigo_procesado = ''
if 'input_codigo' not in st.session_state:
    st.session_state.input_codigo = ''

def limpiar_y_procesar():
    if 'input_codigo' in st.session_state:
        codigo_limpio = st.session_state.input_codigo.replace("'", "-")
        st.session_state.codigo_procesado = codigo_limpio
        st.session_state.input_codigo = ''

if os.path.exists(ruta_logo):
    col1, col2, col3 = st.columns(3)
    with col2: st.image(Image.open(ruta_logo), use_container_width=True)

st.title('SISTEMA CONTROL DE INVENTARIOS PRINDEL')
st.text_input('[ESCANEAR CAJA AQUÍ] -> ', key='input_codigo', placeholder='Leer código de barras...', on_change=limpiar_y_procesar)

codigo_actual = st.session_state.codigo_procesado
if codigo_actual:
    try:
        df = pd.read_csv('inventario_licores.csv', sep='|', encoding='latin-1', keep_default_na=False)
        df.columns = df.columns.str.strip()
        df['id_caja'] = df['id_caja'].astype(str).str.strip()
        df['cajas_totales'] = pd.to_numeric(df['cajas_totales'], errors='coerce').fillna(1).astype(int)
        df['cantidad_por_caja'] = pd.to_numeric(df['cantidad_por_caja'], errors='coerce').fillna(12).astype(int)
        codigo_base = '-'.join(codigo_actual.split('-')[:2]) if '-' in codigo_actual else codigo_actual
        resultado = df[df['id_caja'] == codigo_base]
        if not resultado.empty:
            fila = resultado.iloc[0]
            total_cajas = int(fila['cajas_totales'])
            unidades_por_caja = int(fila['cantidad_por_caja'])
            total_unidades_lote = total_cajas * unidades_por_caja
            partes_codigo = codigo_actual.split('-')
            num_caja_esc = int(partes_codigo[-1]) if partes_codigo[-1].isdigit() else 1
            if num_caja_esc > total_cajas:
                st.markdown('<div style="border: 3px solid #e74c3c; padding: 25px; border-radius: 10px; background-color: #222222; font-family: Arial, sans-serif; margin-top: 20px; text-align: center;"><h2 style="color: #e74c3c; margin-top: 0; font-weight: bold;">❌ CODIGO NO ENCONTRADO</h2><hr style="border-top: 1px solid #444; margin: 10px 0;"><p style="color: #ffffff; font-size: 16px; margin-bottom: 0;">Intente escanear la etiqueta de la caja nuevamente o verifique que esté registrada en la base de datos.</p></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="border: 3px solid #2ecc71; padding: 25px; border-radius: 10px; background-color: #222222; font-family: Arial, sans-serif; margin-top: 20px;"><h2 style="color: #2ecc71; margin-top: 0;">✅ CAJA VERIFICADA: {codigo_actual}</h2><hr style="border-top: 1px solid #444; margin: 10px 0;"><p style="color: #ffffff; font-size: 16px;"><b>Referencia:</b> {fila["referencia_licor"]}</p><p style="color: #ffffff; font-size: 16px;"><b>Cantidad en esta caja:</b> {unidades_por_caja} Unidades</p><p style="color: #ffffff; font-size: 16px;"><b>Lote Completo:</b> {total_cajas} Cajas ({total_unidades_lote} Unidades Totales)</p><p style="color: #ffffff; font-size: 16px;"><b>Responsable:</b> {fila["operario_conteo"]}</p><p style="color: #aaaaaa; font-size: 14px; font-style: italic;"><b>Novedades:</b> {fila["detalles_producto"]}</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="border: 3px solid #e74c3c; padding: 25px; border-radius: 10px; background-color: #222222; font-family: Arial, sans-serif; margin-top: 20px; text-align: center;"><h2 style="color: #e74c3c; margin-top: 0; font-weight: bold;">❌ CODIGO NO ENCONTRADO</h2><hr style="border-top: 1px solid #444; margin: 10px 0;"><p style="color: #ffffff; font-size: 16px; margin-bottom: 0;">Intente escanear la etiqueta de la caja nuevamente o verifique que esté registrada en la base de datos.</p></div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f'⚠️ Error al procesar la base de datos: {e}')
