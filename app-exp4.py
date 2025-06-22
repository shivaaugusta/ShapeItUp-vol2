# --- Streamlit App for Experiment 4 (Revised with Controls & Freeze) ---
import streamlit as st
import os
import random
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets Setup ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_sheets"], scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g").worksheet("Eksperimen_4")

# --- Config ---
st.set_page_config(page_title="Eksperimen 4", layout="wide")

LABEL_MAP = {
    "circle": "circle", "circle-unfilled": "circle", "circle-filled": "circle", "dot": "dot",
    "square": "square", "square-filled": "square", "square-unfilled": "square", "square-x-open": "square-x",
    "triangle": "triangle", "triangle-up": "triangle", "triangle-filled": "triangle", "triangle-unfilled": "triangle",
    "triangle-downward-unfilled": "triangle-down", "downward-triangle-unfilled": "triangle-down", "triangle-down": "triangle-down",
    "triangle-left-unfilled": "triangle-left", "triangle-right-unfilled": "triangle-right",
    "star": "star", "star-unfilled": "star", "sixlinestar-open": "star", "star-filled": "star", "eightline-star-open": "star",
    "plus-open": "plus", "plus-filled": "plus", "plus-unfilled": "plus",
    "cross-open": "cross",
    "diamond": "diamond", "diamond-filled": "diamond", "diamond-unfilled": "diamond", "diamond-plus-open": "diamond",
    "y": "y", "y-filled": "y-filled",
    "minus-open": "minus", "min": "minus",
    "arrow-vertical-open": "arrow", "arrow-horizontal-open": "arrow",
    "hexagon": "hexagon", "pentagon": "pentagon", "triangle-right": "triangle", "triangle-left": "triangle"
}

ROOT_FOLDER = "Shapes-All"
SHAPES = [os.path.join(ROOT_FOLDER, f) for f in os.listdir(ROOT_FOLDER) if f.endswith(".png")]

if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.responses = []
    st.session_state.plots = []
    st.session_state.choices = []

st.title("🔍 Berdasarkan Bentuk")
st.subheader(f"Eksperimen #{st.session_state.step + 1} dari 54")

# --- Generate data once per step ---
if len(st.session_state.plots) <= st.session_state.step:
    def generate_plot(is_high_corr, shape_paths):
        fig, ax = plt.subplots(figsize=(4, 4))
        for shape_path in shape_paths:
            mean = np.random.uniform(0.4, 1.1, 2)
            cov = [[0.02, 0.015], [0.015, 0.02]] if is_high_corr else [[0.02, 0], [0, 0.02]]
            data = np.random.multivariate_normal(mean, cov, 20)
            img = Image.open(shape_path).convert("RGBA").resize((20, 20))
            im = OffsetImage(img, zoom=1.0)
            for x, y in data:
                ab = AnnotationBbox(im, (x, y), frameon=False)
                ax.add_artist(ab)
        ax.set_xlim(0, 1.6)
        ax.set_ylim(0, 1.6)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.axhline(0.8, color='lightgray', linestyle='--', linewidth=1)
        ax.axvline(0.8, color='lightgray', linestyle='--', linewidth=1)
        return fig

    num_shapes = random.randint(2, 4)
    plotA_shapes = random.sample(SHAPES, num_shapes)
    plotB_shapes = random.sample(SHAPES, num_shapes)
    high_corr_plot = random.choice(["A", "B"])

    st.session_state.plots.append({
        "A": plotA_shapes,
        "B": plotB_shapes,
        "answer": high_corr_plot
    })

# --- Load state data ---
data = st.session_state.plots[st.session_state.step]
figA = generate_plot(is_high_corr=(data["answer"] == "A"), shape_paths=data["A"])
figB = generate_plot(is_high_corr=(data["answer"] == "B"), shape_paths=data["B"])

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Plot A**")
    st.pyplot(figA)
with col2:
    st.markdown("**Plot B**")
    st.pyplot(figB)

choice = st.radio("💡 Menurut Anda, plot mana yang lebih berkorelasi?", ["A", "B"], key=f"choice_{st.session_state.step}")

if st.button("🚀 Submit Jawaban"):
    if choice:
        benar = choice == data["answer"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [
            timestamp,
            st.session_state.step + 1,
            choice,
            data["answer"],
            "Benar" if benar else "Salah",
            ", ".join([os.path.splitext(os.path.basename(p))[0] for p in data["A"]]),
            ", ".join([os.path.splitext(os.path.basename(p))[0] for p in data["B"]]),
            len(data["A"])
        ]
        try:
            sheet.append_row(row)
        except Exception as e:
            st.warning(f"Gagal menyimpan ke Google Sheets: {e}")
        st.session_state.step += 1
        st.rerun()
    else:
        st.warning("❗ Pilih salah satu opsi terlebih dahulu.")

if st.session_state.step >= 54:
    st.success("✅ Eksperimen selesai! Terima kasih atas partisipasinya.")
    st.balloons()
    st.stop()
