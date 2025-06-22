# --- Streamlit App for Experiment 4 (Final Freeze + Garis Bantu + Multi-Shape per Plot) ---
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

st.title("🔍 Berdasarkan Bentuk")
st.subheader(f"Eksperimen #{st.session_state.step + 1} dari 54")

# --- Function to generate one plot ---
def generate_plot(is_high_corr, shape_paths):
    fig, ax = plt.subplots()
    for shape_path in shape_paths:
        mean = np.random.uniform(0.3, 1.2, 2)
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
    ax.axhline(0.8, color="gray", linestyle="--", linewidth=0.5)
    ax.axvline(0.8, color="gray", linestyle="--", linewidth=0.5)
    return fig, shape_paths

# --- Generate and store state if not exists ---
if f"plot_data_{st.session_state.step}" not in st.session_state:
    plotA_shapes = random.sample(SHAPES, random.randint(2, 4))
    plotB_shapes = random.sample(SHAPES, random.randint(2, 4))
    high_corr_plot = random.choice(["A", "B"])

    st.session_state[f"plot_data_{st.session_state.step}"] = {
        "plotA_shapes": plotA_shapes,
        "plotB_shapes": plotB_shapes,
        "high_corr_plot": high_corr_plot
    }

plot_data = st.session_state[f"plot_data_{st.session_state.step}"]
plotA_shapes = plot_data["plotA_shapes"]
plotB_shapes = plot_data["plotB_shapes"]
high_corr_plot = plot_data["high_corr_plot"]

figA, used_shapes_A = generate_plot(is_high_corr=(high_corr_plot == "A"), shape_paths=plotA_shapes)
figB, used_shapes_B = generate_plot(is_high_corr=(high_corr_plot == "B"), shape_paths=plotB_shapes)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Plot A**")
    st.pyplot(figA)
with col2:
    st.markdown("**Plot B**")
    st.pyplot(figB)

choice = st.radio("💡 Menurut Anda, plot mana yang lebih berkorelasi?", ["A", "B"], index=None)

if st.button("🚀 Submit Jawaban"):
    if choice:
        benar = choice == high_corr_plot
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [
            timestamp,
            st.session_state.step + 1,
            choice,
            high_corr_plot,
            "Benar" if benar else "Salah",
            ", ".join([os.path.splitext(os.path.basename(p))[0] for p in used_shapes_A]),
            ", ".join([os.path.splitext(os.path.basename(p))[0] for p in used_shapes_B]),
            len(used_shapes_A)
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
    st.stop()
