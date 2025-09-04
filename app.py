
import streamlit as st
import math
import base64
import uuid

# =========================
# Page & Background
# =========================
def set_background(image_file_path):
    try:
        with open(image_file_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        st.markdown(f'''
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
            </style>
        ''', unsafe_allow_html=True)
    except Exception:
        pass

st.set_page_config(page_title="🏈 Moneyball Phil: NFL Prop Simulator", layout="centered")
set_background("ChatGPT Image Jul 14, 2025, 09_58_55 AM.png")

st.title("🏈 Moneyball Phil: NFL Prop Simulator (v2.5)")

# =========================
# Session State
# =========================
if "all_props" not in st.session_state:
    st.session_state.all_props = []
if "temp_props" not in st.session_state:
    st.session_state.temp_props = []
if "parlay_pool" not in st.session_state:
    st.session_state.parlay_pool = []

# =========================
# Helpers
# =========================
def implied_prob(odds: float) -> float:
    if odds == 0: return 0.0
    return (abs(odds) / (abs(odds) + 100)) if odds < 0 else (100 / (odds + 100))

def american_to_decimal(odds: float) -> float:
    if odds == 0: return 1.0
    return 1.0 + (odds / 100.0) if odds > 0 else 1.0 + (100.0 / abs(odds))

def ev_calc(true_prob_frac: float, odds: float) -> float:
    return round((true_prob_frac - implied_prob(odds)) * 100, 2)

def get_tier(prob_pct: float) -> str:
    if prob_pct >= 80: return "🟢 Elite"
    elif prob_pct >= 65: return "🟡 Strong"
    elif prob_pct >= 50: return "🟠 Moderate"
    else: return "🔴 Risky"

def logistic_prob(x_value: float, line_value: float, scale: float = 15.0) -> float:
    try:
        p = 1.0 / (1.0 + math.exp(-(x_value - line_value) / scale))
    except OverflowError:
        p = 0.0 if (x_value - line_value) < 0 else 1.0
    return round(p * 100.0, 2)

def classify_def_tier(yds_allowed: float) -> str:
    if yds_allowed < 210: return "🔴 Tough"
    elif yds_allowed <= 240: return "🟡 Average"
    else: return "🟢 Easy"

def apply_defense_adjustments(ypg: float, tpg: float, tier: str) -> tuple[float, float]:
    if tier == "🔴 Tough": return ypg - 10, tpg - 0.2
    elif tier == "🟢 Easy": return ypg + 10, tpg + 0.2
    return ypg, tpg

def add_play(player: str, prop: str, true_prob_pct: float, odds: float, group: str):
    st.session_state.all_props.append({
        "id": str(uuid.uuid4()),
        "Player": player,
        "Prop": prop,
        "True Prob": round(true_prob_pct, 2),
        "Odds": odds,
        "Group": group
    })

def add_temp_play(player: str, prop: str, true_prob_pct: float, odds: float, group: str):
    st.session_state.temp_props.append({
        "id": str(uuid.uuid4()),
        "Player": player,
        "Prop": prop,
        "True Prob": round(true_prob_pct, 2),
        "Odds": odds,
        "Group": group
    })

# =========================
# Render Functions
# =========================
def render_temp_save_controls():
    if not st.session_state.temp_props:
        return
    st.subheader("📝 Save Plays from Latest Simulation")
    to_save = []
    for p in st.session_state.temp_props:
        col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
        with col1:
            st.markdown(f"**{p['Player']} – {p['Prop']}**  \nTrue: `{p['True Prob']}%` | Odds: `{p['Odds']}`")
        with col2:
            ev = ev_calc(p["True Prob"]/100.0, p["Odds"])
            st.markdown(f"EV: `{ev}%`")
        with col3:
            tier = get_tier(p["True Prob"])
            st.markdown(f"Tier: {tier}")
        with col4:
            if st.checkbox("Save", key=f"save_{p['id']}"):
                to_save.append(p)
    if st.button("➕ Add Selected"):
        for p in to_save:
            add_play(p["Player"], p["Prop"], p["True Prob"], p["Odds"], p["Group"])
        st.session_state.temp_props = []
        st.success("Selected plays added to Top Player Board.")

def render_board_and_delete():
    st.markdown("---")
    st.subheader("📊 Top Player Board (Saved Plays)")
    if not st.session_state.all_props:
        st.info("No saved plays yet.")
        return
    sorted_props = sorted(st.session_state.all_props, key=lambda x: x["True Prob"], reverse=True)
    for p in sorted_props:
        p["_ev"] = ev_calc(p["True Prob"]/100.0, p["Odds"])
        p["_tier"] = get_tier(p["True Prob"])
        col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
        with col1: st.markdown(f"**{p['Player']} – {p['Prop']}**  \nGroup: `{p['Group']}`")
        with col2: st.markdown(f"True: `{p['True Prob']}%`")
        with col3: st.markdown(f"Odds: `{p['Odds']}`  \nEV: `{p['_ev']}%`")
        with col4: st.markdown(f"Tier: {p['_tier']}")

def render_parlay_builder():
    st.markdown("---")
    st.subheader("💡 Parlay Builder (Choose from Saved Plays)")
    if not st.session_state.all_props:
        st.info("Save plays to use them here.")
        return
    labels = [f"{p['Player']} – {p['Prop']} (Odds {p['Odds']}, True {p['True Prob']}%)" for p in st.session_state.all_props]
    label_map = {labels[i]: st.session_state.all_props[i] for i in range(len(labels))}
    chosen = st.multiselect("Select legs (2+)", labels)
    parlay_odds = st.number_input("Sportsbook Parlay Odds (American)", value=0)

    if chosen and len(chosen) >= 2:
        sel = [label_map[c] for c in chosen]
        true_frac = 1.0
        for p in sel:
            true_frac *= (p["True Prob"] / 100.0)

        combined_true_pct = round(true_frac * 100.0, 2)
        imp_parlay = implied_prob(parlay_odds)
        parlay_ev = round((true_frac - imp_parlay) * 100, 2)
        tier = get_tier(combined_true_pct)

        st.success(f"🎯 Parlay Hit Probability: **{combined_true_pct}%**")
        st.info(f"📊 Parlay Implied Probability: **{round(imp_parlay*100,2)}%**")
        st.warning(f"💰 EV: **{parlay_ev}%**  | Tier: {tier}")

# =========================
# Position Selector
# =========================
position = st.selectbox("Select Position", ["Quarterback", "Wide Receiver", "Running Back"])

# =========================
# Quarterback Module
# =========================
if position == "Quarterback":
    st.header("🎯 Quarterback Inputs")
    name = st.text_input("Quarterback Name", value="")
    opp = st.text_input("Opponent Team", value="")

    std_line = st.number_input("Standard Passing Yards Line", value=0.0)
    over_std = st.number_input("Odds Over (Standard)", value=0.0)
    under_std = st.number_input("Odds Under (Standard)", value=0.0)
    alt_line = st.number_input("Alt Over Line", value=0.0)
    alt_odds = st.number_input("Odds for Alt Over", value=0.0)
    td_line = st.number_input("Passing TD Line", value=1.5)
    td_under_odds = st.number_input("Odds for Under TDs", value=0.0)

    ypg = st.number_input("QB Yards/Game", value=0.0)
    tds = st.number_input("QB TD/Game", value=0.0)
    def_yds = st.number_input("Defense Pass Yards Allowed/Game", value=0.0)
    def_tds = st.number_input("Defense Pass TDs Allowed/Game", value=0.0)

    if st.button("Simulate QB Props"):
        tier = classify_def_tier(def_yds)
        avg_ypg = (ypg + def_yds) / 2
        avg_tds = (tds + def_tds) / 2
        adj_ypg, adj_tds = apply_defense_adjustments(avg_ypg, avg_tds, tier)

        st.session_state.temp_props = []  # auto clear

        std_prob = logistic_prob(adj_ypg, std_line)
        alt_prob = logistic_prob(adj_ypg, alt_line)
        td_prob = logistic_prob(adj_tds, td_line, scale=0.5)
        under_td_prob = round(100.0 - td_prob, 2)

        st.info(f"Opponent Defense Tier: **{tier}**")
        st.success(f"📈 Over {std_line} Pass Yds → {std_prob}%")
        st.success(f"📈 Over {alt_line} Alt Pass Yds → {alt_prob}%")
        st.success(f"📉 Under {td_line} Pass TDs → {under_td_prob}%")

        add_temp_play(name, f"Over {std_line} Pass Yds", std_prob, over_std, "QB")
        add_temp_play(name, f"Over {alt_line} Alt Pass Yds", alt_prob, alt_odds, "QB")
        add_temp_play(name, f"Under {td_line} Pass TDs", under_td_prob, td_under_odds, "QB")

# =========================
# Wide Receiver Module
# =========================
if position == "Wide Receiver":
    st.header("🎯 Wide Receiver Inputs")
    name = st.text_input("Wide Receiver Name", value="")
    opp = st.text_input("Opponent Team", value="")

    std_line = st.number_input("Standard Receiving Yards Line", value=0.0)
    over_std = st.number_input("Odds Over (Standard)", value=0.0)
    under_std = st.number_input("Odds Under (Standard)", value=0.0)
    alt_line = st.number_input("Alt Over Line", value=0.0)
    alt_odds = st.number_input("Odds for Alt Over", value=0.0)
    rec_line = st.number_input("Receptions Line", value=0.0)
    rec_over_odds = st.number_input("Odds for Over Receptions", value=0.0)
    rec_under_odds = st.number_input("Odds for Under Receptions", value=0.0)

    ypg = st.number_input("WR Yards/Game", value=0.0)
    rpg = st.number_input("WR Receptions/Game", value=0.0)
    def_yds = st.number_input("Defense WR Yards Allowed/Game", value=0.0)
    def_rec = st.number_input("Defense WR Receptions Allowed/Game", value=0.0)

    if st.button("Simulate WR Props"):
        tier = classify_def_tier(def_yds)
        avg_ypg = (ypg + def_yds) / 2
        avg_rpg = (rpg + def_rec) / 2
        adj_ypg, _ = apply_defense_adjustments(avg_ypg, 0.0, tier)

        st.session_state.temp_props = []  # auto clear

        std_prob = logistic_prob(adj_ypg, std_line)
        alt_prob = logistic_prob(adj_ypg, alt_line)
        rec_prob = logistic_prob(avg_rpg, rec_line, scale=1.5)

        st.info(f"Opponent Defense Tier: **{tier}**")
        st.success(f"📈 Over {std_line} Rec Yds → {std_prob}%")
        st.success(f"📈 Over {alt_line} Alt Rec Yds → {alt_prob}%")
        st.success(f"🎯 Over {rec_line} Receptions → {rec_prob}%")
        st.success(f"📉 Under {rec_line} Receptions → {round(100-rec_prob,2)}%")

        add_temp_play(name, f"Over {std_line} Rec Yds", std_prob, over_std, "WR")
        add_temp_play(name, f"Under {std_line} Rec Yds", round(100-std_prob,2), under_std, "WR")
        add_temp_play(name, f"Over {alt_line} Alt Rec Yds", alt_prob, alt_odds, "WR")
        add_temp_play(name, f"Over {rec_line} Receptions", rec_prob, rec_over_odds, "WR")
        add_temp_play(name, f"Under {rec_line} Receptions", round(100-rec_prob,2), rec_under_odds, "WR")

# =========================
# Running Back Module
# =========================
if position == "Running Back":
    st.header("🎯 Running Back Inputs")
    name = st.text_input("Running Back Name", value="")
    opp = st.text_input("Opponent Team", value="")

    std_line = st.number_input("Standard Rushing Yards Line", value=0.0)
    over_std = st.number_input("Odds Over (Standard)", value=0.0)
    under_std = st.number_input("Odds Under (Standard)", value=0.0)
    alt_line = st.number_input("Alt Over Line", value=0.0)
    alt_odds = st.number_input("Odds for Alt Over", value=0.0)
    rec_line = st.number_input("Receptions Line", value=0.0)
    rec_over_odds = st.number_input("Odds for Over Receptions", value=0.0)
    rec_under_odds = st.number_input("Odds for Under Receptions", value=0.0)

    ypg = st.number_input("RB Yards/Game", value=0.0)
    rpg = st.number_input("RB Receptions/Game", value=0.0)
    def_yds = st.number_input("Defense Rush Yards Allowed/Game", value=0.0)
    def_rec = st.number_input("Defense RB Receptions Allowed/Game", value=0.0)

    if st.button("Simulate RB Props"):
        tier = classify_def_tier(def_yds)
        avg_ypg = (ypg + def_yds) / 2
        avg_rpg = (rpg + def_rec) / 2
        adj_ypg, _ = apply_defense_adjustments(avg_ypg, 0.0, tier)

        st.session_state.temp_props = []  # auto clear

        std_prob = logistic_prob(adj_ypg, std_line)
        alt_prob = logistic_prob(adj_ypg, alt_line)
        rec_prob = logistic_prob(avg_rpg, rec_line, scale=1.5)

        st.info(f"Opponent Defense Tier: **{tier}**")
        st.success(f"📈 Over {std_line} Rush Yds → {std_prob}%")
        st.success(f"📈 Over {alt_line} Alt Rush Yds → {alt_prob}%")
        st.success(f"🎯 Over {rec_line} Receptions → {rec_prob}%")
        st.success(f"📉 Under {rec_line} Receptions → {round(100-rec_prob,2)}%")

        add_temp_play(name, f"Over {std_line} Rush Yds", std_prob, over_std, "RB")
        add_temp_play(name, f"Under {std_line} Rush Yds", round(100-std_prob,2), under_std, "RB")
        add_temp_play(name, f"Over {alt_line} Alt Rush Yds", alt_prob, alt_odds, "RB")
        add_temp_play(name, f"Over {rec_line} Receptions", rec_prob, rec_over_odds, "RB")
        add_temp_play(name, f"Under {rec_line} Receptions", round(100-rec_prob,2), rec_under_odds, "RB")

# =========================
# Save, Board, Parlay
# =========================
render_temp_save_controls()
render_board_and_delete()
render_parlay_builder()

   
