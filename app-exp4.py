# --- Streamlit App Experiment 4 (Correlation Judgement with Multi-Shape) ---
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
worksheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g").worksheet("Eksperimen_4")

# --- Settings ---
SHAPE_FOLDER = "Shapes-All"

# --- Load shapes ---
def load_shapes():
    shapes = []
    for fname in os.listdir(SHAPE_FOLDER):
        if fname.endswith(".png"):
            shapes.append(os.path.join(SHAPE_FOLDER, fname))
    return shapes

SHAPE_POOL = load_shapes()

if len(SHAPE_POOL) < 10:
    st.error("❌ Tidak cukup bentuk tersedia.")
    st.stop()

# --- Session Init ---
if "task_index" not in st.session_state:
    st.session_state.task_index = 1
    st.session_state.total_tasks = 54
    st.session_state.responses = []

index = st.session_state.task_index
st.title("📊 Eksperimen 4: Berdasarkan Bentuk")
st.subheader(f"Eksperimen #{index}")

# --- Generate scatterplot ---
def generate_data(n_categories=3, target_corr=0.8, other_corr=0.2):
    shapes = random.sample(SHAPE_POOL, n_categories)
    x1, y1, x2, y2 = [], [], [], []
    for shape in shapes:
        # high correlation data (plot A)
        x = np.random.uniform(0, 1.5, 20)
        noise = np.random.normal(0, (1 - target_corr) * 0.2, 20)
        y = x + noise
        x1.append(x)
        y1.append(y)

        # low correlation data (plot B)
        x_b = np.random.uniform(0, 1.5, 20)
        noise_b = np.random.normal(0, (1 - other_corr) * 0.6, 20)
        y_b = x_b + noise_b
        x2.append(x_b)
        y2.append(y_b)

    return shapes, (x1, y1), (x2, y2)

# --- Init question ---
if f"shapes_{index}" not in st.session_state:
    N = random.randint(2, 5)
    shapes, (x1, y1), (x2, y2) = generate_data(n_categories=N)
    st.session_state[f"shapes_{index}"] = shapes
    st.session_state[f"x1_{index}"] = x1
    st.session_state[f"y1_{index}"] = y1
    st.session_state[f"x2_{index}"] = x2
    st.session_state[f"y2_{index}"] = y2

shapes = st.session_state[f"shapes_{index}"]
x1 = st.session_state[f"x1_{index}"]
y1 = st.session_state[f"y1_{index}"]
x2 = st.session_state[f"x2_{index}"]
y2 = st.session_state[f"y2_{index}"]

# --- Scatterplot A ---
fig, axs = plt.subplots(1, 2, figsize=(8, 4))
for i, shape in enumerate(shapes):
    img = Image.open(shape).convert("RGBA").resize((15, 15))
    im = OffsetImage(img, zoom=1.0)
    for x, y in zip(x1[i], y1[i]):
        ab = AnnotationBbox(im, (x, y), frameon=False)
        axs[0].add_artist(ab)
    axs[0].scatter([], [], label=f"Kategori {i+1}")

    for x, y in zip(x2[i], y2[i]):
        ab = AnnotationBbox(im, (x, y), frameon=False)
        axs[1].add_artist(ab)
    axs[1].scatter([], [], label=f"Kategori {i+1}")

for ax, title in zip(axs, ["Plot A", "Plot B"]):
    ax.set_xlim(-0.1, 1.6)
    ax.set_ylim(-0.1, 1.6)
    ax.set_title(title)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

st.pyplot(fig)

# --- Input Jawaban ---
st.markdown("""
💡 **Pilih plot dengan korelasi lebih tinggi:**
""")
choice = st.radio("", ["A", "B"])

# --- Submit ---
if st.button("🚀 Submit"):
    correct = (choice == "A")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [timestamp, index, len(shapes), choice, "Benar" if correct else "Salah", ", ".join([os.path.basename(s) for s in shapes])]
    try:
        worksheet.append_row(row)
        st.success("✅ Jawaban berhasil disimpan.")
    except Exception as e:
        st.warning(f"Gagal menyimpan ke Google Sheets: {e}")

    st.session_state.task_index += 1
    st.rerun()

# --- Final ---
if st.session_state.task_index > st.session_state.total_tasks:
    st.balloons()
    st.success("🎉 Eksperimen selesai!")
    st.stop()
