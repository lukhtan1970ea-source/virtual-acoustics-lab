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
