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

# --- Configuration ---
st.set_page_config(page_title="Shape Correlation Experiment", layout="wide")

# --- Constants ---
TOTAL_TASKS = 54
TRAINING_TASKS = 3
SHAPES_FOLDER = "Shapes-All"

# --- Google Sheets Setup ---
def init_google_sheets():
    try:
        if 'google_sheets' not in st.secrets:
            st.error("Google Sheets credentials not found in secrets!")
            return None
            
        scope = ["https://spreadsheets.google.com/feeds", 
                "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["google_sheets"], scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g").worksheet("Eksperimen_4")
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {str(e)}")
        return None

# --- Shape Management ---
def load_shapes():
    if not os.path.exists(SHAPES_FOLDER):
        st.error(f"Shape folder '{SHAPES_FOLDER}' not found!")
        return []
    
    try:
        shapes = [os.path.join(SHAPES_FOLDER, f) 
                 for f in os.listdir(SHAPES_FOLDER) 
                 if f.lower().endswith('.png')]
        
        if len(shapes) < 4:
            st.error(f"Need at least 4 shapes in {SHAPES_FOLDER}, found {len(shapes)}")
            return []
        
        return shapes
    except Exception as e:
        st.error(f"Error loading shapes: {str(e)}")
        return []

# --- Plot Generation ---
def generate_scatterplot(is_high_corr, shape_paths):
    """Generate a scatterplot with given shapes and correlation level"""
    try:
        fig, ax = plt.subplots(figsize=(4, 4))
        
        for shape_path in shape_paths:
            mean = np.random.uniform(0.3, 1.2, 2)
            
            if is_high_corr:
                cov = [[0.02, 0.015], [0.015, 0.02]]  # High correlation
            else:
                cov = [[0.02, 0], [0, 0.02]]  # Low correlation
                
            data = np.random.multivariate_normal(mean, cov, 20)
            
            img = Image.open(shape_path).convert("RGBA").resize((20, 20))
            im = OffsetImage(img, zoom=1.0)
            
            for x, y in data:
                ab = AnnotationBbox(im, (x, y), frameon=False)
                ax.add_artist(ab)
        
        ax.set_xlim(0, 1.6)
        ax.set_ylim(0, 1.6)
        ax.axhline(0.8, color='gray', linestyle='--', linewidth=0.5)
        ax.axvline(0.8, color='gray', linestyle='--', linewidth=0.5)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    except Exception as e:
        st.error(f"Error generating plot: {str(e)}")
        return None

# --- Session State Initialization ---
def init_session_state():
    if 'step' not in st.session_state:
        st.session_state.step = 0
        st.session_state.saved_data = [None] * TOTAL_TASKS
        st.session_state.start_time = datetime.now()
        st.session_state.responses = []
        st.session_state.initialized = True

# --- Main App ---
def main():
    # Initialize session state first
    init_session_state()
    
    # Load other components
    sheet = init_google_sheets()
    shapes = load_shapes()
    
    if not shapes:
        st.stop()

    # Handle experiment completion
    if st.session_state.step >= TOTAL_TASKS:
        st.balloons()
        st.success("🎉 Experiment completed! Thank you for participating.")
        
        if st.button("Restart Experiment"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()
        return
    
    # Validate step is within bounds
    if st.session_state.step < 0 or st.session_state.step >= TOTAL_TASKS:
        st.error("Invalid step index detected. Resetting experiment.")
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()
        return

    # Determine current mode
    is_training = st.session_state.step < TRAINING_TASKS
    current_mode = "Training" if is_training else "Experiment"
    
    # Display progress
    st.title("Shape Correlation Perception Experiment")
    st.subheader(f"{current_mode} Task {st.session_state.step + 1}/{TOTAL_TASKS}")
    st.progress((st.session_state.step + 1) / TOTAL_TASKS)
    
    # Generate or retrieve current task
    if st.session_state.saved_data[st.session_state.step] is None:
        try:
            plotA_shapes = random.sample(shapes, random.randint(2, 4))
            plotB_shapes = random.sample(shapes, random.randint(2, 4))
            high_corr_plot = random.choice(["A", "B"])
            st.session_state.saved_data[st.session_state.step] = (plotA_shapes, plotB_shapes, high_corr_plot)
        except Exception as e:
            st.error(f"Error generating task: {str(e)}")
            st.stop()
    
    try:
        plotA_shapes, plotB_shapes, high_corr_plot = st.session_state.saved_data[st.session_state.step]
    except (IndexError, TypeError) as e:
        st.error("Invalid task data detected. Resetting experiment.")
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()
        return
    
    # Display the two plots
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Plot A**")
        figA = generate_scatterplot(high_corr_plot == "A", plotA_shapes)
        if figA:
            st.pyplot(figA)
        else:
            st.stop()

    with col2:
        st.markdown("**Plot B**")
        figB = generate_scatterplot(high_corr_plot == "B", plotB_shapes)
        if figB:
            st.pyplot(figB)
        else:
            st.stop()
    
    # User response
    choice = st.radio("Which plot shows higher correlation?", ["A", "B"], index=None)
    
    if st.button("Submit Answer"):
        if not choice:
            st.warning("Please select an answer before submitting.")
            return
        
        # Calculate response metrics
        is_correct = choice == high_corr_plot
        response_time = (datetime.now() - st.session_state.start_time).total_seconds()
        
        # Store response
        response_data = {
            "task_number": st.session_state.step + 1,
            "mode": current_mode,
            "choice": choice,
            "correct_answer": high_corr_plot,
            "is_correct": is_correct,
            "response_time": response_time,
            "plotA_shapes": [os.path.basename(p) for p in plotA_shapes],
            "plotB_shapes": [os.path.basename(p) for p in plotB_shapes],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save to Google Sheets (only for actual experiment)
        if not is_training and sheet:
            try:
                sheet.append_row(list(response_data.values()))
            except Exception as e:
                st.error(f"Failed to save data: {str(e)}")
        
        # Store in session
        st.session_state.responses.append(response_data)
        
        # Provide feedback during training
        if is_training:
            if is_correct:
                st.success("✅ Correct! This is a training example.")
            else:
                st.error(f"❌ Not quite right. The correct answer was {high_corr_plot}.")
            
            st.info("This was a training example. The actual experiment will begin next.")
        
        # Move to next task
        st.session_state.step += 1
        st.session_state.start_time = datetime.now()
        
        # Use try-except for rerun
        try:
            st.experimental_rerun()
        except:
            st.rerun()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.error("The experiment will now reset.")
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
