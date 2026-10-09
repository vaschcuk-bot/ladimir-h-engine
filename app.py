import streamlit as st
import plotly.graph_objects as go

# Настройка страницы
st.set_page_config(
    page_title="Digital Twin Earth: H-Engine",
    page_icon="🌐",
    layout="wide"
)

# 1. ПРЕПРОФИЛИ И ИНИЦИАЛИЗАЦИЯ
PRESETS = {
    "Эталон (Гармония)": {"V": 1.00, "R": 1.00, "T": 1.00, "Q": 1.00, "M": 1.00},
    "Кризис Смысла (М = 0.2)": {"V": 1.00, "R": 1.00, "T": 1.00, "Q": 1.00, "M": 0.20},
    "Короткий чек / Суета (T = 0.3)": {"V": 1.00, "R": 1.00, "T": 0.30, "Q": 1.00, "M": 1.00},
    "Застой / Силовой зажим": {"V": 1.60, "R": 0.50, "T": 0.30, "Q": 0.40, "M": 0.20},
    "Технологический / Долгосрочный рывок": {"V": 1.00, "R": 1.40, "T": 1.40, "Q": 1.20, "M": 1.30},
}

for k in ['V', 'R', 'T', 'Q', 'M']:
    if f"input_{k}" not in st.session_state:
        st.session_state[f"input_{k}"] = 1.00
    if f"prev_{k}" not in st.session_state:
        st.session_state[f"prev_{k}"] = 1.00

def clamp(val):
    return max(0.10, min(2.00, round(val, 2)))

# Динамический пересчет: обновляем непосредственно ключи виджетов input_*
def update_inputs(changed_key):
    new_val = st.session_state[f"input_{changed_key}"]
    old_val = st.session_state[f"prev_{changed_key}"]
    delta = round(new_val - old_val, 2)

    if abs(delta) < 0.001:
        return

    if changed_key == 'M':
        st.session_state['input_Q'] = clamp(st.session_state['input_Q'] + 0.65 * delta)
        st.session_state['input_R'] = clamp(st.session_state['input_R'] + 0.45 * delta)
        st.session_state['input_T'] = clamp(st.session_state['input_T'] + 0.50 * delta)
        st.session_state['input_V'] = clamp(st.session_state['input_V'] - 0.40 * delta)
    elif changed_key == 'T':
        st.session_state['input_Q'] = clamp(st.session_state['input_Q'] + 0.55 * delta)
        st.session_state['input_M'] = clamp(st.session_state['input_M'] + 0.50 * delta)
        st.session_state['input_R'] = clamp(st.session_state['input_R'] + 0.40 * delta)
        st.session_state['input_V'] = clamp(st.session_state['input_V'] - 0.35 * delta)
    elif changed_key == 'R':
        st.session_state['input_Q'] = clamp(st.session_state['input_Q'] + 0.50 * delta)
        st.session_state['input_T'] = clamp(st.session_state['input_T'] + 0.40 * delta)
        st.session_state['input_M'] = clamp(st.session_state['input_M'] + 0.30 * delta)
        st.session_state['input_V'] = clamp(st.session_state['input_V'] + 0.20 * delta)
    elif changed_key == 'Q':
        st.session_state['input_M'] = clamp(st.session_state['input_M'] + 0.50 * delta)
        st.session_state['input_T'] = clamp(st.session_state['input_T'] + 0.35 * delta)
        st.session_state['input_R'] = clamp(st.session_state['input_R'] + 0.30 * delta)
    elif changed_key == 'V' and delta > 0:
        st.session_state['input_Q'] = clamp(st.session_state['input_Q'] - 0.45 * delta)
        st.session_state['input_M'] = clamp(st.session_state['input_M'] - 0.55 * delta)
        st.session_state['input_R'] = clamp(st.session_state['input_R'] - 0.35 * delta)
        st.session_state['input_T'] = clamp(st.session_state['input_T'] - 0.30 * delta)

    # Запоминаем новые текущие значения как предыдущие
    for k in ['V', 'R', 'T', 'Q', 'M']:
        st.session_state[f"prev_{k}"] = st.session_state[f"input_{k}"]

def apply_preset():
    preset = PRESETS[st.session_state.selected_preset]
    for k, v in preset.items():
        st.session_state[f"input_{k}"] = v
        st.session_state[f"prev_{k}"] = v

# 2. ИНТЕРФЕЙС
st.title("🌐 Digital Twin Earth: H-Engine Simulator")
st.caption("Автор концепта: В. В. Ващук (Dedushka LADiMIR) | Антикризисная модель Гармонии Систем")

col_control, col_display = st.columns([1, 1])

with col_control:
    st.subheader("Панель управления государством / системой")
    
    st.selectbox("Готовый пресет сценария:", list(PRESETS.keys()), key="selected_preset", on_change=apply_preset)
    st.write("---")
    
    st.number_input("V (Объём / Силовой аппарат):", min_value=0.10, max_value=2.00, step=0.05, format="%.2f", key="input_V", on_change=update_inputs, args=('V',))
    st.number_input("R (Ресурсы / Бензин):", min_value=0.10, max_value=2.00, step=0.05, format="%.2f", key="input_R", on_change=update_inputs, args=('R',))
    st.number_input("T (Время / Дальний свет):", min_value=0.10, max_value=2.00, step=0.05, format="%.2f", key="input_T", on_change=update_inputs, args=('T',))
    st.number_input("Q (Качество / Надежность):", min_value=0.10, max_value=2.00, step=0.05, format="%.2f", key="input_Q", on_change=update_inputs, args=('Q',))
    st.number_input("M (Смысл / Путеводная звезда):", min_value=0.10, max_value=2.00, step=0.05, format="%.2f", key="input_M", on_change=update_inputs, args=('M',))

# 3. РАСЧЕТ И МЕТРИКИ
V = st.session_state['input_V']
R = st.session_state['input_R']
T = st.session_state['input_T']
Q = st.session_state['input_Q']
M = st.session_state['input_M']

delta = (abs(V - 1.0) + abs(R - 1.0) + abs(T - 1.0) + abs(Q - 1.0) + abs(M - 1.0)) / 5.0
V_safe = V if V > 0 else 0.001
H = (Q * M * R * T) / (V_safe * (1.0 + delta))
is_collapse = (delta >= 0.60) or (H <= 0.005) or (M <= 0.15)

with col_display:
    st.subheader("Состояние и фазовая зона")
    
    if is_collapse:
        st.error("🚨 ФАЗОВЫЙ ПЕРЕХОД: СИСТЕМНЫЙ КОЛЛАПС / КРАХ")
    elif delta > 0.35 or H < 0.05:
        st.warning("⚠️ ПРЕДАВАРИЙНОЕ СОСТОЯНИЕ / КРИЗИС")
    else:
        st.success("✅ УСТОЙЧИВОЕ ГАРМОНИЧНОЕ СОСТОЯНИЕ")

    m1, m2, m3 = st.columns(3)
    m1.metric("Сумма ΣXi", f"{V+R+T+Q+M:.2f} / 5.0")
    m2.metric("Дисбаланс Δ", f"{delta:.4f}")
    m3.metric("Индекс Гармонии H", f"{H:.6f}")

    # РАДАР
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[V, R, T, Q, M],
        theta=['V (Volume)', 'R (Resources)', 'T (Time)', 'Q (Quality)', 'M (Meaning)'],
        fill='toself',
        name='Состояние системы',
        line_color="#FF2A2A" if is_collapse else ("#FFA500" if delta > 0.35 else "#00E676")
    ))
    fig.add_trace(go.Scatterpolar(
        r=[1.0]*5,
        theta=['V (Volume)', 'R (Resources)', 'T (Time)', 'Q (Quality)', 'M (Meaning)'],
        fill='none', name='Эталон (1.0)', line=dict(color='white', dash='dash')
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 2.0])), template="plotly_dark", height=380)
    st.plotly_chart(fig, use_container_width=True)
