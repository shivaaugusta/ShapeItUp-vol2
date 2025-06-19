import streamlit as st
import os
import random
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image

# --- Setup Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_sheets"], scopes=scope)
client = gspread.authorize(creds)
worksheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g").worksheet("Eksperimen_4")

# --- Gabungkan bentuk unik dari semua folder ---
ROOT_FOLDERS = ["Shapes-D3", "Shapes-Excel", "Shapes-Tableau", "Shapes-Matlab", "Shapes-R"]
def collect_unique_shapes():
    shape_dict = {}
    for folder in ROOT_FOLDERS:
        if not os.path.exists(folder):
            continue
        for fname in os.listdir(folder):
            if fname.endswith(".png"):
                label = os.path.splitext(fname)[0]
                if label not in shape_dict:
                    shape_dict[label] = os.path.join(folder, fname)
    return shape_dict

SHAPE_DICT = collect_unique_shapes()
ALL_LABELS = list(SHAPE_DICT.keys())

# --- Streamlit UI ---
st.title("⭐ Eksperimen 4: Pilih 3 Bentuk Favorit")
st.write("Pilih 3 bentuk yang menurutmu paling **nyaman dan menarik** untuk digunakan dalam visualisasi data.")

# --- Ambil 20 bentuk acak ---
random.seed(42)  # agar konsisten
selected_labels = random.sample(ALL_LABELS, min(20, len(ALL_LABELS)))
selected_paths = [SHAPE_DICT[label] for label in selected_labels]

# --- Pilihan bentuk (grid) ---
st.subheader("📷 Pilih 3 bentuk favorit")
cols = st.columns(5)
selected = []

for i, label in enumerate(selected_labels):
    col = cols[i % 5]
    with col:
        st.image(selected_paths[i], caption=label, width=80)
        if st.checkbox(f"Pilih {label}", key=f"shape_{i}"):
            selected.append(label)

# --- Submit ---
if st.button("🚀 Submit"):
    if len(selected) != 3:
        st.error("❌ Kamu harus memilih **tepat 3 bentuk**.")
    else:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            worksheet.append_row([timestamp] + selected)
            st.success("✅ Terima kasih! Jawaban kamu sudah disimpan.")
        except Exception as e:
            st.error(f"Gagal menyimpan ke Google Sheets: {e}")
