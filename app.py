import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- PHYSICAL CONSTANTS (9 Materials) ---
MATERIALS = {
    "Steel": {"E": 2.0e11, "rho": 7800, "color": "cyan"},
    "Aluminum": {"E": 0.7e11, "rho": 2700, "color": "lightgreen"},
    "Copper": {"E": 1.1e11, "rho": 8900, "color": "orange"},
    "Iron": {"E": 2.1e11, "rho": 7870, "color": "darkgray"},
    "Lead": {"E": 0.16e11, "rho": 11340, "color": "purple"},
    "Tungsten": {"E": 4.1e11, "rho": 19250, "color": "gold"},
    "Titanium": {"E": 1.15e11, "rho": 4540, "color": "magenta"},
    "Gold": {"E": 0.78e11, "rho": 19300, "color": "yellow"},
    "Silver": {"E": 0.83e11, "rho": 10500, "color": "white"}
}

st.set_page_config(page_title="Virtual Lab: Young's Modulus", layout="wide")

st.title("🔬 Virtual Acoustics Lab")
st.subheader("Dynamic Determination of Young's Modulus via Standing Waves")

# Основная разметка экрана (2 колонки)
col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚙️ Controls")
    material = st.selectbox("Select Rod Material:", list(MATERIALS.keys()))
    mat_data = MATERIALS[material]
    
    st.info("📏 **Rod Specifications:**\n* Length (L): 0.500 m\n* Diameter (d): 15.0 mm")
    
    st.markdown("""
    **STUDENT GUIDE:**
    1. Click on the slider handle.
    2. Use **Left/Right Keyboard Arrows** for super-precise 1 Hz tuning.
    3. Find the peak frequency where Oscilloscope Amplitude reaches **1.0 V**.
    """)

# Изолированный фрагмент: при движении слайдера Streamlit обновляет ТОЛЬКО этот блок
@st.experimental_fragment
def run_experiment_block(selected_material, physics_data):
    # Плавный слайдер с шагом 1 Гц
    current_freq = st.slider(
        "Signal Generator Frequency (Hz):", 
        min_value=1000, max_value=6000, value=1500, step=1
    )
    
    # Физические расчеты амплитуды резонанса
    E = physics_data["E"]
    rho = physics_data["rho"]
    rod_length = 0.500
    
    v_sound = np.sqrt(E / rho)
    f0 = v_sound / (2 * rod_length)
    
    Q = 45 # Оптимальная ширина пика для ручного поиска
    amp = 1.0 / np.sqrt(1.0 + Q**2 * (current_freq/f0 - f0/current_freq)**2)
    
    if amp < 0.02:
        amp = 0.02

    # Создание графиков через классический Matplotlib (Dark стиль)
    plt.style.use('dark_background')
    fig, (ax_scope, ax_rod) = plt.subplots(2, 1, figsize=(7, 6))
    fig.tight_layout(pad=3.5)
    
    # 1. Цифровой осциллограф
    t = np.linspace(0, 0.002, 250) 
    v_signal = amp * np.sin(2 * np.pi * current_freq * t)
    ax_scope.plot(t*1000, v_signal, color='lime', linewidth=2.5)
    ax_scope.grid(True, color='#333333', linestyle='--')
    ax_scope.set_title(f"DIGITAL OSCILLOSCOPE (Current Freq: {current_freq} Hz)", fontsize=10, fontweight='bold', color='#00f0ff')
    ax_scope.set_xlabel("Time (ms)", fontsize=9)
    ax_scope.set_ylabel("Amplitude (V)", fontsize=9)
    ax_scope.set_ylim(-1.1, 1.1)
    
    # 2. Профиль стоячої хвилі
    x = np.linspace(0, rod_length, 100)
    wave_profile = amp * np.cos(np.pi * x / rod_length)
    ax_rod.axhline(0, color='white', lw=2, alpha=0.3)
    ax_rod.plot(x, wave_profile, color=physics_data["color"], linewidth=3, label="Displacement Envelope")
    ax_rod.plot(x, -wave_profile, color=physics_data["color"], linewidth=1, linestyle='--')
    ax_rod.plot(rod_length/2, 0, 'ro', markersize=9, label="Clamped Center (Node)")
    ax_rod.set_title(f"Standing Wave Profile: {selected_material} Rod", fontsize=10, fontweight='bold', color='#00f0ff')
    ax_rod.set_xlabel("Position along the rod (m)", fontsize=9)
    ax_rod.set_ylabel("Relative Displacement", fontsize=9)
    ax_rod.set_ylim(-1.2, 1.2)
    ax_rod.legend(loc="upper right", fontsize=8)
    ax_rod.grid(True, linestyle=':', alpha=0.3)
    
    # Отрисовка графиков в правую колонку
    with col2:
        st.pyplot(fig)

# Запуск интерактивной части
run_experiment_block(material, mat_data)
