# --- Streamlit App for Experiment 1: Estimation Based on Shape Types ---
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
sheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g").worksheet("Eksperimen_1")

# --- Shape Mapping ---
SHAPE_TYPE_MAP = {
    "circle": "filled", "circle-unfilled": "unfilled", "circle-filled": "filled", "dot": "filled",
    "square": "filled", "square-unfilled": "unfilled", "square-x-open": "open", "square-filled": "filled",
    "triangle-filled": "filled", "triangle-unfilled": "unfilled", "triangle-downward-unfilled": "unfilled",
    "triangle-left-unfilled": "unfilled", "triangle-right-unfilled": "unfilled",
    "star-filled": "filled", "star-unfilled": "unfilled", "sixlinestar-open": "open", "eightline-star-open": "open",
    "plus-filled": "filled", "plus-unfilled": "unfilled", "plus-open": "open",
    "cross-open": "open", "diamond": "filled", "diamond-filled": "filled", "diamond-unfilled": "unfilled",
    "diamond-plus-open": "open", "y": "filled", "y-filled": "filled", "minus-open": "open",
    "arrow-vertical-open": "open", "arrow-horizontal-open": "open",
}

LABEL_MAP = {k: k for k in SHAPE_TYPE_MAP}

ROOT_FOLDERS = ["Shapes-D3", "Shapes-Excel", "Shapes-Tableau", "Shapes-Matlab", "Shapes-R"]

# --- Utility to collect shapes ---
def collect_unique_shapes():
    shape_dict = {}
    for folder in ROOT_FOLDERS:
        if not os.path.exists(folder):
            continue
        for fname in os.listdir(folder):
            if fname.endswith(".png"):
                raw = os.path.splitext(fname)[0]
                if raw in SHAPE_TYPE_MAP and raw not in shape_dict:
                    shape_dict[raw] = os.path.join(folder, fname)
    return list(shape_dict.values())

SHAPE_POOL = collect_unique_shapes()

# --- Initialize session state ---
if "task_index" not in st.session_state:
    st.session_state.task_index = 0
    st.session_state.correct = 0
    st.session_state.total_tasks = 53

index = st.session_state.task_index
mode = "latihan" if index < 3 else "eksperimen"

st.title("🧠 Experiment 1: Estimating Based on Shape")
st.subheader(f"{'🔍 Training' if mode == 'latihan' else '📊 Experiment'} #{index + 1 if mode == 'latihan' else index - 2 + 1}")

# --- Generate task ---
if f"x_data_{index}" not in st.session_state:
    shape_counts = {"filled": 0, "unfilled": 0, "open": 0}
    for s in SHAPE_POOL:
        label = os.path.splitext(os.path.basename(s))[0]
        t = SHAPE_TYPE_MAP.get(label)
        if t: shape_counts[t] += 1

    valid_types = [t for t, c in shape_counts.items() if c >= 3]
    if len(valid_types) < 1:
        st.error("❌ Not enough shape types for experiment.")
        st.stop()

    selected_types = random.sample(valid_types, random.randint(1, min(3, len(valid_types))))
    valid_shapes = [s for s in SHAPE_POOL if SHAPE_TYPE_MAP.get(os.path.splitext(os.path.basename(s))[0]) in selected_types]
    if len(valid_shapes) < 3:
        st.error("❌ Not enough valid shapes to continue.")
        st.stop()

    N = random.randint(2, min(10, len(valid_shapes)))
    chosen_shapes = random.sample(valid_shapes, N)
    means = np.random.uniform(0.3, 1.0, N)
    y_data = [np.random.normal(loc=m, scale=0.05, size=20) for m in means]
    x_data = [np.random.uniform(0.0, 1.5, 20) for _ in range(N)]
    target_idx = int(np.argmax([np.mean(y) for y in y_data]))

    shape_labels = [LABEL_MAP[os.path.splitext(os.path.basename(s))[0]] for s in chosen_shapes]

    st.session_state[f"x_data_{index}"] = x_data
    st.session_state[f"y_data_{index}"] = y_data
    st.session_state[f"chosen_shapes_{index}"] = chosen_shapes
    st.session_state[f"shape_labels_{index}"] = shape_labels
    st.session_state[f"target_idx_{index}"] = target_idx

# --- Load state ---
x_data = st.session_state[f"x_data_{index}"]
y_data = st.session_state[f"y_data_{index}"]
chosen_shapes = st.session_state[f"chosen_shapes_{index}"]
shape_labels = st.session_state[f"shape_labels_{index}"]
target_idx = st.session_state[f"target_idx_{index}"]

# --- Visualize ---
fig, ax = plt.subplots()
for i in range(len(chosen_shapes)):
    img = Image.open(chosen_shapes[i]).convert("RGBA").resize((20, 20))
    im = OffsetImage(img, zoom=1.0)
    for x, y in zip(x_data[i], y_data[i]):
        ab = AnnotationBbox(im, (x, y), frameon=False)
        ax.add_artist(ab)
    ax.scatter([], [], label=f"Category {i+1} ({shape_labels[i]})")

ax.set_xlim(-0.1, 1.6)
ax.set_ylim(-0.1, 1.6)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.legend()
st.pyplot(fig)

# --- User Input ---
selected_label = st.selectbox("📍 Select the category with the highest Y mean:",
                              [f"Category {i+1} ({label})" for i, label in enumerate(shape_labels)])
selected_index = int(selected_label.split()[1]) - 1

# --- Submit ---
if st.button("🚀 Submit Answer"):
    correct = selected_index == target_idx
    if correct:
        st.session_state.correct += 1
        st.success("✅ Correct answer!")
    else:
        st.error(f"❌ Incorrect. Correct answer was Category {target_idx+1} ({shape_labels[target_idx]})")

    if mode == "latihan" and not correct:
        st.warning("⚠️ You must answer correctly to continue training.")
        st.stop()

    if mode == "eksperimen":
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        shape_types_used = "+".join(sorted(set(SHAPE_TYPE_MAP.get(os.path.splitext(os.path.basename(s))[0], '') for s in chosen_shapes)))
        row = [timestamp, index - 2 + 1, len(chosen_shapes), shape_types_used,
               shape_labels[selected_index], shape_labels[target_idx], "Benar" if correct else "Salah",
               ", ".join([os.path.basename(f) for f in chosen_shapes])]
        try:
            sheet.append_row(row)
        except Exception as e:
            st.warning(f"Failed to save to sheet: {e}")

    st.session_state.task_index += 1
    st.rerun()

# --- End ---
if st.session_state.task_index == st.session_state.total_tasks:
    st.success(f"🎉 Experiment complete! Final score: {st.session_state.correct} out of 50.")
    st.balloons()
    st.stop()
