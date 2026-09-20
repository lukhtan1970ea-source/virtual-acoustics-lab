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

# Основная разметка экрана (2 колонки)
col1, col2 = st.columns([1, 1.5]) # Левая чуть уже, правая шире

with col1:
    st.header("⚙️ Controls")
    material = st.selectbox("Select Rod Material:", list(MATERIALS.keys()))
    mat_data = MATERIALS[material]
    
    st.info("📏 **Rod Specifications:**\n* Length (L): 0.500 m\n* Diameter (d): 15.0 mm")
    
    # Родной высокоскоростной слайдер Streamlit
    current_freq = st.slider(
        "Signal Generator Frequency (Hz):", 
        min_value=1000, max_value=6000, value=1500, step=1
    )
    
    st.markdown("""
    **STUDENT GUIDE:**
    1. Click on the slider handle inside the workspace.
    2. Use **Left/Right Keyboard Arrows** for ultra-precise 1 Hz tuning.
    3. Find the peak frequency where Oscilloscope Amplitude reaches **1.0 V**.
    """)

# --- ФИЗИЧЕСКИЕ РАСЧЕТЫ (Выполняются мгновенно на сервере) ---
E = mat_data["E"]
rho = mat_data["rho"]
rod_length = 0.500

v_sound = np.sqrt(E / rho)
f0 = v_sound / (2 * rod_length)

Q = 50 # Оптимальная ширина резонансного пика
amp = 1.0 / np.sqrt(1.0 + Q**2 * (current_freq/f0 - f0/current_freq)**2)

if amp < 0.02:
    amp = 0.02

# --- ГЕНЕРАЦИЯ ВЕКТОРОВ ДАННЫХ ---
# 1. Цифровой осциллограф (400 точек для абсолютной округлости и плавности линии)
t = np.linspace(0, 0.002, 400) 
v_signal = amp * np.sin(2 * np.pi * current_freq * t)

fig_scope = go.Figure()
fig_scope.add_trace(go.Scatter(x=t*1000, y=v_signal, mode='lines', line=dict(color='#39ff14', width=3)))

grid_style = dict(gridcolor='rgba(128, 128, 128, 0.15)', zerolinecolor='rgba(128, 128, 128, 0.3)')

fig_scope.update_layout(
    title=dict(text=f"DIGITAL OSCILLOSCOPE (Current Freq: {current_freq} Hz)", font=dict(color='#00f0ff', size=14)),
    xaxis=dict(title="Time (ms)", range=[0, 2.0], **grid_style),
    yaxis=dict(title="Amplitude (V)", range=[-1.1, 1.1], **grid_style),
    template="plotly_dark",
    margin=dict(l=40, r=20, t=40, b=40),
    height=290,
    showlegend=False
)

# 2. Профиль стоячей волны
x = np.linspace(0, rod_length, 150)
wave_profile = amp * np.cos(np.pi * x / rod_length)

fig_rod = go.Figure()
fig_rod.add_trace(go.Scatter(x=x, y=wave_profile, mode='lines', line=dict(color=mat_data["color"], width=3), name="Displacement"))
fig_rod.add_trace(go.Scatter(x=x, y=-wave_profile, mode='lines', line=dict(color=mat_data["color"], width=1, dash='dash'), showlegend=False))
fig_rod.add_trace(go.Scatter(x=[rod_length/2], y=[0], mode='markers', marker=dict(color='red', size=11), name="Clamped Center (Node)"))

fig_rod.update_layout(
    title=dict(text=f"Standing Wave Profile: {material} Rod", font=dict(color='#00f0ff', size=14)),
    xaxis=dict(title="Position along the rod (m)", range=[0, rod_length], **grid_style),
    yaxis=dict(title="Relative Displacement", range=[-1.2, 1.2], **grid_style),
    template="plotly_dark",
    margin=dict(l=40, r=20, t=40, b=40),
    height=290,
    showlegend=False
)

# Выводим графики в правую колонку
with col2:
    st.plotly_chart(fig_scope, use_container_width=True, key=f"scope_{current_freq}")
    st.plotly_chart(fig_rod, use_container_width=True, key=f"rod_{current_freq}")
