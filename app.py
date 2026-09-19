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

# Выбор материала (вызывает легкую перезагрузку только при смене металла)
material = st.selectbox("Select Rod Material:", list(MATERIALS.keys()))
mat_data = MATERIALS[material]

st.info("📏 **Rod Specifications:** Length (L) = 0.500 m | Diameter (d) = 15.0 mm. Use the sliders INSIDE the graphs below to tune the frequency in real-time!")

# Расчет физики резонанса
E = mat_data["E"]
rho = mat_data["rho"]
rod_length = 0.500
v_sound = np.sqrt(E / rho)
f0 = v_sound / (2 * rod_length)
Q = 50 

# Диапазон частот для анимации (с шагом 20 Гц, чтобы браузер не лагал)
frequencies = np.arange(1000, 6001, 20)

# Генерируем данные для интерактивного графика Plotly
# Диапазон частот для анимации с высокой точностью (шаг 5 Гц для плавной прокрутки)
frequencies = np.arange(1000, 6001, 5)

# Генерируем данные для высокоточного интерактивного графика Plotly
fig = go.Figure()

# Повышаем детализацию: 500 точек для идеальной плавности синусоиды
t = np.linspace(0, 0.002, 500)
x = np.linspace(0, rod_length, 150)

# 1. Создаем базовые («стартовые») кривые для начальной частоты 1500 Гц
amp_start = 1.0 / np.sqrt(1.0 + Q**2 * (1500/f0 - f0/1500)**2)
if amp_start < 0.02: amp_start = 0.02

# Кривая осциллографа (индекс трассы 0)
fig.add_trace(go.Scatter(x=t*1000, y=amp_start*np.sin(2*np.pi*1500*t), mode='lines', line=dict(color='#39ff14', width=2.5), name="Oscilloscope"))
# Кривая стоячей волны + (индекс трассы 1)
fig.add_trace(go.Scatter(x=x, y=amp_start*np.cos(np.pi*x/rod_length), mode='lines', line=dict(color=mat_data["color"], width=3), xaxis="x2", yaxis="y2", name="Wave Envelope"))
# Кривая стоячей волны - (индекс трассы 2)
fig.add_trace(go.Scatter(x=x, y=-amp_start*np.cos(np.pi*x/rod_length), mode='lines', line=dict(color=mat_data["color"], width=1, dash='dash'), xaxis="x2", yaxis="y2", showlegend=False))
# Узел (Node) по центру (индекс трассы 3)
fig.add_trace(go.Scatter(x=[rod_length/2], y=[0], mode='markers', marker=dict(color='red', size=10), xaxis="x2", yaxis="y2", name="Center Clamp"))

# 2. Создаем кадры анимации (Frames) для каждого положения слайдера
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

# 3. Настраиваем интерактивный слайдер Plotly, который переключает кадры внутри браузера
sliders_steps = []
for f in frequencies:
    sliders_steps.append({
        "args": [[str(f)], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}],
        "label": str(f),
        "method": "animate"
    })


# 3. Настраиваем интерактивный слайдер Plotly, который переключает кадры внутри браузера
sliders_steps = []
for f in frequencies:
    sliders_steps.append({
        "args": [[str(f)], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}],
        "label": str(f),
        "method": "animate"
    })

# Оформление двойного темного графика на одном холсте (Subplots через слои)
fig.update_layout(
    template="plotly_dark",
    height=650,
    margin=dict(l=50, r=30, t=50, b=40),
    # Сетка первого графика (Осциллограф)
    xaxis=dict(title="Time (ms)", domain=[0, 1.0], range=[0, 2.0], gridcolor='#222222'),
    yaxis=dict(title="Amplitude (V)", range=[-1.1, 1.1], gridcolor='#222222'),
    # Сетка второго графика (Стрижень) - смещена вниз
    xaxis2=dict(title="Position along the rod (m)", domain=[0, 1.0], range=[0, rod_length], gridcolor='#222222', anchor="y2"),
    yaxis2=dict(title="Relative Displacement", range=[-1.2, 1.2], gridcolor='#222222', anchor="x2"),
    
    # Распределение осей по вертикали
    yaxis2_position=0.45,
    grid=dict(rows=2, columns=1, pattern='independent'),
    
    # Внедрение слайдера
    sliders=[{
        "active": int(np.where(frequencies == 1500)[0][0]),
        "currentvalue": {"prefix": "Generator Frequency: ", "suffix": " Hz", "font": {"color": "#00f0ff", "size": 16}},
        "pad": {"t": 50},
        "steps": sliders_steps
    }],
    showlegend=False
)

# Выводим готовый интерактивный холст
st.plotly_chart(fig, use_container_width=True)
