import streamlit as st
import pandas as pd
import datetime
import io
from fpdf import FPDF
from PIL import Image

# ---- CONFIGURACIÓN INICIAL ----
st.set_page_config(page_title="Calculadora de Créditos Hipotecarios - Argentina", layout="centered")
st.title("🏠 Calculadora de Créditos Hipotecarios")

# ---- CARGA DE LOGO ----
logo_path = "LOGO BARRIO (1).png"
try:
    logo = Image.open(logo_path)
    st.image(logo, use_column_width=True)
except:
    st.warning("⚠️ No se pudo cargar el logo. Asegurate de que el archivo esté en el mismo directorio que el script.")

# ---- DATOS DEL CLIENTE ----
st.subheader("Datos del cliente")
cliente = st.text_input("Nombre del cliente")
asesor = st.text_input("Nombre del asesor")
proyecto = st.text_input("Nombre del proyecto")
fecha = st.date_input("Fecha", value=datetime.date.today())

# ---- PARÁMETROS DEL CRÉDITO ----
st.subheader("Parámetros del crédito")
monto_total = st.number_input("Monto total de la propiedad ($)", min_value=0)
anticipo = st.slider("Anticipo (%)", 0, 100, 20)
plazo_meses = st.slider("Plazo del crédito (meses)", 1, 360, 240)
tipo_ingreso = st.selectbox("Tipo de ingreso", ["Empleado público", "Empleado privado", "Monotributista", "Responsable inscripto"])
tipo_credito_preferido = st.selectbox("Preferencia de tipo de crédito", ["Tasa fija", "UVA", "Mixto"])

# ---- VALIDACIÓN DE ANTICIPO ----
anticipo_monto = monto_total * (anticipo / 100)
saldo_credito = monto_total - anticipo_monto
if anticipo == 100:
    st.warning("⚠️ El anticipo cubre el 100% del valor. No hay monto a financiar.")

# ---- VALIDACIÓN DE CRÉDITO ----
st.subheader("Validación de crédito personalizada")
usar_tasa_sugerida = st.checkbox("Usar tasa sugerida por tipo de crédito", value=True)

if usar_tasa_sugerida:
    tasa_dict = {"UVA": 3.5, "Fija": 9.0, "Mixta": 6.5}
    tasa_anual = tasa_dict.get(tipo_credito_preferido, 7.0)
else:
    tasa_anual = st.number_input("Ingresá la tasa anual (%)", min_value=0.0, value=7.0, step=0.1)

if st.button("Validar crédito"):
    cuota_estim = (saldo_credito * (1 + (tasa_anual / 100) * (plazo_meses / 12))) / plazo_meses
    st.success(f"✅ Cuota estimada con tasa del {tasa_anual:.2f}%: ${cuota_estim:,.2f}")

# ---- DATOS DE CRÉDITOS DISPONIBLES ----
creditos = pd.DataFrame({
    "Banco": ["Banco Nación", "Banco Provincia", "Banco Ciudad"],
    "Tipo": ["UVA", "Fija", "Mixta"],
    "Tasa Anual (%)": [3.5, 9.0, 6.5],
    "Plazo máximo (años)": [30, 20, 25]
})

creditos["Monto financiado"] = saldo_credito
creditos["Cuota estimada ($)"] = (saldo_credito * (1 + (creditos["Tasa Anual (%)"] / 100) * (plazo_meses / 12))) / plazo_meses

# ---- RESULTADOS ----
st.subheader("Comparación de Créditos")
mejor_opcion = creditos.sort_values(by="Cuota estimada ($)").iloc[0]
st.success(f"💡 La mejor opción es: {mejor_opcion['Banco']} ({mejor_opcion['Tipo']}) con una cuota estimada de ${mejor_opcion['Cuota estimada ($)']:.2f}")

st.dataframe(creditos.sort_values(by="Cuota estimada ($)"))

# ---- GRÁFICO COMPARATIVO ----
st.subheader("Gráfico de comparación de cuotas")
st.bar_chart(creditos.set_index("Banco")["Cuota estimada ($)"])

# ---- GENERAR PDF ----
def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    try:
        pdf.image(logo_path, x=10, y=8, w=60)
    except:
        pass
    pdf.ln(30)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="INFORME COMPARATIVO DE CRÉDITOS HIPOTECARIOS", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Cliente: {cliente} | Asesor: {asesor}", ln=True)
    pdf.cell(200, 10, txt=f"Proyecto: {proyecto} | Fecha: {fecha.strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(10)
    for i, row in creditos.iterrows():
        cuota_txt = f"Banco: {row['Banco']} | Tipo: {row['Tipo']} | Cuota estimada: ${row['Cuota estimada ($)']:.2f}"
        pdf.cell(200, 10, txt=cuota_txt, ln=True)
    return pdf.output(dest='S').encode('latin1')

if st.button("📄 Descargar informe en PDF"):
    pdf_data = generar_pdf()
    st.download_button("Descargar PDF", data=pdf_data, file_name="informe_credito.pdf", mime="application/pdf")
