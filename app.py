import streamlit as st
import numpy as np
import streamlit.components.v1 as components

# --- PHYSICAL CONSTANTS (9 Materials) ---
MATERIALS = {
    "Steel": {"E": 2.0e11, "rho": 7800},
    "Aluminum": {"E": 0.7e11, "rho": 2700},
    "Copper": {"E": 1.1e11, "rho": 8900},
    "Iron": {"E": 2.1e11, "rho": 7870},
    "Lead": {"E": 0.16e11, "rho": 11340},
    "Tungsten": {"E": 4.1e11, "rho": 19250},
    "Titanium": {"E": 1.15e11, "rho": 4540},
    "Gold": {"E": 0.78e11, "rho": 19300},
    "Silver": {"E": 0.83e11, "rho": 10500}
}

st.set_page_config(page_title="Virtual Lab: Young's Modulus", layout="wide")

st.title("🔬 Virtual Acoustics Lab")
st.subheader("Dynamic Determination of Young's Modulus via Standing Waves")

col1, col2 = st.columns([1, 2]) # Левая колонка чуть уже, правая с графиками — шире

with col1:
    st.header("⚙️ Controls")
    material = st.selectbox("Select Rod Material:", list(MATERIALS.keys()))
    mat_data = MATERIALS[material]
    
    st.info("📏 **Rod Specifications:**\n* Length (L): 0.500 m\n* Diameter (d): 15.0 mm")
    
    st.markdown("""
    **STUDENT GUIDE:**
    1. Drag the slider inside the workspace.
    2. The graphs will update **instantly in real-time** as you move the mouse.
    3. Find the peak frequency where Oscilloscope Amplitude reaches **1.0 V**.
    """)

# Рассчитываем теоретическую частоту резонанса для передачи в JavaScript
E = mat_data["E"]
rho = mat_data["rho"]
v_sound = np.sqrt(E / rho)
f0 = v_sound / (2 * 0.500)

# Высокоскоростной интерактивный движок на чистом JavaScript + Plotly.js
js_engine_code = f"""
<div id="controls" style="font-family: Arial, sans-serif; color: white; background: #1e222b; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
    <label style="display:block; margin-bottom:8px; font-weight:bold; font-size:16px;">
        Signal Generator Frequency: <span id="freq_val" style="color:#00f0ff; font-size:18px;">1500</span> Hz
    </label>
    <input type="range" id="realtime_slide" min="1000" max="6000" value="1500" step="1" 
        style="width: 100%; accent-color: #00f0ff; cursor: pointer;">
</div>

<div id="scope_chart"></div>
<div id="rod_chart" style="margin-top:15px;"></div>

<!-- Подключаем библиотеку Plotly -->
<script src="https://plot.ly"></script>

<script>
    const f0 = {f0};
    const Q = 70; // Ширина резонансного пика
    const rodLength = 0.500;
    
    // Подготовка массивов точек
    const t_arr = [];
    for(let i=0; i<=150; i++) t_arr.push((0.002 / 150) * i);
    
    const x_arr = [];
    for(let i=0; i<=80; i++) x_arr.push((rodLength / 80) * i);

    // Функция мгновенного пересчета графиков прямо в браузере
    function updateExperiment(freq) {{
        let amp = 1.0 / Math.sqrt(1.0 + Math.pow(Q, 2) * Math.pow((freq/f0 - f0/freq), 2));
        if (amp < 0.015) amp = 0.015; // Эмуляция шума
        
        const y_scope = t_arr.map(t => amp * Math.sin(2 * Math.PI * freq * t));
        const y_rod = x_arr.map(x => amp * Math.cos(Math.PI * x / rodLength));
        const y_rod_neg = y_rod.map(y => -y);
        
        // Быстрое обновление линий без перезагрузки холста
        Plotly.restyle('scope_chart', {{y: [y_scope]}});
        Plotly.relayout('scope_chart', {{'title.text': 'DIGITAL OSCILLOSCOPE (Current Freq: ' + freq + ' Hz)'}});
        
        Plotly.restyle('rod_chart', {{y: [y_rod, y_rod_neg]}});
    }}

    // Настройки стилей графиков (Темная тема)
    const layout_scope = {{
        title: {{ text: 'DIGITAL OSCILLOSCOPE (Current Freq: 1500 Hz)', font: {{ color: '#00f0ff', size: 14 }} }},
        xaxis: {{ title: 'Time (ms)', range: [0, 2.0], gridcolor: '#222222' }},
        yaxis: {{ title: 'Amplitude (V)', range: [-1.1, 1.1], gridcolor: '#222222' }},
        paper_bgcolor: '#0e1117', plot_bgcolor: '#0e1117',
        margin: {{ l: 40, r: 20, t: 40, b: 40 }}, height: 280, showlegend: false
    }};

    const layout_rod = {{
        title: {{ text: 'Standing Wave Profile inside the Rod', font: {{ color: '#00f0ff', size: 14 }} }},
        xaxis: {{ title: 'Position along the rod (m)', range: [0, rodLength], gridcolor: '#222222' }},
        yaxis: {{ title: 'Relative Displacement', range: [-1.2, 1.2], gridcolor: '#222222' }},
        paper_bgcolor: '#0e1117', plot_bgcolor: '#0e1117',
        margin: {{ l: 40, r: 20, t: 40, b: 40 }}, height: 280, showlegend: false,
        shapes: [{{ type: 'line', x0: 0, y0: 0, x1: rodLength, y1: 0, line: {{ color: 'gray', width: 2, dash: 'dot' }} }}]
    }};

    // Первичный рендеринг графиков
    Plotly.newPlot('scope_chart', [{{ x: t_arr.map(t => t*1000), y: t_arr.map(t => 0), mode: 'lines', line: {{ color: '#39ff14', width: 3 }} }}], layout_scope, {{displayModeBar: false}});
    Plotly.newPlot('rod_chart', [
        {{ x: x_arr, y: x_arr.map(x => 0), mode: 'lines', line: {{ color: '#00f0ff', width: 3 }} }},
        {{ x: x_arr, y: x_arr.map(x => 0), mode: 'lines', line: {{ color: '#00f0ff', width: 1, dash: 'dash' }} }},
        {{ x: [rodLength/2], y: [0], mode: 'markers', marker: {{ color: 'red', size: 12 }} }} // Координата [0] теперь на месте!
    ], layout_rod, {{displayModeBar: false}});

    // Инициализация ползунка
    const slider = document.getElementById('realtime_slide');
    const valDisplay = document.getElementById('freq_val');
    updateExperiment(1500);

    slider.addEventListener('input', (e) => {{
        const val = parseInt(e.target.value);
        valDisplay.innerText = val;
        updateExperiment(val);
    }});
</script>
"""

with col2:
    components.html(js_engine_code, height=680)



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

col1, col2 = st.columns([1, 2]) # Левая колонка чуть уже, правая шире

with col1:
    st.header("⚙️ Controls")
    material = st.selectbox("Select Rod Material:", list(MATERIALS.keys()))
    mat_data = MATERIALS[material]
    
    st.info("📏 **Rod Specifications:**\n* Length (L): 0.500 m\n* Diameter (d): 15.0 mm")
    
    # Надежный встроенный слайдер (шаг 2 Гц для высокой скорости отклика)
    current_freq = st.slider(
        "Signal Generator Frequency (Hz):", 
        min_value=1000, max_value=6000, value=1500, step=2
    )
    
    st.markdown("""
    **STUDENT GUIDE:**
    1. Click on the slider handle.
    2. Use **Left/Right Keyboard Arrows** for precise 2 Hz tuning.
    3. Find the peak where Oscilloscope Amplitude reaches **1.0 V**.
    """)

# --- ФИЗИЧЕСКИЕ РАСЧЕТЫ НА СТОРОНЕ PYTHON ---
E = mat_data["E"]
rho = mat_data["rho"]
rod_length = 0.500

v_sound = np.sqrt(E / rho)
f0 = v_sound / (2 * rod_length)

# Смягчаем пик (Q=40), чтобы студенты легко «нащупывали» резонанс издалека
Q = 40 
amp = 1.0 / np.sqrt(1.0 + Q**2 * (current_freq/f0 - f0/current_freq)**2)

# Минимальный фоновый шум осциллографа
if amp < 0.02:
    amp = 0.02

# --- ГЕНЕРАЦИЯ ДАННЫХ ДЛЯ ГРАФИКОВ ---
# 1. Данные осциллографа
t = np.linspace(0, 0.002, 120) 
v_signal = amp * np.sin(2 * np.pi * current_freq * t)

fig_scope = go.Figure()
fig_scope.add_trace(go.Scatter(x=t*1000, y=v_signal, mode='lines', line=dict(color='#39ff14', width=3)))
fig_scope.update_layout(
    title=dict(text=f"DIGITAL OSCILLOSCOPE (Current Freq: {current_freq} Hz)", font=dict(color='#00f0ff', size=14)),
    xaxis=dict(title="Time (ms)", range=[0, 2.0], gridcolor='#222222'),
    yaxis=dict(title="Amplitude (V)", range=[-1.1, 1.1], gridcolor='#222222'),
    template="plotly_dark",
    margin=dict(l=40, r=20, t=40, b=40),
    height=300,
    showlegend=False
)

# 2. Данные стоячей волны
x = np.linspace(0, rod_length, 60)
wave_profile = amp * np.cos(np.pi * x / rod_length)

fig_rod = go.Figure()
fig_rod.add_trace(go.Scatter(x=x, y=wave_profile, mode='lines', line=dict(color=mat_data["color"], width=3), name="Displacement"))
fig_rod.add_trace(go.Scatter(x=x, y=-wave_profile, mode='lines', line=dict(color=mat_data["color"], width=1, dash='dash'), showlegend=False))
fig_rod.add_shape(type="line", x0=0, y0=0, x1=rod_length, y1=0, line=dict(color="gray", width=2, dash="dot"))
fig_rod.add_trace(go.Scatter(x=[rod_length/2], y=[0], mode='markers', marker=dict(color='red', size=12), name="Clamped Center (Node)"))

fig_rod.update_layout(
    title=dict(text=f"Standing Wave Profile: {material} Rod", font=dict(color='#00f0ff', size=14)),
    xaxis=dict(title="Position along the rod (m)", range=[0, rod_length], gridcolor='#222222'),
    yaxis=dict(title="Relative Displacement", range=[-1.2, 1.2], gridcolor='#222222'),
    template="plotly_dark",
    margin=dict(l=40, r=20, t=40, b=40),
    height=300,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

with col2:
    st.plotly_chart(fig_scope, use_container_width=True, key="scope_p")
    st.plotly_chart(fig_rod, use_container_width=True, key="rod_p")

