import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- PHYSICAL CONSTANTS (9 Materials) ---
MATERIALS = {
    "Steel": {"E": 2.0e11, "rho": 7800, "color": "#00f0ff"},
    "Aluminum": {"E": 0.7e11, "rho": 2700, "color": "#39ff14"},
    "Copper": {"E": 1.1e11, "rho": 8900, "color": "#ffaa00"},
    "Iron": {"E": 2.1e11, "rho": 7870, "color": "#aaaaaa"},
    "Lead": {"E": 0.16e11, "rho": 11340, "color": "#cc00ff"},
    "Tungsten": {"E": 4.1e11, "rho": 19250, "color": "#ffcc00"},
    "Titanium": {"E": 1.15e11, "rho": 4540, "color": "#ff00ff"},
    "Gold": {"E": 0.78e11, "rho": 19300, "color": "#ffee00"},
    "Silver": {"E": 0.83e11, "rho": 10500, "color": "#ffffff"}
}

st.set_page_config(page_title="Virtual Lab: Young's Modulus", layout="wide")

st.title("🔬 Virtual Acoustics Lab")
st.subheader("Dynamic Determination of Young's Modulus via Standing Waves")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚙️ Controls")
    material = st.selectbox("Select Rod Material:", list(MATERIALS.keys()))
    mat_data = MATERIALS[material]
    
    st.info("📏 **Rod Specifications:**\n* Length (L): 0.500 m\n* Diameter (d): 15.0 mm")
    
    st.markdown("""
    **STUDENT GUIDE:**
    1. Drag the slider to change frequency.
    2. Click on the slider and use **Left/Right Keyboard Arrows** for ultra-precise tuning (1 Hz steps).
    3. Find the peak where Oscilloscope Amplitude reaches **1.0 V**.
    """)

# Isolated Interactive Fragment for instant responsiveness
@st.fragment
def render_plots(material_name, mat_info):
    current_freq = st.slider(
        "Signal Generator Frequency (Hz):", 
        min_value=1000, max_value=6000, value=1500, step=1
    )
    
    # Physics Calculations
    E = mat_info["E"]
    rho = mat_info["rho"]
    rod_length = 0.500
    
    v_sound = np.sqrt(E / rho)
    f0 = v_sound / (2 * rod_length)
    
    Q = 200 
    amp = 1.0 / np.sqrt(1.0 + Q**2 * (current_freq/f0 - f0/current_freq)**2)
    
    # --- 1. DIGITAL OSCILLOSCOPE (Plotly) ---
    t = np.linspace(0, 0.002, 200)
    v_signal = amp * np.sin(2 * np.pi * current_freq * t)
    
    fig_scope = go.Figure()
    fig_scope.add_trace(go.Scatter(x=t*1000, y=v_signal, mode='lines', line=dict(color='#39ff14', width=3)))
    fig_scope.update_layout(
        title=dict(text="DIGITAL OSCILLOSCOPE (Receiver Output)", font=dict(color='#00f0ff', size=14, family="Arial")),
        xaxis=dict(title="Time (ms)", range=[0, 2], gridcolor='#222222'),
        yaxis=dict(title="Amplitude (V)", range=[-1.1, 1.1], gridcolor='#222222'),
        template="plotly_dark",
        margin=dict(l=40, r=20, t=40, b=40),
        height=320,
        showlegend=False
    )
    
    # --- 2. STANDING WAVE PROFILE (Plotly) ---
    x = np.linspace(0, rod_length, 100)
    wave_profile = amp * np.cos(np.pi * x / rod_length)
    
    fig_rod = go.Figure()
    # Envelope lines
    fig_rod.add_trace(go.Scatter(x=x, y=wave_profile, mode='lines', line=dict(color=mat_info["color"], width=3), name="Displacement"))
    fig_rod.add_trace(go.Scatter(x=x, y=-wave_profile, mode='lines', line=dict(color=mat_info["color"], width=1, dash='dash'), showlegend=False))
    # Neutral axis
    fig_rod.add_shape(type="line", x0=0, y0=0, x1=rod_length, y1=0, line=dict(color="gray", width=2, dash="dot"))
    # Node point (Center)
    fig_rod.add_trace(go.Scatter(x=[rod_length/2], y=[0], mode='markers', marker=dict(color='red', size=12), name="Clamped Center (Node)"))
    
    fig_rod.update_layout(
        title=dict(text=f"Standing Wave Profile: {material_name} Rod", font=dict(color='#00f0ff', size=14, family="Arial")),
        xaxis=dict(title="Position along the rod (m)", range=[0, rod_length], gridcolor='#222222'),
        yaxis=dict(title="Relative Displacement", range=[-1.2, 1.2], gridcolor='#222222'),
        template="plotly_dark",
        margin=dict(l=40, r=20, t=40, b=40),
        height=320,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    with col2:
        st.plotly_chart(fig_scope, use_container_width=True, key="scope_chart")
        st.plotly_chart(fig_rod, use_container_width=True, key="rod_chart")

render_plots(material, mat_data)



