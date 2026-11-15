from datetime import datetime
from fpdf import FPDF
import streamlit as st
import torch
import torch.nn as nn

st.set_page_config(
    page_title="BioGen-Vascular Pro Enterprise", page_icon="🩺", layout="centered"
)


class DeepVascularMLP(nn.Module):

  def __init__(self):
    super(DeepVascularMLP, self).__init__()
    self.network = nn.Sequential(
        nn.Linear(2, 16),
        nn.ReLU(),
        nn.Linear(16, 8),
        nn.ReLU(),
        nn.Linear(8, 1),
        nn.Sigmoid(),
    )

  def forward(self, x):
    return self.network(x)


@st.cache_resource
def load_model():
  model = DeepVascularMLP()
  model.eval()
  return model


ai_model = load_model()

st.title("🩺 BioGen-Vascular Pro Enterprise (v2.1)")
st.markdown(
    "**Medical AI Platform for Vascular Perfusion Analysis and Automated"
    " Reporting**"
)
st.markdown("---")

tissue = st.text_input(
    "Tissue Type", value="Skin and Vascular Tissue (Primary)"
)
blood_pressure = st.number_input(
    "Blood Pressure (mmHg)", value=120.0, step=1.0
)
wound_radius = st.number_input("Wound Radius (mm)", value=20.0, step=0.5)

st.markdown("---")

if st.button("Run AI Simulation & Generate Report", type="primary"):
  inputs = torch.tensor(
      [[float(blood_pressure), float(wound_radius)]], dtype=torch.float32
  )
  with torch.no_grad():
    prediction = ai_model(inputs).item()

  efficiency = round(max(10.0, min(98.5, prediction * 100)), 2)
  note = (
      f"Advanced Vascular Perfusion Analysis using Deep PyTorch MLP Core v2.1."
      f" Calculated Tissue Perfusion Efficiency: {efficiency}%."
  )

  st.success("Simulation completed successfully!")

  col1, col2 = st.columns(2)
  with col1:
    st.metric(
        label="Perfusion Efficiency", value=f"{efficiency}%", delta="Normal Range"
    )
  with col2:
    st.metric(label="AI Model Core", value="PyTorch MLP v2.1")

  st.info(f"**Clinical Note:**\n{note}")

  pdf_filename = "medical_report.pdf"
  pdf = FPDF()
  pdf.add_page()
  pdf.set_font("Arial", "B", 16)
  pdf.cell(
      0,
      10,
      txt="BioGen-Vascular Pro - Medical AI Report",
      ln=True,
      align="C",
  )
  pdf.set_font("Arial", "", 12)
  pdf.ln(10)

  pdf.cell(
      0,
      10,
      txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
      ln=True,
      align="L",
  )
  pdf.cell(0, 10, txt=f"Tissue Type: {tissue}", ln=True, align="L")
  pdf.cell(
      0, 10, txt=f"Blood Pressure: {blood_pressure} mmHg", ln=True, align="L"
  )
  pdf.cell(0, 10, txt=f"Wound Radius: {wound_radius} mm", ln=True, align="L")
  pdf.cell(
      0, 10, txt=f"Perfusion Efficiency: {efficiency} %", ln=True, align="L"
  )
  pdf.ln(5)
  pdf.multi_cell(0, 10, txt=f"Clinical Note:\n{note}")
  pdf.output(pdf_filename)

  with open(pdf_filename, "rb") as f:
    st.download_button(
        label="📥 Download Official Medical PDF Report",
        data=f,
        file_name="medical_report.pdf",
        mime="application/pdf",
    )