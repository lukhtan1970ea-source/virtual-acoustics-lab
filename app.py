import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

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

# 1. Page Configuration (Static part - loaded once)
st.set_page_config(page_title="Virtual Lab: Young's Modulus", layout="wide")

st.title("🔬 Virtual Acoustics Lab")
st.subheader("Dynamic Determination of Young's Modulus via Standing Waves")

# Create layout layout columns
col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚙️ Controls")
    # Material selection triggers full layout, but it's rare
    material = st.selectbox("Select Rod Material:", list(MATERIALS.keys()))
    mat_data = MATERIALS[material]
    
    st.info("📏 **Rod Specifications:**\n* Length (L): 0.500 m\n* Diameter (d): 15.0 mm")
    
    st.markdown("""
    **STUDENT GUIDE:**
    1. Drag the slider to change frequency.
    2. Click on the slider and use **Left/Right Keyboard Arrows** for ultra-precise tuning (1 Hz steps).
    3. Find the peak where Oscilloscope Amplitude reaches **1.0 V**.
    """)

# 2. Isolated Interactive Fragment (This block runs instantly inside the browser cache)
@st.fragment
def render_interactive_plots(material_name, mat_info):
    # Dynamic Slider inside the isolated fragment
    current_freq = st.slider(
        "Signal Generator Frequency (Hz):", 
        min_value=1000, max_value=6000, value=1500, step=1
    )
    
    # Physics Calculations (Lightweight mathematics)
    E = mat_info["E"]
    rho = mat_info["rho"]
    rod_length = 0.500
    
    v_sound = np.sqrt(E / rho)
    f0 = v_sound / (2 * rod_length)
    
    # Lorentzian resonance profile
    Q = 200 
    amp = 1.0 / np.sqrt(1.0 + Q**2 * (current_freq/f0 - f0/current_freq)**2)
    
    # Fast Plotting Block (Optimized vectors)
    plt.style.use('dark_background')
    fig, (ax_scope, ax_rod) = plt.subplots(2, 1, figsize=(7, 6))
    fig.tight_layout(pad=3.5)
    
    # 1. Digital Oscilloscope (Reduced to 300 points for immediate rendering)
    t = np.linspace(0, 0.002, 300)
    v_signal = amp * np.sin(2 * np.pi * current_freq * t)
    ax_scope.plot(t*1000, v_signal, color='#39ff14', linewidth=2)
    ax_scope.grid(True, color='#333333', linestyle='--')
    ax_scope.set_title("DIGITAL OSCILLOSCOPE (Receiver Output)", fontsize=10, fontweight='bold', color='#00f0ff')
    ax_scope.set_xlabel("Time (ms)", fontsize=9)
    ax_scope.set_ylabel("Amplitude (V)", fontsize=9)
    ax_scope.set_ylim(-1.1, 1.1)
    
    # 2. Standing Wave Profile (Reduced to 100 points)
    x = np.linspace(0, rod_length, 100)
    wave_profile = amp * np.cos(np.pi * x / rod_length)
    ax_rod.axhline(0, color='white', lw=3, alpha=0.3)
    ax_rod.plot(x, wave_profile, color=mat_info["color"], linewidth=3, label="Displacement Envelope")
    ax_rod.plot(x, -wave_profile, color=mat_info["color"], linewidth=1, linestyle='--')
    ax_rod.plot(rod_length/2, 0, 'ro', markersize=10, label="Clamped Center (Node)")
    ax_rod.set_title(f"Standing Wave Profile: {material_name} Rod", fontsize=10, fontweight='bold', color='#00f0ff')
    ax_rod.set_xlabel("Position along the rod (m)", fontsize=9)
    ax_rod.set_ylabel("Relative Displacement", fontsize=9)
    ax_rod.set_ylim(-1.2, 1.2)
    ax_rod.legend(loc="upper right", fontsize=8)
    ax_rod.grid(True, linestyle=':', alpha=0.4)
    
    # Output graph to the right column smoothly
    with col2:
        st.pyplot(fig)

# Run our optimized fragment
render_interactive_plots(material, mat_data)


