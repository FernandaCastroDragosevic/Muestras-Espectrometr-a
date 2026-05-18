
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

st.set_page_config(layout="wide")
st.title("📋 Ingreso de Muestras")

archivo = "datos_muestras.xlsx"

# 🔹 INICIALIZAR VARIABLES
if "from_val" not in st.session_state:
    st.session_state.from_val = 0
if "to_val" not in st.session_state:
    st.session_state.to_val = 2
if "contador" not in st.session_state:
    st.session_state.contador = 0
if "tipo" not in st.session_state:
    st.session_state.tipo = "Matriz"
if "sample_id" not in st.session_state:
    st.session_state.sample_id = "SAMPLE_0001"
if "comentarios_key" not in st.session_state:
    st.session_state.comentarios_key = "comentarios_0"
if "sin_coincidencias_key" not in st.session_state:
    st.session_state.sin_coincidencias_key = "sin_0"
if "confirmar_reset" not in st.session_state:
    st.session_state.confirmar_reset = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

# 🔹 FORMULARIO
with st.form("formulario"):

    st.subheader("Datos principales")

    hole_id = st.text_input("Hole ID")

    # ✅ NUEVO CAMPO USUARIO
    usuario = st.text_input("Usuario", value=st.session_state.usuario)

    col1, col2 = st.columns(2)
    with col1:
        from_val = st.number_input("From", value=st.session_state.from_val)
    with col2:
        to_val = st.number_input("To", value=st.session_state.to_val)

    tipo = st.selectbox(
        "Tipo",
        ["Matriz", "Fractura", "Ocurrencias Especiales"],
        index=0 if st.session_state.tipo == "Matriz"
        else 1 if st.session_state.tipo == "Fractura"
        else 2
    )

    sin_coincidencias = st.checkbox(
        "⚠️ Sin Coincidencias - Repetir Muestra",
        key=st.session_state.sin_coincidencias_key
    )

    st.subheader("Información adicional")

    sample_id = st.text_input("Sample ID", value=st.session_state.sample_id)
    comentarios = st.text_area("Comentarios", key=st.session_state.comentarios_key)

    st.markdown("---")

    colA, colB, colC = st.columns(3)

    submit = colA.form_submit_button("✅ INGRESAR")
    reset = colB.form_submit_button("🔄 RESET")
    eliminar = colC.form_submit_button("🧹 ELIMINAR ÚLTIMA")


# 🔹 VALIDACIÓN
def validar():
    if hole_id.strip() == "":
        st.error("Debe ingresar Hole ID ❌")
        return False
    if usuario.strip() == "":
        st.error("Debe ingresar Usuario ❌")
        return False
    if sample_id.strip() == "":
        st.error("Debe ingresar Sample ID ❌")
        return False
    if tipo == "Ocurrencias Especiales" and comentarios.strip() == "":
        st.error("Debe agregar detalle en comentarios ⚠️ ❌")
        return False
    return True


# 🔹 GUARDAR
if submit:

    if validar():

        # ✅ guardar usuario en sesión (para persistencia)
        st.session_state.usuario = usuario

        nueva = {
            "Hole ID": hole_id,
            "Usuario": usuario,
            "From": from_val,
            "To": to_val,
            "Tipo": tipo,
            "Sin coincidencias": sin_coincidencias,
            "Comentarios": comentarios,
            "Sample ID": sample_id
        }

        if os.path.exists(archivo):
            df = pd.read_excel(archivo)
            df = pd.concat([df, pd.DataFrame([nueva])], ignore_index=True)
        else:
            df = pd.DataFrame([nueva])

        df.to_excel(archivo, index=False)
        st.success("✔️ Muestra guardada")

        # 🔹 LÓGICA AVANCE
        if sin_coincidencias:
            st.session_state.tipo = tipo

        elif tipo in ["Matriz", "Fractura"]:
            st.session_state.contador += 1

            if st.session_state.contador == 2:
                st.session_state.from_val = to_val
                st.session_state.to_val = to_val + 2
                st.session_state.contador = 0

            st.session_state.tipo = "Fractura" if tipo == "Matriz" else "Matriz"

        else:
            st.session_state.tipo = "Ocurrencias Especiales"

        # 🔹 SAMPLE ID
        try:
            base = sample_id[:-4]
            num = int(sample_id[-4:])
            st.session_state.sample_id = f"{base}{num+1:04d}"
        except:
            pass

        # 🔹 RESET INPUTS
        st.session_state.comentarios_key = f"comentarios_{datetime.now().timestamp()}"
        st.session_state.sin_coincidencias_key = f"sin_{datetime.now().timestamp()}"

        st.rerun()


# 🔹 RESET
if reset:
    st.session_state.from_val = 0
    st.session_state.to_val = 2
    st.session_state.tipo = "Matriz"
    st.session_state.sample_id = "SAMPLE_0001"
    st.session_state.contador = 0
    st.session_state.usuario = ""
    st.session_state.comentarios_key = f"comentarios_{datetime.now().timestamp()}"
    st.session_state.sin_coincidencias_key = f"sin_{datetime.now().timestamp()}"
    st.rerun()


# 🔹 ELIMINAR ÚLTIMA
if eliminar:
    if os.path.exists(archivo):
        df = pd.read_excel(archivo)
        if len(df) > 0:
            df = df.iloc[:-1]
            df.to_excel(archivo, index=False)
            st.success("Última muestra eliminada ✅")
            st.rerun()


# 🔹 TABLA + EXPORTAR
if os.path.exists(archivo):

    df = pd.read_excel(archivo)

    st.markdown("---")
    st.subheader("📊 Datos del día")

    st.dataframe(df, use_container_width=True)

    fecha = datetime.now().strftime("%Y-%m-%d")

    output = BytesIO()
    df.to_excel(output, index=False)

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "⬇️ Descargar base del día",
            data=output.getvalue(),
            file_name=f"muestras_{fecha}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col2:
        if st.button("🆕 Empezar nueva base"):
            st.session_state.confirmar_reset = True

    if st.session_state.confirmar_reset:

        st.warning("⚠️ ¿Seguro que ya exportaste la base de datos?")

        colA, colB = st.columns(2)

        with colA:
            if st.button("❌ No, cancelar"):
                st.session_state.confirmar_reset = False

        with colB:
            if st.button("✅ Sí, ya la exporté"):

                if os.path.exists(archivo):
                    os.remove(archivo)

                st.success("✅ Nueva base iniciada")
                st.session_state.confirmar_reset = False
                st.rerun()

