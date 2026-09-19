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

# Выбор материала
material = st.selectbox("Select Rod Material:", list(MATERIALS.keys()))
mat_data = MATERIALS[material]

st.info("📏 **Rod Specifications:** Length (L) = 0.500 m | Diameter (d) = 15.0 mm. Use the slider INSIDE the graph below to tune the frequency in real-time!")

# Расчет физики резонанса
E = mat_data["E"]
rho = mat_data["rho"]
rod_length = 0.500
v_sound = np.sqrt(E / rho)
f0 = v_sound / (2 * rod_length)
Q = 50 

# ОПТИМИЗИРОВАННЫЙ ШАГ: 10 Гц для идеального баланса плавности и скорости
frequencies = np.arange(1000, 6001, 10)

fig = go.Figure()

# ПОВЫШЕННАЯ ДЕТАЛИЗАЦИЯ: 400 точек дают абсолютно гладкую аналоговую синусоиду
t = np.linspace(0, 0.002, 400)
x = np.linspace(0, rod_length, 120)

# Стартовая частота (середина диапазона для красивой инициализации)
start_f = 3500
amp_start = 1.0 / np.sqrt(1.0 + Q**2 * (start_f/f0 - f0/start_f)**2)
if amp_start < 0.02: amp_start = 0.02

# Базовые трассы (Очищенные маркеры без дублирования)
fig.add_trace(go.Scatter(x=t*1000, y=amp_start*np.sin(2*np.pi*start_f*t), mode='lines', line=dict(color='#39ff14', width=3), name="Oscilloscope"))
fig.add_trace(go.Scatter(x=x, y=amp_start*np.cos(np.pi*x/rod_length), mode='lines', line=dict(color=mat_data["color"], width=3), xaxis="x2", yaxis="y2", name="Wave Envelope"))
fig.add_trace(go.Scatter(x=x, y=-amp_start*np.cos(np.pi*x/rod_length), mode='lines', line=dict(color=mat_data["color"], width=1, dash='dash'), xaxis="x2", yaxis="y2", showlegend=False))
fig.add_trace(go.Scatter(x=[rod_length/2], y=[0], mode='markers', marker=dict(color='red', size=10), xaxis="x2", yaxis="y2", name="Center Clamp"))

# Генерация чистых кадров без наслоения
frames = []
for f in frequencies:
    amp = 1.0 / np.sqrt(1.0 + Q**2 * (f/f0 - f0/f)**2)
    if amp < 0.02: amp = 0.02
    
    y_v = amp * np.sin(2 * np.pi * f * t)
    y_w = amp * np.cos(np.pi * x / rod_length)
    
    frames.append(go.Frame(
        data=[
            go.Scatter(y=y_v),
            go.Scatter(y=y_w),
            go.Scatter(y=-y_w)
        ],
        name=str(f)
    ))
fig.frames = frames

# Шаги слайдера Plotly
sliders_steps = []
for f in frequencies:
    sliders_steps.append({
        "args": [[str(f)], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}],
        "label": str(f),
        "method": "animate"
    })

# Оформление универсальной сетки (отчетливо видна и на светлом, и на темном фоне)
grid_color = 'rgba(128, 128, 128, 0.25)'

fig.update_layout(
    height=650,
    margin=dict(l=50, r=30, t=50, b=40),
    xaxis=dict(title="Time (ms)", domain=[0, 1.0], range=[0, 2.0], gridcolor=grid_color),
    yaxis=dict(title="Amplitude (V)", range=[-1.1, 1.1], gridcolor=grid_color),
    xaxis2=dict(title="Position along the rod (m)", domain=[0, 1.0], range=[0, rod_length], gridcolor=grid_color, anchor="y2"),
    yaxis2=dict(title="Relative Displacement", range=[-1.2, 1.2], gridcolor=grid_color, anchor="x2"),
    yaxis2_position=0.45,
    grid=dict(rows=2, columns=1, pattern='independent'),
    sliders=[{
        "active": int(np.where(frequencies == start_f)[0][0]),
        "currentvalue": {"prefix": "Generator Frequency: ", "suffix": " Hz", "font": {"color": "#00f0ff", "size": 16}},
        "pad": {"t": 50},
        "steps": sliders_steps
    }],
    showlegend=False
)

# КРИТИЧЕСКИЙ МОМЕНТ: динамический ключ привязан к металлу. 
# Смена металла полностью уничтожает старый кэш Plotly, предотвращая полупрозрачность!
st.plotly_chart(fig, use_container_width=True, key=f"plotly_lab_{material}")
