import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

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

col1, col2 = st.columns([1, 2]) # Левая колонка чуть уже, правая шире

with col1:
    st.header("⚙️ Controls")
    material = st.selectbox("Select Rod Material:", list(MATERIALS.keys()))
    mat_data = MATERIALS[material]
    
    st.info("📏 **Rod Specifications:**\n* Length (L): 0.500 m\n* Diameter (d): 15.0 mm")
    
    st.markdown("""
    **STUDENT GUIDE:**
    1. Click on the slider handle.
    2. Use **Left/Right Keyboard Arrows** for precise 1 Hz tuning.
    3. Find the peak frequency where Oscilloscope Amplitude reaches max values.
    """)

# Изолированный быстрый фрагмент для мгновенного отклика слайдера
@st.fragment
def run_fast_plots(selected_material, physics_data):
    current_freq = st.slider(
        "Signal Generator Frequency (Hz):", 
        min_value=1000, max_value=6000, value=1500, step=1
    )
    
    # Физические расчеты
    E = physics_data["E"]
    rho = physics_data["rho"]
    rod_length = 0.500
    
    v_sound = np.sqrt(E / rho)
    f0 = v_sound / (2 * rod_length)
    
    Q = 45 
    amp = 1.0 / np.sqrt(1.0 + Q**2 * (current_freq/f0 - f0/current_freq)**2)
    if amp < 0.02:
        amp = 0.02

    # --- 1. ГРАФИК ОСЦИЛЛОГРАФА (Altair - рендеринг в браузере) ---
    t = np.linspace(0, 0.002, 150) 
    v_signal = amp * np.sin(2 * np.pi * current_freq * t)
    df_scope = pd.DataFrame({"Time (ms)": t * 1000, "Amplitude (V)": v_signal})
    
    chart_scope = alt.Chart(df_scope).mark_line(color='#39ff14', strokeWidth=2.5).encode(
        x=alt.X('Time (ms):Q', scale=alt.Scale(domain=[0, 2.0])),
        y=alt.Y('Amplitude (V):Q', scale=alt.Scale(domain=[-1.1, 1.1]))
    ).properties(
        title=f"DIGITAL OSCILLOSCOPE (Current Freq: {current_freq} Hz)",
        height=280
    ).configure_view(strokeWidth=0).configure_axis(gridColor='#333333')

    # --- 2. ГРАФИК СТРОЯЧЕЙ ВОЛНЫ (Altair) ---
    x = np.linspace(0, rod_length, 80)
    wave_profile = amp * np.cos(np.pi * x / rod_length)
    df_rod = pd.DataFrame({"Position (m)": x, "Displacement": wave_profile, "Displacement_Neg": -wave_profile})
    
    # Основная линия волны
    line1 = alt.Chart(df_rod).mark_line(color=physics_data["color"], strokeWidth=3).encode(
        x=alt.X('Position (m):Q', scale=alt.Scale(domain=[0, rod_length])),
        y=alt.Y('Displacement:Q', scale=alt.Scale(domain=[-1.2, 1.2]), title="Relative Displacement")
    )
    # Зеркальная пунктирная линия огибающей
    line2 = alt.Chart(df_rod).mark_line(color=physics_data["color"], strokeWidth=1, strokeDash=[4, 4]).encode(
        x='Position (m):Q',
        y='Displacement_Neg:Q'
    )
    # Точка зажима (Node) посередине
    node_df = pd.DataFrame({"x": [rod_length / 2], "y": [0]})
    node_point = alt.Chart(node_df).mark_circle(color='red', size=120).encode(x='x:Q', y='y:Q')
    
    # Сборка графика воедино
    chart_rod = alt.layer(line1, line2, node_point).properties(
        title=f"Standing Wave Profile: {selected_material} Rod",
        height=280
    ).configure_view(strokeWidth=0).configure_axis(gridColor='#333333')

    # Вывод графиков в правую колонку
    with col2:
        st.altair_chart(chart_scope, use_container_width=True)
        st.altair_chart(chart_rod, use_container_width=True)

run_fast_plots(material, mat_data)

