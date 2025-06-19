# --- Streamlit App Experiment 1 (Final Repro ShapeItUp) ---
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
worksheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g").worksheet("Eksperimen_1")

# --- Folder sumber ---
ROOT_FOLDERS = ["Shapes-D3", "Shapes-Excel", "Shapes-Tableau", "Shapes-Matlab", "Shapes-R"]

# --- Mapping label visual ---
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
    "y": "y", "y-filled": "y",
    "minus-open": "minus", "min": "minus",
    "arrow-vertical-open": "arrow", "arrow-horizontal-open": "arrow",
    "hexagon": "hexagon", "pentagon": "pentagon", "triangle-right": "triangle", "triangle-left": "triangle"
}

# --- Mapping shape type ---
SHAPE_TYPE_MAP = {
    "circle": "filled", "circle-unfilled": "unfilled", "circle-filled": "filled", "dot": "filled",
    "square-filled": "filled", "square-unfilled": "unfilled", "square-x-open": "open",
    "triangle-filled": "filled", "triangle-unfilled": "unfilled", "downward-triangle-unfilled": "unfilled",
    "triangle-left-unfilled": "unfilled", "triangle-right-unfilled": "unfilled",
    "star-filled": "filled", "star-unfilled": "unfilled", "sixlinestar-open": "open", "eightline-star-open": "open",
    "plus-filled": "filled", "plus-unfilled": "unfilled", "plus-open": "open",
    "cross-open": "open",
    "diamond-filled": "filled", "diamond-unfilled": "unfilled", "diamond-plus-open": "open",
    "y": "filled", "y-filled": "filled",
    "minus-open": "open", "min": "open",
    "arrow-vertical-open": "open", "arrow-horizontal-open": "open",
    "hexagon": "filled", "pentagon": "filled"
}

SHAPE_TYPE_COMBOS = [
    ["filled"], ["unfilled"], ["open"],
    ["filled", "unfilled"], ["filled", "open"], ["unfilled", "open"],
    ["filled", "unfilled", "open"]
]

# --- Kumpulkan shape unik ---
def collect_unique_shapes():
    shape_dict = {}
    missing_types = set()
    for folder in ROOT_FOLDERS:
        if not os.path.exists(folder):
            continue
        for fname in os.listdir(folder):
            if fname.endswith(".png"):
                raw = os.path.splitext(fname)[0]
                label = LABEL_MAP.get(raw, raw)
                if raw not in SHAPE_TYPE_MAP:
                    missing_types.add(raw)
                if label not in shape_dict:
                    shape_dict[label] = os.path.join(folder, fname)
    if missing_types:
        st.warning(f"⚠️ Bentuk belum dikenali di SHAPE_TYPE_MAP: {', '.join(sorted(missing_types))}")
    return list(shape_dict.values())

SHAPE_POOL = collect_unique_shapes()

# --- Validasi kombinasi tipe bentuk ---
def validate_shape_combo(shapes, expected_types):
    found_types = set()
    for shape_path in shapes:
        raw = os.path.splitext(os.path.basename(shape_path))[0]
        s_type = SHAPE_TYPE_MAP.get(raw)
        if s_type:
            found_types.add(s_type)
    return set(expected_types).issubset(found_types)

# --- Inisialisasi state ---
if "task_index" not in st.session_state:
    st.session_state.task_index = 0
    st.session_state.correct = 0
    st.session_state.total_tasks = 53

index = st.session_state.task_index
mode = "latihan" if index < 3 else "eksperimen"
st.title("🧠 Eksperimen 1: Estimasi Berdasarkan Bentuk")
st.subheader(f"{'🔍 Latihan' if mode == 'latihan' else '📊 Eksperimen'} #{index + 1 if mode == 'latihan' else index - 2 + 1}")

# --- Generate soal ---
if f"x_data_{index}" not in st.session_state:
    random.shuffle(SHAPE_TYPE_COMBOS)
    combo = None
    chosen_shapes = []
    for c in SHAPE_TYPE_COMBOS:
        possible_shapes = [s for s in SHAPE_POOL if SHAPE_TYPE_MAP.get(os.path.splitext(os.path.basename(s))[0]) in c]
        if len(possible_shapes) >= 10:
            sample = random.sample(possible_shapes, random.randint(2, min(10, len(possible_shapes))))
            if validate_shape_combo(sample, c):
                combo = c
                chosen_shapes = sample
                break

    if combo is None:
        st.error("❌ Tidak ada kombinasi tipe bentuk yang valid.")
        st.stop()

    means = np.random.uniform(0.3, 1.0, len(chosen_shapes))
    y_data = [np.random.normal(loc=m, scale=0.05, size=20) for m in means]
    x_data = [np.random.uniform(0.0, 1.5, 20) for _ in range(len(chosen_shapes))]
    target_idx = int(np.argmax([np.mean(y) for y in y_data]))

    shape_labels = []
    for shape in chosen_shapes:
        raw = os.path.splitext(os.path.basename(shape))[0]
        label = LABEL_MAP.get(raw, raw)
        shape_labels.append(label)

    st.session_state[f"x_data_{index}"] = x_data
    st.session_state[f"y_data_{index}"] = y_data
    st.session_state[f"chosen_shapes_{index}"] = chosen_shapes
    st.session_state[f"shape_labels_{index}"] = shape_labels
    st.session_state[f"target_idx_{index}"] = target_idx
    st.session_state[f"shape_combo_{index}"] = "+".join(combo)

# --- Load state ---
x_data = st.session_state[f"x_data_{index}"]
y_data = st.session_state[f"y_data_{index}"]
chosen_shapes = st.session_state[f"chosen_shapes_{index}"]
shape_labels = st.session_state[f"shape_labels_{index}"]
target_idx = st.session_state[f"target_idx_{index}"]
shape_combo = st.session_state[f"shape_combo_{index}"]

# --- Visualisasi ---
fig, ax = plt.subplots()
for i in range(len(chosen_shapes)):
    img = Image.open(chosen_shapes[i]).convert("RGBA").resize((20, 20))
    im = OffsetImage(img, zoom=1.0)
    for x, y in zip(x_data[i], y_data[i]):
        ab = AnnotationBbox(im, (x, y), frameon=False)
        ax.add_artist(ab)
    ax.scatter([], [], label=f"Kategori {i+1} ({shape_labels[i]})")

ax.set_xlim(-0.1, 1.6)
ax.set_ylim(-0.1, 1.6)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.legend()
st.pyplot(fig)

# --- Input ---
selected_label = st.selectbox("📍 Pilih kategori dengan rata-rata Y tertinggi:",
                              [f"Kategori {i+1} ({label})" for i, label in enumerate(shape_labels)])
selected_index = int(selected_label.split()[1]) - 1

# --- Submit ---
if st.button("🚀 Submit Jawaban"):
    benar = selected_index == target_idx
    if benar:
        st.session_state.correct += 1
        st.success("✅ Jawaban benar!")
    else:
        st.error(f"❌ Salah. Jawaban: Kategori {target_idx+1} ({shape_labels[target_idx]})")

    if mode == "latihan" and not benar:
        st.warning("⚠️ Latihan harus benar untuk lanjut.")
        st.stop()

    if mode == "eksperimen":
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [
            timestamp,
            index - 2 + 1,
            len(chosen_shapes),
            shape_combo,
            shape_labels[selected_index],
            shape_labels[target_idx],
            "Benar" if benar else "Salah",
            ", ".join([os.path.basename(f) for f in chosen_shapes])
        ]
        try:
            worksheet.append_row(row)
        except Exception as e:
            st.warning(f"Gagal simpan ke spreadsheet: {e}")

    st.session_state.task_index += 1
    st.rerun()

# --- Akhiran ---
if st.session_state.task_index == st.session_state.total_tasks:
    st.success(f"🎉 Eksperimen selesai! Skor akhir: {st.session_state.correct} dari 50.")
    st.balloons()
    st.stop()
