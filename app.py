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

# Page Configuration
st.set_page_config(page_title="Virtual Lab: Young's Modulus", layout="wide")

# Custom Dark Theme Styles


st.title("🔬 Virtual Acoustics Lab")
st.subheader("Dynamic Determination of Young's Modulus via Standing Waves")

# Layout Split: Sidebar for Controls, Main Panel for Graphs
col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚙️ Controls")
    
    # Material Dropdown
    material = st.selectbox("Select Rod Material:", list(MATERIALS.keys()))
    mat_data = MATERIALS[material]
    
    # Fixed Specifications Display
    st.info("📏 **Rod Specifications:**\n* Length (L): 0.500 m\n* Diameter (d): 15.0 mm")
    
    # Frequency Slider (Wider range to cover all new metals)
    current_freq = st.slider("Signal Generator Frequency (Hz):", 
                             min_value=1000, max_value=6000, value=1500, step=1)
    
    # Text Guide
    st.markdown("""
    **STUDENT GUIDE:**
    1. Tune the generator frequency to find the resonance maximum on the oscilloscope.
    2. At peak amplitude (V = 1.0), a standing wave forms (fundamental mode).
    3. Record the resonance frequency ($f_0$) to calculate Sound Velocity ($v$) and Young's Modulus ($E$).
    """)

# Physics Calculations
E = mat_data["E"]
rho = mat_data["rho"]
rod_length = 0.500

v_sound = np.sqrt(E / rho)
f0 = v_sound / (2 * rod_length)

# Resonance Curve Profile (Lorentzian distribution)
Q = 200 
amp = 1.0 / np.sqrt(1.0 + Q**2 * (current_freq/f0 - f0/current_freq)**2)

# Graph Plotting
plt.style.use('dark_background')
fig, (ax_scope, ax_rod) = plt.subplots(2, 1, figsize=(8, 7))
fig.tight_layout(pad=4.0)

# 1. Digital Oscilloscope
t = np.linspace(0, 0.002, 1000)
v_signal = amp * np.sin(2 * np.pi * current_freq * t)
ax_scope.plot(t*1000, v_signal, color='#39ff14', linewidth=2)
ax_scope.grid(True, color='#333333', linestyle='--')
ax_scope.set_title("DIGITAL OSCILLOSCOPE (Receiver Output)", fontsize=11, fontweight='bold', color='#00f0ff')
ax_scope.set_xlabel("Time (ms)")
ax_scope.set_ylabel("Amplitude (V)")
ax_scope.set_ylim(-1.1, 1.1)

# 2. Standing Wave Profile
x = np.linspace(0, rod_length, 200)
wave_profile = amp * np.cos(np.pi * x / rod_length)
ax_rod.axhline(0, color='white', lw=3, alpha=0.3)
ax_rod.plot(x, wave_profile, color=mat_data["color"], linewidth=3, label="Displacement Envelope")
ax_rod.plot(x, -wave_profile, color=mat_data["color"], linewidth=1, linestyle='--')
ax_rod.plot(rod_length/2, 0, 'ro', markersize=10, label="Clamped Center (Node)")
ax_rod.set_title(f"Standing Wave Profile inside the {material} Rod", fontsize=11, fontweight='bold', color='#00f0ff')
ax_rod.set_xlabel("Position along the rod (m)")
ax_rod.set_ylabel("Relative Displacement")
ax_rod.set_ylim(-1.2, 1.2)
ax_rod.legend(loc="upper right")
ax_rod.grid(True, linestyle=':', alpha=0.4)

with col2:
    st.pyplot(fig)

