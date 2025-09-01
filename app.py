
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
        pass  # background optional

st.set_page_config(page_title="🏈 Moneyball Phil: NFL Prop Simulator", layout="centered")
set_background("ChatGPT Image Jul 14, 2025, 09_58_55 AM.png")

st.title("🏈 Moneyball Phil: NFL Prop Simulator (v2.1)")

# =========================
# Session State
# =========================
if "all_props" not in st.session_state:
    st.session_state.all_props = []   # all saved plays (dicts)
if "temp_props" not in st.session_state:
    st.session_state.temp_props = []  # last simulation (unsaved plays)
if "parlay_pool" not in st.session_state:
    st.session_state.parlay_pool = [] # subset explicitly chosen for parlay

# =========================
# Helpers
# =========================
def implied_prob(odds: float) -> float:
    """Return implied probability in [0,1] from American odds."""
    if odds == 0:
        return 0.0
    return (abs(odds) / (abs(odds) + 100)) if odds < 0 else (100 / (odds + 100))

def american_to_decimal(odds: float) -> float:
    """American -> Decimal odds (>=1)."""
    if odds == 0:
        return 1.0
    return 1.0 + (odds / 100.0) if odds > 0 else 1.0 + (100.0 / abs(odds))

def ev_calc(true_prob_frac: float, odds: float) -> float:
    """EV% = (True% - Implied%) * 100."""
    return round((true_prob_frac - implied_prob(odds)) * 100, 2)

def get_tier(prob_pct: float) -> str:
    if prob_pct >= 80:
        return "🟢 Elite"
    elif prob_pct >= 65:
        return "🟡 Strong"
    elif prob_pct >= 50:
        return "🟠 Moderate"
    else:
        return "🔴 Risky"

def logistic_prob(x_value: float, line_value: float, scale: float = 15.0) -> float:
    """Return probability (%) using logistic centered on the betting line."""
    try:
        p = 1.0 / (1.0 + math.exp(-(x_value - line_value) / scale))
    except OverflowError:
        p = 0.0 if (x_value - line_value) < 0 else 1.0
    return round(p * 100.0, 2)

def classify_def_tier(pass_yds_allowed_per_g: float) -> str:
    """
    Tiering by defensive passing yards allowed per game.
    You can tweak thresholds to be more/less aggressive.
    """
    if isinstance(pass_yds_allowed_per_g, (int, float)):
        if pass_yds_allowed_per_g < 210:
            return "🔴 Tough"
        elif pass_yds_allowed_per_g <= 240:
            return "🟡 Average"
        else:
            return "🟢 Easy"
    return "Unknown"

def apply_defense_adjustments(ypg: float, tpg: float, tier: str,
                              avg_bumps=(0.0, 0.0),
                              tough_bumps=(-10.0, -0.20),
                              easy_bumps=(+10.0, +0.20)) -> tuple[float, float]:
    """
    Returns adjusted (ypg, tpg) after defense tier effect.
    - avg_bumps: applied on 'Average' defenses (default no change)
    - tough_bumps: negative bump for tough defenses
    - easy_bumps: positive bump for easy defenses
    """
    adj_ypg, adj_tpg = ypg, tpg
    if tier == "🔴 Tough":
        adj_ypg += tough_bumps[0]
        adj_tpg += tough_bumps[1]
    elif tier == "🟢 Easy":
        adj_ypg += easy_bumps[0]
        adj_tpg += easy_bumps[1]
    elif tier == "🟡 Average":
        adj_ypg += avg_bumps[0]
        adj_tpg += avg_bumps[1]
    return adj_ypg, adj_tpg

def add_play(player: str, prop: str, true_prob_pct: float, odds: float, group: str):
    st.session_state.all_props.append({
        "id": str(uuid.uuid4()),
        "Player": player,
        "Prop": prop,
        "True Prob": round(true_prob_pct, 2),
        "Odds": odds,
        "Group": group  # e.g., QB / WR / RB
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

def render_temp_save_controls():
    if not st.session_state.temp_props:
        st.info("No new simulation results yet.")
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
    cols = st.columns([1,1,6])
    with cols[0]:
        if st.button("➕ Add Selected"):
            for p in to_save:
                add_play(p["Player"], p["Prop"], p["True Prob"], p["Odds"], p["Group"])
            st.session_state.temp_props = []
            st.success("Selected plays added to Top Player Board.")
    with cols[1]:
        if st.button("✖️ Discard All New"):
            st.session_state.temp_props = []
            st.info("Discarded this run's results.")

def render_board_and_delete():
    st.markdown("---")
    st.subheader("📊 Top Player Board (Saved Plays)")
    if not st.session_state.all_props:
        st.info("No saved plays yet. Save from the latest simulation above.")
        return

    # Selection map
    selected_ids = set()
    for p in st.session_state.all_props:
        p["_ev"] = ev_calc(p["True Prob"]/100.0, p["Odds"])
        p["_tier"] = get_tier(p["True Prob"])

    # Sort by True Prob (desc)
    sorted_props = sorted(st.session_state.all_props, key=lambda x: x["True Prob"], reverse=True)

    for p in sorted_props:
        c1, c2, c3, c4, c5 = st.columns([4, 2, 2, 2, 1])
        with c1:
            st.markdown(f"**{p['Player']} – {p['Prop']}**  \nGroup: `{p['Group']}`")
        with c2:
            st.markdown(f"True: `{p['True Prob']}%`")
        with c3:
            st.markdown(f"Odds: `{p['Odds']}`  \nEV: `{p['_ev']}%`")
        with c4:
            st.markdown(f"Tier: {p['_tier']}")
        with c5:
            if st.checkbox("🗑️", key=f"del_{p['id']}"):
                selected_ids.add(p["id"])

    colA, colB, colC = st.columns([1,1,6])
    with colA:
        if st.button("🗑️ Delete Selected"):
            st.session_state.all_props = [p for p in st.session_state.all_props if p["id"] not in selected_ids]
            st.success("Selected plays deleted.")
    with colB:
        if st.button("🧹 Clear All"):
            st.session_state.all_props = []
            st.session_state.parlay_pool = []
            st.info("Cleared all saved plays.")

def render_parlay_builder():
    st.markdown("---")
    st.subheader("💡 Parlay Builder (Choose from Saved Plays)")
    if not st.session_state.all_props:
        st.info("Save plays to use them here.")
        return

    # Multi-select by label
    labels = [f"{p['Player']} – {p['Prop']} (Odds {p['Odds']}, True {p['True Prob']}%)" for p in st.session_state.all_props]
    label_map = {labels[i]: st.session_state.all_props[i] for i in range(len(labels))}
    chosen = st.multiselect("Select legs (2+)", labels)

    if chosen and len(chosen) >= 2:
        sel = [label_map[c] for c in chosen]
        # Combined (independence): True% product; Decimal odds multiply
        true_frac = 1.0
        dec_prod = 1.0
        imp_frac = 1.0
        for p in sel:
            true_frac *= (p["True Prob"] / 100.0)
            dec_prod *= american_to_decimal(p["Odds"])
            imp_frac *= implied_prob(p["Odds"])

        combined_true_pct = round(true_frac * 100.0, 2)
        combined_implied_pct = round(imp_frac * 100.0, 2)
        # Parlay EV% = (True - Implied) * 100
        parlay_ev = round((true_frac - imp_frac) * 100.0, 2)

        st.success(f"Parlay Hit Probability: `{combined_true_pct}%`")
        st.info(f"Parlay Implied Probability: `{combined_implied_pct}%`")
        st.warning(f"Parlay EV: `{parlay_ev}%`  (Independence assumption)")

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

    st.subheader("📊 Passing Yards Props")
    std_line = st.number_input("Standard Passing Yards Line", value=0.0)
    over_std = st.number_input("Odds Over (Standard)", value=0.0)
    under_std = st.number_input("Odds Under (Standard)", value=0.0)
    alt_line = st.number_input("Alt Over Line", value=0.0)
    alt_odds = st.number_input("Odds for Alt Over", value=0.0)

    st.subheader("🎯 Passing TD Prop (Under only)")
    td_line = st.number_input("Passing TD Line", value=1.5)
    td_under_odds = st.number_input("Odds for Under TDs", value=0.0)

    st.subheader("📈 QB & Defense Stats (Season Averages)")
    ypg = st.number_input("QB Yards/Game", value=0.0)
    tds = st.number_input("QB TD/Game", value=0.0)
    attempts = st.number_input("Pass Attempts/Game", value=0.0)
    def_yds = st.number_input("Defense Yards Allowed/Game", value=0.0)
    def_tds = st.number_input("Defense Pass TDs/Game", value=0.0)

    with st.expander("⚙️ Defense Effect Settings"):
        st.write("Defense tier tweaks applied to QB inputs before probability:")
        avg_y_bump = st.number_input("Average: yards bump", value=0.0, step=1.0)
        avg_t_bump = st.number_input("Average: TDs bump", value=0.0, step=0.05, format="%.2f")
        tough_y_bump = st.number_input("Tough: yards bump", value=-10.0, step=1.0)
        tough_t_bump = st.number_input("Tough: TDs bump", value=-0.20, step=0.05, format="%.2f")
        easy_y_bump = st.number_input("Easy: yards bump", value=10.0, step=1.0)
        easy_t_bump = st.number_input("Easy: TDs bump", value=0.20, step=0.05, format="%.2f")

    if st.button("Simulate QB Props"):
        # Determine defense tier
        tier = classify_def_tier(def_yds)

        # Apply defense-based adjustments to QB stats
        adj_ypg, adj_tds = apply_defense_adjustments(
            ypg, tds, tier,
            avg_bumps=(avg_y_bump, avg_t_bump),
            tough_bumps=(tough_y_bump, tough_t_bump),
            easy_bumps=(easy_y_bump, easy_t_bump),
        )

        # Calculate probabilities using adjusted QB stats
        std_prob = logistic_prob(adj_ypg, std_line)
        alt_prob = logistic_prob(adj_ypg, alt_line)
        td_prob = logistic_prob(adj_tds, td_line, scale=0.5)   # Over prob
        under_td_prob = round(100.0 - td_prob, 2)

        st.info(f"Opponent Defense Tier: **{tier}**")
        st.success(f"📈 Standard Yards Over {std_line} → True %: **{std_prob}%**")
        st.success(f"📈 Alt Yards Over {alt_line} → True %: **{alt_prob}%**")
        st.success(f"📉 Under {td_line} Passing TDs → True %: **{under_td_prob}%**")

        # Stage new simulation plays (not auto-saved)
        st.session_state.temp_props = []
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

    st.subheader("📊 Receiving Yards Props")
    std_line = st.number_input("Standard Receiving Yards Line", value=0.0)
    over_std = st.number_input("Odds Over (Standard)", value=0.0)
    under_std = st.number_input("Odds Under (Standard)", value=0.0)
    alt_line = st.number_input("Alt Over Line", value=0.0)
    alt_odds = st.number_input("Odds for Alt Over", value=0.0)

    st.subheader("🎯 Receptions Prop")
    rec_line = st.number_input("Receptions Line", value=0.0)
    rec_over_odds = st.number_input("Odds for Over Receptions", value=0.0)
    rec_under_odds = st.number_input("Odds for Under Receptions", value=0.0)

    st.subheader("📈 WR & Defense Stats (Season Averages)")
    ypg = st.number_input("WR Yards/Game", value=0.0)
    rpg = st.number_input("WR Receptions/Game", value=0.0)
    def_yds = st.number_input("Defense WR Yards Allowed/Game", value=0.0)
    def_rec = st.number_input("Defense WR Receptions Allowed/Game", value=0.0)

    with st.expander("⚙️ Defense Effect Settings"):
        avg_y_bump = st.number_input("Average: yards bump", value=0.0, step=1.0, key="wr_avg_y")
        tough_y_bump = st.number_input("Tough: yards bump", value=-8.0, step=1.0, key="wr_tough_y")
        easy_y_bump = st.number_input("Easy: yards bump", value=8.0, step=1.0, key="wr_easy_y")

    if st.button("Simulate WR Props"):
        tier = classify_def_tier(def_yds)
        adj_ypg, _ = apply_defense_adjustments(ypg, 0.0, tier,
                                               avg_bumps=(avg_y_bump, 0.0),
                                               tough_bumps=(tough_y_bump, 0.0),
                                               easy_bumps=(easy_y_bump, 0.0))
        std_prob = logistic_prob(adj_ypg, std_line)
        alt_prob = logistic_prob(adj_ypg, alt_line)
        rec_prob = logistic_prob(rpg, rec_line, scale=1.5)

        st.info(f"Opponent Defense Tier: **{tier}**")
        st.success(f"📈 Standard Yards Over {std_line} → True %: **{std_prob}%**")
        st.success(f"📈 Alt Yards Over {alt_line} → True %: **{alt_prob}%**")
        st.success(f"🎯 Receptions Over {rec_line} → True %: **{rec_prob}%**")
        st.success(f"📉 Receptions Under {rec_line} → True %: **{round(100-rec_prob,2)}%**")

        st.session_state.temp_props = []
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

    st.subheader("📊 Rushing Yards Props")
    std_line = st.number_input("Standard Rushing Yards Line", value=0.0)
    over_std = st.number_input("Odds Over (Standard)", value=0.0)
    under_std = st.number_input("Odds Under (Standard)", value=0.0)
    alt_line = st.number_input("Alt Over Line", value=0.0)
    alt_odds = st.number_input("Odds for Alt Over", value=0.0)

    st.subheader("🎯 Receptions Prop")
    rec_line = st.number_input("Receptions Line", value=0.0)
    rec_over_odds = st.number_input("Odds for Over Receptions", value=0.0)
    rec_under_odds = st.number_input("Odds for Under Receptions", value=0.0)

    st.subheader("📈 RB & Defense Stats (Season Averages)")
    ypg = st.number_input("RB Yards/Game", value=0.0)
    rpg = st.number_input("RB Receptions/Game", value=0.0)
    def_yds = st.number_input("Defense Rush Yards Allowed/Game", value=0.0)
    def_rec = st.number_input("Defense RB Receptions Allowed/Game", value=0.0)

    with st.expander("⚙️ Defense Effect Settings"):
        avg_y_bump = st.number_input("Average: yards bump", value=0.0, step=1.0, key="rb_avg_y")
        tough_y_bump = st.number_input("Tough: yards bump", value=-8.0, step=1.0, key="rb_tough_y")
        easy_y_bump = st.number_input("Easy: yards bump", value=8.0, step=1.0, key="rb_easy_y")

    if st.button("Simulate RB Props"):
        tier = classify_def_tier(def_yds)
        adj_ypg, _ = apply_defense_adjustments(ypg, 0.0, tier,
                                               avg_bumps=(avg_y_bump, 0.0),
                                               tough_bumps=(tough_y_bump, 0.0),
                                               easy_bumps=(easy_y_bump, 0.0))
        std_prob = logistic_prob(adj_ypg, std_line)
        alt_prob = logistic_prob(adj_ypg, alt_line)
        rec_prob = logistic_prob(rpg, rec_line, scale=1.5)

        st.info(f"Opponent Defense Tier: **{tier}**")
        st.success(f"📈 Standard Rush Yards Over {std_line} → True %: **{std_prob}%**")
        st.success(f"📈 Alt Rush Yards Over {alt_line} → True %: **{alt_prob}%**")
        st.success(f"🎯 Receptions Over {rec_line} → True %: **{rec_prob}%**")
        st.success(f"📉 Receptions Under {rec_line} → True %: **{round(100-rec_prob,2)}%**")

        st.session_state.temp_props = []
        add_temp_play(name, f"Over {std_line} Rush Yds", std_prob, over_std, "RB")
        add_temp_play(name, f"Under {std_line} Rush Yds", round(100-std_prob,2), under_std, "RB")
        add_temp_play(name, f"Over {alt_line} Alt Rush Yds", alt_prob, alt_odds, "RB")
        add_temp_play(name, f"Over {rec_line} Receptions", rec_prob, rec_over_odds, "RB")
        add_temp_play(name, f"Under {rec_line} Receptions", round(100-rec_prob,2), rec_under_odds, "RB")

# =========================
# Save Controls, Board, Parlay
# =========================
render_temp_save_controls()
render_board_and_delete()
render_parlay_builder()





   
