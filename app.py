import streamlit as st
import numpy as np
import streamlit.components.v1 as components

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

col1, col2 = st.columns([1, 1.8])

with col1:
    st.header("⚙️ Controls")
    material = st.selectbox("Select Rod Material:", list(MATERIALS.keys()))
    mat_data = MATERIALS[material]
    
    st.info("📏 **Rod Specifications:**\n* Length (L): 0.500 m\n* Diameter (d): 15.0 mm")
    
    st.markdown("""
    **STUDENT GUIDE:**
    1. Drag the slider inside the workspace on the right.
    2. The graphs will update **instantly in real-time** as you move the mouse.
    3. Find the peak frequency where Oscilloscope Amplitude reaches **1.0 V**.
    """)

# Расчет физики резонанса для передачи в браузер
E = mat_data["E"]
rho = mat_data["rho"]
v_sound = np.sqrt(E / rho)
f0 = v_sound / (2 * 0.500)
line_color = mat_data["color"]

# Высокоскоростной автономный интерактивный движок на чистом JavaScript + Chart.js
js_engine_code = f"""
<div id="controls" style="font-family: Arial, sans-serif; color: white; background: #1e222b; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
    <label style="display:block; margin-bottom:8px; font-weight:bold; font-size:16px;">
        Signal Generator Frequency: <span id="freq_val" style="color:#00f0ff; font-size:18px;">1500</span> Hz
    </label>
    <input type="range" id="realtime_slide" min="1000" max="6000" value="1500" step="1" 
        style="width: 100%; accent-color: #00f0ff; cursor: pointer;">
</div>

<div style="position: relative; height:240px; width:100%;"><canvas id="scopeCanvas"></canvas></div>
<div style="position: relative; height:240px; width:100%; margin-top:25px;"><canvas id="rodCanvas"></canvas></div>

<script src="https://jsdelivr.net"></script>

<script>
    const f0 = {f0};
    const Q = 50; 
    const rodLength = 0.500;
    const waveColor = "{line_color}";
    
    const t_points = [];
    for(let i=0; i<=600; i++) t_points.push((0.002 / 600) * i);
    
    const x_points = [];
    for(let i=0; i<=150; i++) x_points.push((rodLength / 150) * i);

    // Конфигурация Цифрового Осциллографа
    const ctxScope = document.getElementById('scopeCanvas').getContext('2d');
    const scopeChart = new Chart(ctxScope, {{
        type: 'line',
        data: {{
            labels: t_points.map(t => (t * 1000).toFixed(2)),
            datasets: [{{ data: new Array(601).fill(0), borderColor: '#39ff14', borderWidth: 2.5, pointRadius: 0, fill: false }}]
        }},
        options: {{
            responsive: true, maintainAspectRatio: false,
            plugins: {{ title: {{ display: true, text: 'DIGITAL OSCILLOSCOPE (Current Freq: 1500 Hz)', color: '#00f0ff', font: {{ size: 14, weight: 'bold' }} }}, legend: {{ display: false }} }},
            scales: {{
                x: {{ title: {{ display: true, text: 'Time (ms)', color: '#888' }}, ticks: {{ color: '#666', maxTicksLimit: 8 }}, grid: {{ color: '#222' }} }},
                y: {{ min: -1.1, max: 1.1, title: {{ display: true, text: 'Amplitude (V)', color: '#888' }}, ticks: {{ color: '#666' }}, grid: {{ color: '#222' }} }}
            }}
        }}
    }});

    // Конфигурация Профиля Стрижня (убрали borderDash, чтобы ничего не ломалось)
    const ctxRod = document.getElementById('rodCanvas').getContext('2d');
    const rodChart = new Chart(ctxRod, {{
        type: 'line',
        data: {{
            labels: x_points.map(x => x.toFixed(3)),
            datasets: [
                {{ label: 'Envelope', data: new Array(151).fill(0), borderColor: waveColor, borderWidth: 3, pointRadius: 0, fill: false }}
            ]
        }},
        options: {{
            responsive: true, maintainAspectRatio: false,
            plugins: {{ title: {{ display: true, text: 'Standing Wave Profile inside the Rod', color: '#00f0ff', font: {{ size: 14, weight: 'bold' }} }}, legend: {{ display: false }} }},
            scales: {{
                x: {{ title: {{ display: true, text: 'Position along the rod (m)', color: '#888' }}, ticks: {{ color: '#666', maxTicksLimit: 6 }}, grid: {{ color: '#222' }} }},
                y: {{ min: -1.2, max: 1.2, title: {{ display: true, text: 'Relative Displacement', color: '#888' }}, ticks: {{ color: '#666' }}, grid: {{ color: '#222' }} }}
            }}
        }}
    }});

    function updateVisuals(freq) {{
        let amp = 1.0 / Math.sqrt(1.0 + Math.pow(Q, 2) * Math.pow((freq/f0 - f0/freq), 2));
        if (amp < 0.02) amp = 0.02;
        
        const y_scope = t_points.map(t => amp * Math.sin(2 * Math.PI * freq * t));
        const y_rod_pos = x_points.map(x => amp * Math.cos(Math.PI * x / rodLength));
        
        scopeChart.data.datasets[0].data = y_scope;
        scopeChart.options.plugins.title.text = 'DIGITAL OSCILLOSCOPE (Current Freq: ' + freq + ' Hz)';
        scopeChart.update('none'); 
        
        rodChart.data.datasets[0].data = y_rod_pos;
        rodChart.update('none');
    }}

    const slider = document.getElementById('realtime_slide');
    const valDisplay = document.getElementById('freq_val');
    
    updateVisuals(1500);

    slider.addEventListener('input', (e) => {{
        const val = parseInt(e.target.value);
        valDisplay.innerText = val;
        updateVisuals(val);
    }});
</script>
"""

with col2:
    components.html(js_engine_code, height=640)
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
fig = go.Figure()

# Векторы времени и координат
t = np.linspace(0, 0.002, 150)
x = np.linspace(0, rod_length, 80)

# 1. Создаем базовые («стартовые») кривые для начальной частоты 1500 Гц
amp_start = 1.0 / np.sqrt(1.0 + Q**2 * (1500/f0 - f0/1500)**2)
if amp_start < 0.02: amp_start = 0.02

# Кривая осциллографа (индекс трассы 0)
fig.add_trace(go.Scatter(x=t*1000, y=amp_start*np.sin(2*np.pi*1500*t), mode='lines', line=dict(color='#39ff14', width=3), name="Oscilloscope"))
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
