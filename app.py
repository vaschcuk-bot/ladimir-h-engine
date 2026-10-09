
import streamlit as st
import plotly.graph_objects as go

# ============================================================
# DIGITAL TWIN EARTH: H-ENGINE
# Синхронизированная архитектура состояния Streamlit
# ============================================================

st.set_page_config(
    page_title="Digital Twin Earth: H-Engine",
    page_icon="🌐",
    layout="wide",
)

PARAMS = ("V", "R", "T", "Q", "M")
MIN_VAL = 0.10
MAX_VAL = 2.00
STEP = 0.05

LABELS = {
    "V": "V — Объём / Силовой аппарат",
    "R": "R — Ресурсы / Бензин",
    "T": "T — Время / Дальний свет",
    "Q": "Q — Качество / Надёжность",
    "M": "M — Смысл / Путеводная звезда",
}

PRESETS = {
    "Эталон (Гармония)": {
        "V": 1.00, "R": 1.00, "T": 1.00,
        "Q": 1.00, "M": 1.00,
    },
    "Кризис Смысла (M = 0.2)": {
        "V": 1.00, "R": 1.00, "T": 1.00,
        "Q": 1.00, "M": 0.20,
    },
    "Короткий чек / Суета (T = 0.3)": {
        "V": 1.00, "R": 1.00, "T": 0.30,
        "Q": 1.00, "M": 1.00,
    },
    "Застой / Силовой зажим": {
        "V": 1.60, "R": 0.50, "T": 0.30,
        "Q": 0.40, "M": 0.20,
    },
    "Технологический / Долгосрочный рывок": {
        "V": 1.00, "R": 1.40, "T": 1.40,
        "Q": 1.20, "M": 1.30,
    },
}


def clamp(value):
    """Ограничение диапазона с округлением до сотых."""
    return round(max(MIN_VAL, min(MAX_VAL, value)), 2)


def read_model():
    """Получить единый снимок пяти параметров."""
    return {k: float(st.session_state[f"input_{k}"])
            for k in PARAMS}


def write_model(values):
    """Синхронно записать модель и ключи всех виджетов."""
    for k in PARAMS:
        value = clamp(float(values[k]))
        st.session_state[f"input_{k}"] = value
        st.session_state[f"_model_{k}"] = value


def update_inputs(changed_key):
    """
    Вызывается до перерисовки интерфейса.
    Изменённое значение уже находится в input_<key>.
    Остальные ключи можно безопасно обновить здесь.
    """
    new_value = float(st.session_state[f"input_{changed_key}"])
    old_value = float(st.session_state[f"_model_{changed_key}"])
    delta = round(new_value - old_value, 2)

    # Защита от повторной обработки неизменившегося значения.
    if abs(delta) < 0.001:
        return

    values = read_model()
    values[changed_key] = clamp(new_value)

    # Матрица перекрёстных связей исходной модели.
    effects = {
        "M": {"Q": 0.65, "R": 0.45, "T": 0.50, "V": -0.40},
        "T": {"Q": 0.55, "M": 0.50, "R": 0.40, "V": -0.35},
        "R": {"Q": 0.50, "T": 0.40, "M": 0.30, "V": 0.20},
        "Q": {"M": 0.50, "T": 0.35, "R": 0.30},
    }

    if changed_key in effects:
        for target, coefficient in effects[changed_key].items():
            values[target] = clamp(
                values[target] + coefficient * delta
            )

    elif changed_key == "V" and delta > 0:
        values["Q"] = clamp(values["Q"] - 0.45 * delta)
        values["M"] = clamp(values["M"] - 0.55 * delta)
        values["R"] = clamp(values["R"] - 0.35 * delta)
        values["T"] = clamp(values["T"] - 0.30 * delta)

    # При снижении V исходная модель не задаёт обратную коррекцию.
    write_model(values)


def apply_preset():
    """Пресет заменяет все пять значений как одна операция."""
    preset_name = st.session_state["selected_preset"]
    write_model(PRESETS[preset_name])


# ============================================================
# ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ
# ============================================================

if "_initialized" not in st.session_state:
    for k in PARAMS:
        st.session_state[f"input_{k}"] = 1.00
        st.session_state[f"_model_{k}"] = 1.00

    st.session_state["selected_preset"] = "Эталон (Гармония)"
    st.session_state["_initialized"] = True

# ============================================================
# ЗАГОЛОВОК И ПАНЕЛИ
# ============================================================

st.title("🌐 Digital Twin Earth: H-Engine Simulator")
st.caption(
    "Автор концепта: В. В. Ващук (Dedushka LADiMIR) | "
    "Антикризисная модель гармонии систем"
)

col_control, col_display = st.columns([1, 1])

with col_control:
    st.subheader("Панель управления системой")

    st.selectbox(
        "Готовый пресет сценария:",
        options=list(PRESETS.keys()),
        key="selected_preset",
        on_change=apply_preset,
    )

    st.divider()

    for k in PARAMS:
        st.number_input(
            LABELS[k],
            min_value=MIN_VAL,
            max_value=MAX_VAL,
            step=STEP,
            format="%.2f",
            key=f"input_{k}",
            on_change=update_inputs,
            args=(k,),
        )

    st.caption(
        "Изменение одного параметра автоматически корректирует "
        "связанные параметры по заданной матрице."
    )

# Единый снимок для всех вычислений и визуализаций.
model = read_model()
V, R, T, Q, M = (model[k] for k in PARAMS)

# ============================================================
# РАСЧЁТ МЕТРИК
# ============================================================

sigma = sum(model.values())

# Среднее абсолютное отклонение от эталона 1.0.
delta = sum(abs(model[k] - 1.0) for k in PARAMS) / len(PARAMS)

V_safe = max(V, 0.001)
H = (Q * M * R * T) / (V_safe * (1.0 + delta))

is_collapse = (
    delta >= 0.60
    or H <= 0.005
    or M <= 0.15
)

is_warning = delta > 0.35 or H < 0.05

# ============================================================
# ПАНЕЛЬ СОСТОЯНИЯ
# ============================================================

with col_display:
    st.subheader("Состояние и фазовая зона")

    if is_collapse:
        st.error("🚨 СИСТЕМНЫЙ КОЛЛАПС / КРАХ")
        status_color = "#FF2A2A"
    elif is_warning:
        st.warning("⚠️ ПРЕДАВАРИЙНОЕ СОСТОЯНИЕ / КРИЗИС")
        status_color = "#FFA500"
    else:
        st.success("✅ УСТОЙЧИВОЕ СОСТОЯНИЕ")
        status_color = "#00E676"

    m1, m2, m3 = st.columns(3)

    m1.metric("Сумма ΣXi", f"{sigma:.2f} / 5.00")
    m2.metric("Дисбаланс Δ", f"{delta:.4f}")
    m3.metric("Индекс гармонии H", f"{H:.6f}")

    st.caption(
        "Статус вычисляется по порогам заданной модели, "
        "а не является подтверждённым прогнозом реальной системы."
    )

    # Полярная диаграмма.
    axes = ["V (Объём)", "R (Ресурсы)", "T (Время)",
            "Q (Качество)", "M (Смысл)"]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[V, R, T, Q, M, V],
        theta=axes + [axes[0]],
        fill="toself",
        name="Текущее состояние",
        line=dict(color=status_color, width=3),
    ))

    fig.add_trace(go.Scatterpolar(
        r=[1.0] * 6,
        theta=axes + [axes[0]],
        mode="lines",
        name="Эталон (1.0)",
        line=dict(color="white", dash="dash", width=2),
    ))

    fig.update_layout(
        template="plotly_dark",
        height=430,
        margin=dict(l=35, r=35, t=35, b=35),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 2.0],
                tick0=0,
                dtick=0.5,
            ),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.18),
    )

    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# ТАБЛИЦА ПАРАМЕТРОВ
# ============================================================

st.subheader("Контроль параметров")

st.dataframe(
    [
        {
            "Параметр": k,
            "Значение": f"{model[k]:.2f}",
            "Отклонение от 1.0": f"{model[k] - 1.0:+.2f}",
        }
        for k in PARAMS
    ],
    hide_index=True,
    use_container_width=True,
)
