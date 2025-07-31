import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date

# ---- CONFIGURACIÓN INICIAL ----
st.set_page_config(page_title="Calculadora de Créditos Hipotecarios - Argentina", layout="centered")
st.title("🏠 Calculadora de Créditos Hipotecarios")

# ---- DATOS DEL CLIENTE ----
st.subheader("Datos del cliente")
cliente = st.text_input("Nombre del cliente")
asesor = st.text_input("Nombre del asesor")
proyecto = st.text_input("Nombre del proyecto")
fecha = st.date_input("Fecha", value=date.today())

# ---- PARÁMETROS DEL CRÉDITO ----
st.subheader("Parámetros del crédito")
monto_total = st.number_input("Monto total de la propiedad ($)", min_value=0)
anticipo = st.slider("Anticipo (%)", 0, 100, 20)
plazo_anos = st.slider("Plazo del crédito (años)", 5, 30, 20)
tipo_ingreso = st.selectbox("Tipo de ingreso", ["Empleado público", "Empleado privado", "Monotributista", "Responsable inscripto"])
tipo_credito_preferido = st.selectbox("Preferencia de tipo de crédito", ["Tasa fija", "UVA", "Mixto"])

# ---- DATOS DE CRÉDITOS DISPONIBLES ----
creditos = pd.DataFrame({
    "Banco": ["Banco Nación", "Banco Provincia", "Banco Ciudad"],
    "Tipo": ["UVA", "Fija", "Mixta"],
    "Tasa Anual (%)": [3.5, 9.0, 6.5],
    "Plazo máximo (años)": [30, 20, 25]
})

# ---- CÁLCULOS ----
anticipo_monto = monto_total * (anticipo / 100)
saldo_credito = monto_total - anticipo_monto
cuotas_anuales = plazo_anos * 12

creditos["Monto financiado"] = saldo_credito
creditos["Cuota estimada ($)"] = (saldo_credito * (1 + (creditos["Tasa Anual (%)"] / 100) * plazo_anos)) / cuotas_anuales

# ---- RESULTADOS ----
st.subheader("Comparación de Créditos")
st.dataframe(creditos.sort_values(by="Cuota estimada ($)"))

# ---- GENERAR PDF ----
def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe Comparativo de Créditos Hipotecarios", ln=1, align="C")
    pdf.cell(200, 10, txt=f"Cliente: {cliente} | Asesor: {asesor} | Proyecto: {proyecto}", ln=2)
    pdf.cell(200, 10, txt=f"Fecha: {fecha.strftime('%d/%m/%Y')}", ln=3)
    pdf.ln(10)
    for i, row in creditos.iterrows():
        pdf.cell(200, 10, txt=f"Banco: {row['Banco']} | Tipo: {row['Tipo']} | Cuota: ${row['Cuota estimada ($)']:.2f}", ln=1)
    return pdf

if st.button("📄 Descargar informe PDF"):
    pdf = generar_pdf()
    pdf.output("informe_credito.pdf")
    with open("informe_credito.pdf", "rb") as f:
        st.download_button("Descargar PDF", data=f, file_name="informe_credito.pdf")
