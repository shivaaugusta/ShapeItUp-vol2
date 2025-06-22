# --- Streamlit App Experiment 4 (Revised with Random A/B) ---
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

# --- Folder with Shapes ---
SHAPE_FOLDER = "Shapes-All"
SHAPE_LIST = sorted([f for f in os.listdir(SHAPE_FOLDER) if f.endswith(".png")])

# --- Session Setup ---
if "trial_index" not in st.session_state:
    st.session_state.trial_index = 1
    st.session_state.total_trials = 54
    st.session_state.correct_count = 0

index = st.session_state.trial_index

st.title("🔍 Eksperimen 4: Korelasi Bentuk")
st.subheader(f"Soal #{index} dari {st.session_state.total_trials}")

# --- Generate Scatterplots ---
def generate_scatter(corr, shape_name):
    cov = [[1, corr], [corr, 1]]
    data = np.random.multivariate_normal([0.75, 0.75], cov, 60)
    x_vals, y_vals = data[:, 0], data[:, 1]
    img = Image.open(os.path.join(SHAPE_FOLDER, shape_name)).convert("RGBA").resize((20, 20))
    return x_vals, y_vals, img

# --- Generate Task ---
if f"scatter_A_{index}" not in st.session_state:
    # Ambil dua bentuk acak
    shape_high, shape_low = random.sample(SHAPE_LIST, 2)

    # Generate scatterplot dengan korelasi tinggi dan rendah
    x_high, y_high, img_high = generate_scatter(0.9, shape_high)
    x_low, y_low, img_low = generate_scatter(0.2, shape_low)

    # Acak penempatan target di A atau B
    target_in_A = random.choice([True, False])

    if target_in_A:
        x_A, y_A, img_A = x_high, y_high, img_high
        x_B, y_B, img_B = x_low, y_low, img_low
        st.session_state[f"correct_{index}"] = "A"
    else:
        x_A, y_A, img_A = x_low, y_low, img_low
        x_B, y_B, img_B = x_high, y_high, img_high
        st.session_state[f"correct_{index}"] = "B"

    st.session_state[f"scatter_A_{index}"] = (x_A, y_A, img_A)
    st.session_state[f"scatter_B_{index}"] = (x_B, y_B, img_B)
    st.session_state[f"shapes_{index}"] = (shape_high, shape_low)

# --- Load state ---
x_A, y_A, img_A = st.session_state[f"scatter_A_{index}"]
x_B, y_B, img_B = st.session_state[f"scatter_B_{index}"]
shape_high, shape_low = st.session_state[f"shapes_{index}"]

# --- Display plots ---
col1, col2 = st.columns(2)
with col1:
    figA, axA = plt.subplots()
    for x, y in zip(x_A, y_A):
        ab = AnnotationBbox(OffsetImage(img_A, zoom=1.0), (x, y), frameon=False)
        axA.add_artist(ab)
    axA.set_xlim(-0.5, 2)
    axA.set_ylim(-0.5, 2)
    axA.set_title("Plot A")
    axA.axis("off")
    st.pyplot(figA)

with col2:
    figB, axB = plt.subplots()
    for x, y in zip(x_B, y_B):
        ab = AnnotationBbox(OffsetImage(img_B, zoom=1.0), (x, y), frameon=False)
        axB.add_artist(ab)
    axB.set_xlim(-0.5, 2)
    axB.set_ylim(-0.5, 2)
    axB.set_title("Plot B")
    axB.axis("off")
    st.pyplot(figB)

# --- Input ---
answer = st.radio("📍 Menurut Anda, plot mana yang lebih berkorelasi?", ["A", "B"])

# --- Submit ---
if st.button("🚀 Submit Jawaban"):
    correct = st.session_state[f"correct_{index}"]
    benar = answer == correct

    if benar:
        st.session_state.correct_count += 1
        st.success("✅ Jawaban benar!")
    else:
        st.error(f"❌ Jawaban salah. Yang benar: {correct}")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        timestamp, index, shape_high, shape_low, answer, correct,
        "Benar" if benar else "Salah"
    ]

    try:
        sheet.append_row(row)
    except Exception as e:
        st.warning(f"Gagal simpan ke spreadsheet: {e}")

    st.session_state.trial_index += 1
    st.rerun()

# --- Final ---
if st.session_state.trial_index > st.session_state.total_trials:
    st.success(f"🎉 Eksperimen selesai. Skor Anda: {st.session_state.correct_count} dari {st.session_state.total_trials}")
    st.balloons()
    st.stop()
