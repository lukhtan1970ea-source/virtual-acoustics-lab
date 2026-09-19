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

col1, col2 = st.columns([1, 2]) # Левая колонка чуть уже, правая шире

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
line_color = mat_data["color"]

# Высокоскоростной интерактивный движок на чистом JavaScript + Chart.js
js_engine_code = f"""
<div id="controls" style="font-family: Arial, sans-serif; color: white; background: #1e222b; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
    <label style="display:block; margin-bottom:8px; font-weight:bold; font-size:16px;">
        Signal Generator Frequency: <span id="freq_val" style="color:#00f0ff; font-size:18px;">1500</span> Hz
    </label>
    <input type="range" id="realtime_slide" min="1000" max="6000" value="1500" step="1" 
        style="width: 100%; accent-color: #00f0ff; cursor: pointer;">
</div>

<div style="position: relative; height:260px; width:100%;"><canvas id="scopeCanvas"></canvas></div>
<div style="position: relative; height:260px; width:100%; margin-top:20px;"><canvas id="rodCanvas"></canvas></div>

<!-- Подключаем легкую и быструю библиотеку Chart.js -->
<script src="https://jsdelivr.net"></script>

<script>
    const f0 = {f0};
    const Q = 50; 
    const rodLength = 0.500;
    const waveColor = "{line_color}";
    
    // Генерируем статические сетки осей
    const t_points = [];
    const t_labels = [];
    for(let i=0; i<=150; i++) {{
        let t = (0.002 / 150) * i;
        t_points.push(t);
        t_labels.push((t * 1000).toFixed(2));
    }}
    
    const x_points = [];
    const x_labels = [];
    for(let i=0; i<=80; i++) {{
        let x = (rodLength / 80) * i;
        x_points.push(x);
        x_labels.push(x.toFixed(3));
    }}

    // Конфігурація Осцилографа
    const ctxScope = document.getElementById('scopeCanvas').getContext('2d');
    const scopeChart = new Chart(ctxScope, {{
        type: 'line',
        data: {{
            labels: t_labels,
            datasets: [{{ label: 'Signal (V)', data: new Array(151).fill(0), borderColor: '#39ff14', borderWidth: 2.5, pointRadius: 0, fill: false }}]
        }},
        options: {{
            responsive: true, maintainAspectRatio: false,
            plugins: {{ title: {{ display: true, text: 'DIGITAL OSCILLOSCOPE', color: '#00f0ff', font: {{ size: 14 }} }}, legend: {{ display: false }} }},
            scales: {{
                x: {{ title: {{ display: true, text: 'Time (ms)', color: '#fff' }}, ticks: {{ color: '#aaa', maxTicksLimit: 10 }}, grid: {{ color: '#222' }} }},
                y: {{ min: -1.1, max: 1.1, title: {{ display: true, text: 'Amplitude (V)', color: '#fff' }}, ticks: {{ color: '#aaa' }}, grid: {{ color: '#222' }} }}
            }}
        }}
    }});

    // Конфігурація Стрижня
    const ctxRod = document.getElementById('rodCanvas').getContext('2d');
    const rodChart = new Chart(ctxRod, {{
        type: 'line',
        data: {{
            labels: x_labels,
            datasets: [
                {{ label: 'Envelope +', data: new Array(81).fill(0), borderColor: waveColor, borderWidth: 3, pointRadius: 0, fill: false }},
                {{ label: 'Envelope -', data: new Array(81).fill(0), borderColor: waveColor, borderWidth: 1, borderDash:, pointRadius: 0, fill: false }},
                {{ label: 'Node', data: [{{ x: 40, y: 0 }}], backgroundColor: 'red', pointRadius: 6, showLine: false }}
            ]
        }},
        options: {{
            responsive: true, maintainAspectRatio: false,
            plugins: {{ title: {{ display: true, text: 'Standing Wave Profile inside the Rod', color: '#00f0ff', size: 14 }}, legend: {{ display: false }} }},
            scales: {{
                x: {{ title: {{ display: true, text: 'Position along the rod (m)', color: '#fff' }}, ticks: {{ color: '#aaa', maxTicksLimit: 10 }}, grid: {{ color: '#222' }} }},
                y: {{ min: -1.2, max: 1.2, title: {{ display: true, text: 'Relative Displacement', color: '#fff' }}, ticks: {{ color: '#aaa' }}, grid: {{ color: '#222' }} }}
            }}
        }}
    }});

    // Функція миттєвого оновлення
    function updateVisuals(freq) {{
        let amp = 1.0 / Math.sqrt(1.0 + Math.pow(Q, 2) * Math.pow((freq/f0 - f0/freq), 2));
        if (amp < 0.02) amp = 0.02;
        
        // Оновлюємо дані масивів
        const y_scope = t_points.map(t => amp * Math.sin(2 * Math.PI * freq * t));
        const y_rod_pos = x_points.map(x => amp * Math.cos(Math.PI * x / rodLength));
        const y_rod_neg = y_rod_pos.map(y => -y);
        
        scopeChart.data.datasets[0].data = y_scope;
        scopeChart.options.plugins.title.text = 'DIGITAL OSCILLOSCOPE (Current Freq: ' + freq + ' Hz)';
        scopeChart.update('none'); // Оновлення без зайвих анімацій інтерфейсу (максимальна швидкість)
        
        rodChart.data.datasets[0].data = y_rod_pos;
        rodChart.data.datasets[1].data = y_rod_neg;
        rodChart.update('none');
    }}

    // Слухач подій на повзунок (mousemove / input)
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
    # Отрисовка высокоскоростного HTML-движка
    components.html(js_engine_code, height=620)

