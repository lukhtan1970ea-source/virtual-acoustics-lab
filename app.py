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

col1, col2 = st.columns([1, 2])


with col1:
    st.header("⚙️ Controls")
    material = st.selectbox("Select Rod Material:", list(MATERIALS.keys()))
    mat_data = MATERIALS[material]
    
    st.info("📏 **Rod Specifications:**\n* Length (L): 0.500 m\n* Diameter (d): 15.0 mm")
    
    st.markdown("""
    **STUDENT GUIDE:**
    1. Drag the custom slider below.
    2. The graphs will update **instantly in real-time** as you move your mouse.
    3. Find the peak where Oscilloscope Amplitude reaches max values (**1.0 V**).
    """)

    st.write("---")
    st.write("**Drag for Real-Time Tuning:**")

    # JavaScript + HTML5 Custom Real-Time Slider Integration
    # It catches mousemove events and sends data back to Streamlit instantly
    if "live_freq" not in st.session_state:
        st.session_state.live_freq = 1500

    html_slider = f"""
    <div style="font-family: Arial, sans-serif; color: white; background: #1e222b; padding: 15px; border-radius: 8px;">
        <label style="display:block; margin-bottom:8px; font-weight:bold;">Frequency: <span id="freq_val" style="color:#00f0ff;">{st.session_state.live_freq}</span> Hz</label>
        <input type="range" id="realtime_slide" min="1000" max="6000" value="{st.session_state.live_freq}" step="1" 
            style="width: 100%; accent-color: #00f0ff; cursor: pointer;">
    </div>

    <script>
        const slider = document.getElementById('realtime_slide');
        const valDisplay = document.getElementById('freq_val');
        
        // Listen to active dragging (mousemove/input) without waiting for mouseup
        slider.addEventListener('input', (e) => {{
            const val = e.target.value;
            valDisplay.innerText = val;
            
            // Modern Streamlit JS bridge to push data instantly
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: parseInt(val)
            }}, '*');
        }});
    </script>
    """
    
    # Render the custom high-speed slider component
    slider_return = components.html(html_slider, height=95)
    
    # Catch the fast callback value
    # Catch the fast callback value safely
if slider_return is not None and str(slider_return).isdigit():
    st.session_state.live_freq = int(slider_return)


# Extract frequency for plotting
current_freq = st.session_state.live_freq

# Physics Calculations
E = mat_data["E"]
rho = mat_data["rho"]
rod_length = 0.500

v_sound = np.sqrt(E / rho)
f0 = v_sound / (2 * rod_length)

Q = 200 
amp = 1.0 / np.sqrt(1.0 + Q**2 * (current_freq/f0 - f0/current_freq)**2)

# --- 1. DIGITAL OSCILLOSCOPE (Plotly) ---
t = np.linspace(0, 0.002, 150) # Lightweight points vector
v_signal = amp * np.sin(2 * np.pi * current_freq * t)

fig_scope = go.Figure()
fig_scope.add_trace(go.Scatter(x=t*1000, y=v_signal, mode='lines', line=dict(color='#39ff14', width=3)))
fig_scope.update_layout(
    title=dict(text="DIGITAL OSCILLOSCOPE (Receiver Output)", font=dict(color='#00f0ff', size=14, family="Arial")),
    xaxis=dict(title="Time (ms)", range=[0, 2], gridcolor='#222222'),
    yaxis=dict(title="Amplitude (V)", range=[-1.1, 1.1], gridcolor='#222222'),
    template="plotly_dark",
    margin=dict(l=40, r=20, t=40, b=40),
    height=320,
    showlegend=False
)

# --- 2. STANDING WAVE PROFILE (Plotly) ---
x = np.linspace(0, rod_length, 80)
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
    st.plotly_chart(fig_scope, use_container_width=True, key="scope_chart")
    st.plotly_chart(fig_rod, use_container_width=True, key="rod_chart")



