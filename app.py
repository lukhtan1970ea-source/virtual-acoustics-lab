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

# Расчет физики резонанса для передачи в браузер
E = mat_data["E"]
rho = mat_data["rho"]
v_sound = np.sqrt(E / rho)
f0 = v_sound / (2 * 0.500)
line_color = mat_data["color"]

# Высокоскоростной интерактивный движок на Plotly.js без использования тяжелых кадров Python
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

<script src="https://plot.ly"></script>

<script>
    const f0 = {f0};
    const Q = 50; 
    const rodLength = 0.500;
    const waveColor = "{line_color}";
    
    // Генерируем 800 точек по оси времени для ИДЕАЛЬНОЙ аналоговой плавности синуса
    const t_arr = [];
    for(let i=0; i<=800; i++) t_arr.push((0.002 / 800) * i);
    const t_ms = t_arr.map(t => t * 1000);
    
    // 200 точек для профиля стержня
    const x_arr = [];
    for(let i=0; i<=200; i++) x_arr.push((rodLength / 200) * i);

    function updateExperiment(freq) {{
        let amp = 1.0 / Math.sqrt(1.0 + Math.pow(Q, 2) * Math.pow((freq/f0 - f0/freq), 2));
        if (amp < 0.015) amp = 0.015; 
        
        const y_scope = t_arr.map(t => amp * Math.sin(2 * Math.PI * freq * t));
        const y_rod = x_arr.map(x => amp * Math.cos(Math.PI * x / rodLength));
        const y_rod_neg = y_rod.map(y => -y);
        
        // Метод animate мгновенно перерисовывает линию, стирая старую (без полупрозрачности)
        Plotly.animate('scope_chart', {{
            data: [{{y: y_scope}}]
        }}, {{transition: {{duration: 0}}, frame: {{duration: 0, redraw: false}}}});
        
        Plotly.relayout('scope_chart', {{'title.text': 'DIGITAL OSCILLOSCOPE (Current Freq: ' + freq + ' Hz)'}});
        
        Plotly.animate('rod_chart', {{
            data: [{{y: y_rod}}, {{y: y_rod_neg}}]
        }}, {{transition: {{duration: 0}}, frame: {{duration: 0, redraw: false}}}});
    }}

    const isDark = window.parent.document.body.getAttribute('data-test-script-state') !== 'light';
    const gridColor = 'rgba(128, 128, 128, 0.2)';
    const textColor = '#ffffff';

    const layout_scope = {{
        title: {{ text: 'DIGITAL OSCILLOSCOPE (Current Freq: 1500 Hz)', font: {{ color: '#00f0ff', size: 14, family: 'Arial' }} }},
        xaxis: {{ title: 'Time (ms)', range: [0, 2.0], gridcolor: gridColor, tickfont: {{color: textColor}} }},
        yaxis: {{ title: 'Amplitude (V)', range: [-1.1, 1.1], gridcolor: gridColor, tickfont: {{color: textColor}} }},
        paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
        margin: {{ l: 50, r: 20, t: 45, b: 40 }}, height: 290, showlegend: false
    }};

    const layout_rod = {{
        title: {{ text: 'Standing Wave Profile inside the Rod', font: {{ color: '#00f0ff', size: 14, family: 'Arial' }} }},
        xaxis: {{ title: 'Position along the rod (m)', range: [0, rodLength], gridcolor: gridColor, tickfont: {{color: textColor}} }},
        yaxis: {{ title: 'Relative Displacement', range: [-1.2, 1.2], gridcolor: gridColor, tickfont: {{color: textColor}} }},
        paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
        margin: {{ l: 50, r: 20, t: 45, b: 40 }}, height: 290, showlegend: false,
        shapes: [{{ type: 'line', x0: 0, y0: 0, x1: rodLength, y1: 0, line: {{ color: 'gray', width: 2, dash: 'dot' }} }}]
    }};

    Plotly.newPlot('scope_chart', [{{ x: t_ms, y: t_arr.map(t => 0), mode: 'lines', line: {{ color: '#39ff14', width: 2.5 }} }}], layout_scope, {{displayModeBar: false}});
    Plotly.newPlot('rod_chart', [
        {{ x: x_arr, y: x_arr.map(x => 0), mode: 'lines', line: {{ color: waveColor, width: 3 }} }},
        {{ x: x_arr, y: x_arr.map(x => 0), mode: 'lines', line: {{ color: waveColor, width: 1, dash: 'dash' }} }},
        {{ x: [rodLength/2], y:, mode: 'markers', marker: {{ color: 'red', size: 10 }} }}
    ], layout_rod, {{displayModeBar: false}});

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
    components.html(js_engine_code, height=640)
