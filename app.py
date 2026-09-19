import streamlit as st
import numpy as np
import plotly.graph_objects as go
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

col1, col2 = st.columns([1, 2]) # Левая колонка чуть уже, правая с графиками — шире

with col1:
    st.header("⚙️ Controls")
    material = st.selectbox("Select Rod Material:", list(MATERIALS.keys()))
    mat_data = MATERIALS[material]
    
    st.info("📏 **Rod Specifications:**\n* Length (L): 0.500 m\n* Diameter (d): 15.0 mm")
    
    st.markdown("""
    **STUDENT GUIDE:**
    1. Drag the custom slider below.
    2. Watch the graphs update **instantly** in real-time.
    3. Find the peak frequency where Oscilloscope Amplitude reaches exactly **1.0 V**.
    """)

    st.write("---")
    st.write("**Drag for Real-Time Tuning:**")

    # Сессионные переменные для отслеживания частоты
    if "live_freq" not in st.session_state:
        st.session_state.live_freq = 1500
    if "prev_freq" not in st.session_state:
        st.session_state.prev_freq = 1500

    html_slider = f"""
    <div style="font-family: Arial, sans-serif; color: white; background: #1e222b; padding: 15px; border-radius: 8px;">
        <label style="display:block; margin-bottom:8px; font-weight:bold;">Frequency: <span id="freq_val" style="color:#00f0ff;">{st.session_state.live_freq}</span> Hz</label>
        <input type="range" id="realtime_slide" min="1000" max="6000" value="{st.session_state.live_freq}" step="1" 
            style="width: 100%; accent-color: #00f0ff; cursor: pointer;">
    </div>

    <script>
        const slider = document.getElementById('realtime_slide');
        const valDisplay = document.getElementById('freq_val');
        
        slider.addEventListener('input', (e) => {{
            const val = e.target.value;
            valDisplay.innerText = val;
            
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: parseInt(val)
            }}, '*');
        }});
    </script>
    """
    
    slider_return = components.html(html_slider, height=95)
    
    if slider_return is not None and str(slider_return).isdigit():
        st.session_state.live_freq = int(slider_return)

# Если частота сдвинулась, принудительно перезапускаем контекст расчетов
if st.session_state.live_freq != st.session_state.prev_freq:
    st.session_state.prev_freq = st.session_state.live_freq
    st.rerun()

current_freq = st.session_state.live_freq

# --- МАТЕМАТИКА И ФИЗИКА (Выполняется СТРОГО при каждом изменении) ---
E = mat_data["E"]
rho = mat_data["rho"]
rod_length = 0.500

v_sound = np.sqrt(E / rho)
f0 = v_sound / (2 * rod_length)

# Добротность Q=60 (сделана чуть шире, чтобы студенты легче замечали подъем волны)
Q = 60 
amp = 1.0 / np.sqrt(1.0 + Q**2 * (current_freq/f0 - f0/current_freq)**2)

# Базовый шум прибора, чтобы линия никогда не была идеально мертвой
if amp < 0.015:
    amp = 0.015

# --- ОТРИСОВКА ГРАФИКОВ ---
# 1. Осциллограф
t = np.linspace(0, 0.002, 200) 
v_signal = amp * np.sin(2 * np.pi * current_freq * t)

fig_scope = go.Figure()
fig_scope.add_trace(go.Scatter(x=t*1000, y=v_signal, mode='lines', line=dict(color='#39ff14', width=3)))
fig_scope.update_layout(
    title=dict(text=f"DIGITAL OSCILLOSCOPE (Current Freq: {current_freq} Hz)", font=dict(color='#00f0ff', size=14, family="Arial")),
    xaxis=dict(title="Time (ms)", range=[0, 2.0], gridcolor='#222222'),
    yaxis=dict(title="Amplitude (V)", range=[-1.1, 1.1], gridcolor='#222222'),
    template="plotly_dark",
    margin=dict(l=40, r=20, t=40, b=40),
    height=320,
    showlegend=False
)

# 2. Стоячая волна в стрижне
x = np.linspace(0, rod_length, 100)
wave_profile = amp * np.cos(np.pi * x / rod_length)

fig_rod = go.Figure()
fig_rod.add_trace(go.Scatter(x=x, y=wave_profile, mode='lines', line=dict(color=mat_data["color"], width=3), name="Displacement"))
fig_rod.add_trace(go.Scatter(x=x, y=-wave_profile, mode='lines', line=dict(color=mat_data["color"], width=1, dash='dash'), showlegend=False))
fig_rod.add_shape(type="line", x0=0, y0=0, x1=rod_length, y1=0, line=dict(color="gray", width=2, dash="dot"))
fig_rod.add_trace(go.Scatter(x=[rod_length/2], y=[0], mode='markers', marker=dict(color='red', size=12), name="Clamped Center (Node)"))

fig_rod.update_layout(
    title=dict(text=f"Standing Wave Profile: {material} Rod", font=dict(color='#00f0ff', size=14, family="Arial")),
    xaxis=dict(title="Position along the rod (m)", range=[0, rod_length], gridcolor='#222222'),
    yaxis=dict(title="Relative Displacement", range=[-1.2, 1.2], gridcolor='#222222'),
    template="plotly_dark",
    margin=dict(l=40, r=20, t=40, b=40),
    height=320,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

with col2:
    st.plotly_chart(fig_scope, use_container_width=True, key=f"scope_{current_freq}")
    st.plotly_chart(fig_rod, use_container_width=True, key=f"rod_{current_freq}")





