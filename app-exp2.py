# --- Streamlit App Experiment 2 (Final & Clean - English Version) ---
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# --- Google Sheets Authentication ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_sheets"], scopes=scope)
client = gspread.authorize(creds)
worksheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g").worksheet("Eksperimen_2")

# --- UI Header ---
st.title("🧪 Experiment 2: Evaluating Shape Palettes in Scatterplots")
st.info("Select the category (shape) that has the highest **mean Y value**. Shapes are taken from popular visualization tool palettes.")

# --- Select Palette & Category Count ---
available_palettes = ["D3", "Tableau", "Excel", "Matlab", "R"]
selected_palette = st.selectbox("🎨 Select a shape palette:", available_palettes)
n_categories = st.selectbox("🔢 Select number of categories:", list(range(2, 11)))

# --- Load Shape Files ---
palette_path = f"Shapes-{selected_palette}"
try:
    shape_files = sorted([f for f in os.listdir(palette_path) if f.endswith(".png")])
except FileNotFoundError:
    st.error(f"Folder '{palette_path}' not found.")
    st.stop()

if len(shape_files) < n_categories:
    st.error("Not enough shapes in this palette.")
    st.stop()

# --- Trial Identity & Session State Check ---
current_key = (selected_palette, n_categories)
if (
    "selected_shapes" not in st.session_state
    or "x_data" not in st.session_state
    or "y_data" not in st.session_state
    or st.session_state.get("current_key") != current_key
):
    st.session_state.current_key = current_key
    st.session_state.selected_shapes = np.random.choice(shape_files, size=n_categories, replace=False)
    st.session_state.x_data = [np.random.uniform(0, 1.5, 20) for _ in range(n_categories)]
    st.session_state.y_data = [np.random.normal(loc=np.random.uniform(0.3, 1.2), scale=0.1, size=20) for _ in range(n_categories)]

# --- Retrieve From State ---
selected_shapes = st.session_state.selected_shapes
x_data = st.session_state.x_data
y_data = st.session_state.y_data

# --- Plot Scatterplot ---
fig, ax = plt.subplots()
for i in range(n_categories):
    shape_path = os.path.join(palette_path, selected_shapes[i])
    label_name = selected_shapes[i].replace(".png", "")
    img = Image.open(shape_path).convert("RGBA").resize((20, 20))
    im = OffsetImage(img, zoom=1.0)

    for x, y in zip(x_data[i], y_data[i]):
        ab = AnnotationBbox(im, (x, y), frameon=False)
        ax.add_artist(ab)

    ax.scatter([], [], label=f"Category {i+1} ({label_name})")

ax.set_xlim(-0.1, 1.6)
ax.set_ylim(-0.1, 1.6)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.legend()
st.pyplot(fig)

# --- User Selection ---
selected_label = st.selectbox("📍 Choose the category with the **highest Y mean**:",
                              [f"Category {i+1}" for i in range(n_categories)])
selected_index = int(selected_label.split()[1]) - 1
true_idx = int(np.argmax([np.mean(y) for y in y_data]))

# --- Submission ---
if st.button("🚀 Submit Answer"):
    is_correct = (selected_index == true_idx)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response = [
        timestamp,
        selected_palette,
        n_categories,
        selected_label,
        f"Category {true_idx+1}",
        "Correct" if is_correct else "Incorrect",
        ", ".join(selected_shapes)
    ]

    try:
        worksheet.append_row(response)
        if is_correct:
            st.success(f"✅ Correct! Category {true_idx+1} had the highest Y mean.")
        else:
            st.error(f"❌ Incorrect. The correct answer was Category {true_idx+1}.")
    except Exception as e:
        st.error(f"Failed to log response: {e}")
