import streamlit as st
import pandas as pd
import os
from PIL import Image

ruta_logo = 'pequeño.png'
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
    with col2: st.image(Image.open(ruta_logo), width=150)

st.title('SISTEMA CONTROL DE INVENTARIOS PRINDEL')
with st.expander('➕ Registrar Nuevo Producto en el Inventario'):
    with st.form('form_nuevo_producto', clear_on_submit=True):
        new_id = st.text_input('ID de la Caja (Ej: L-001)')
        new_ref = st.text_input('Referencia del Licor')
        col_c1, col_c2 = st.columns(2)
        with col_c1: new_cajas = st.number_input('Total de Cajas', min_value=1, value=1, step=1)
        with col_c2: new_cant = st.number_input('Cantidad por Caja', min_value=1, value=12, step=1)
        new_operario = st.text_input('Operario de Conteo')
        new_detalles = st.text_area('Detalles / Novedades', value='Ninguna')
        btn_guardar = st.form_submit_button('💾 Guardar Producto')

        if btn_guardar:
            if new_id.strip() == '' or new_ref.strip() == '':
                st.error('❌ El ID de la Caja y la Referencia son obligatorios.')
            else:
                nuevo_registro = pd.DataFrame([{
                    'id_caja': new_id.strip(),
                    'referencia_licor': new_ref.strip(),
                    'cajas_totales': int(new_cajas),
                    'cantidad_por_caja': int(new_cant),
                    'operario_conteo': new_operario.strip(),
                    'detalles_producto': new_detalles.strip()
                }])
                try:
                    nuevo_registro.to_csv('inventario_licores.csv', mode='a', sep='|', index=False, header=not os.path.exists('inventario_licores.csv'), encoding='latin-1')
                    st.success('✅ ¡Producto guardado exitosamente en la base de datos!')
                except Exception as e:
                    st.error(f'❌ Error al guardar el archivo: {e}')

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
                st.markdown('<div style="border: 3px solid #e74c3c; padding: 25px; border-radius: 10px; background-color: #222222; font-family: Arial, sans-serif; margin-top: 20px; text-align: center;"><h2 style="color: #e74c3c; margin-top: 0; font-weight: bold;">CODIGO NO ENCONTRADO</h2><hr style="border-top: 1px solid #444; margin: 10px 0;"><p style="color: #ffffff; font-size: 16px; margin-bottom: 0;">Intente escanear la etiqueta de la caja nuevamente o verifique que esté registrada en la base de datos.</p></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="border: 3px solid #2ecc71; padding: 25px; border-radius: 10px; background-color: #222222; font-family: Arial, sans-serif; margin-top: 20px;"><h2 style="color: #2ecc71; margin-top: 0;">CAJA VERIFICADA: {codigo_actual}</h2><hr style="border-top: 1px solid #444; margin: 10px 0;"><p style="color: #ffffff; font-size: 16px;"><b>Referencia:</b> {fila["referencia_licor"]}</p><p style="color: #ffffff; font-size: 16px;"><b>Cantidad en esta caja:</b> {unidades_por_caja} Unidades</p><p style="color: #ffffff; font-size: 16px;"><b>Lote Completo:</b> {total_cajas} Cajas ({total_unidades_lote} Unidades Totales)</p><p style="color: #ffffff; font-size: 16px;"><b>Responsable:</b> {fila["operario_conteo"]}</p><p style="color: #aaaaaa; font-size: 14px; font-style: italic;"><b>Observación:</b> {fila["detalles_producto"]}</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="border: 3px solid #e74c3c; padding: 25px; border-radius: 10px; background-color: #222222; font-family: Arial, sans-serif; margin-top: 20px; text-align: center;"><h2 style="color: #e74c3c; margin-top: 0; font-weight: bold;">CODIGO NO ENCONTRADO</h2><hr style="border-top: 1px solid #444; margin: 10px 0;"><p style="color: #ffffff; font-size: 16px; margin-bottom: 0;">Intente escanear la etiqueta de la caja nuevamente o verifique que esté registrada en la base de datos.</p></div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f'⚠️ Error al procesar la base de datos: {e}')
