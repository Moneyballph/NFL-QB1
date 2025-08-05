
import streamlit as st
import math
import base64

# === 🎨 Background ===
def set_background(image_file_path):
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

st.set_page_config(page_title="🏈 Moneyball Phil: NFL Prop Simulator", layout="centered")
set_background("ChatGPT Image Jul 14, 2025, 09_58_55 AM.png")

# === 🏈 TITLE ===
st.title("🏈 Moneyball Phil: NFL Prop Simulator (v2.0)")
st.markdown("Simulate **Player Props** for QBs, WRs, and RBs including true hit probability, EV%, and parlay builder.")

# === 🔽 POSITION DROPDOWN ===
position = st.selectbox("Select Position", ["Quarterback (QB)", "Wide Receiver (WR)", "Running Back (RB)"])

# === 📋 COMMON INPUTS ===
st.header("📋 Player & Matchup Info")

col1, col2 = st.columns(2)
with col1:
    player_name = st.text_input("Player Name", value="")
with col2:
    opponent_team = st.text_input("Opponent Team", value="")

# === 💼 DEFENSE CLASSIFIER ===
def classify_def_tier(yds_allowed):
    if yds_allowed < 205:
        return "🔴 Tough"
    elif yds_allowed <= 240:
        return "🟡 Average"
    else:
        return "🟢 Easy"

# === 📈 SHARED FUNCTIONS ===
def implied_prob(odds):
    return abs(odds) / (abs(odds) + 100) if odds < 0 else 100 / (odds + 100)

def ev_calc(true_prob, odds):
    imp = implied_prob(odds)
    return round((true_prob - imp) * 100, 2)

def get_tier(prob):
    if prob >= 80: return "🟢 Elite"
    elif prob >= 65: return "🟡 Strong"
    elif prob >= 50: return "🟠 Moderate"
    else: return "🔴 Risky"

def logistic_prob(x, line, scale=15):
    return round((1 / (1 + math.exp(-(x - line) / scale))) * 100, 2)

def binomial_probability(k, n, p):
    comb = math.comb(n, k)
    return comb * (p ** k) * ((1 - p) ** (n - k))

props = []
results = []

# === 👨‍🏫 POSITION-BASED LOGIC ===
if position == "Quarterback (QB)":
    st.subheader("📊 Passing Yards & Touchdowns")
    col1, col2, col3 = st.columns(3)
    with col1:
        standard_yds_line = st.number_input("Standard Passing Yards Line", value=0.0, step=0.1, format="%.1f")
    with col2:
        odds_over_std = st.number_input("Odds for Over (Standard Line)", value=0.0, step=0.1, format="%.1f")
    with col3:
        odds_under_std = st.number_input("Odds for Under (Standard Line)", value=0.0, step=0.1, format="%.1f")

    col4, col5 = st.columns(2)
    with col4:
        alt_yds_line = st.number_input("Alt Over Yards Line", value=0.0, step=0.1, format="%.1f")
    with col5:
        odds_alt_over = st.number_input("Odds for Alt Over", value=0.0, step=0.1, format="%.1f")

    st.subheader("🎯 Touchdown Props")
    col6, col7 = st.columns(2)
    with col6:
        td_line = st.number_input("TD Line", value=1.5, step=0.1, format="%.1f")
    with col7:
        odds_under_tds = st.number_input("Odds for Under TDs", value=0.0, step=0.1, format="%.1f")

    st.subheader("📊 QB & Defense Stats")
    col8, col9, col10 = st.columns(3)
    with col8:
        qb_yards = st.number_input("QB Yards/Game", value=0.0)
    with col9:
        qb_td = st.number_input("QB TDs/Game", value=0.0)
    with col10:
        pass_attempts = st.number_input("Pass Attempts/Game", value=0.0)

    col11, col12 = st.columns(2)
    with col11:
        def_yds_allowed = st.number_input("Defense Yards Allowed", value=0.0)
    with col12:
        def_td_allowed = st.number_input("Defense TDs Allowed", value=0.0)

    matchup_tier = classify_def_tier(def_yds_allowed)

    if st.button("🎯 Simulate Player"):
        avg_yds = (0.65 * qb_yards + 0.35 * def_yds_allowed) * (1.08 if pass_attempts >= 36 else 1.0)
        avg_tds = (qb_td + def_td_allowed) / 2
        p_per_attempt = avg_tds / pass_attempts if pass_attempts > 0 else 0

        std_over_prob = logistic_prob(avg_yds, standard_yds_line)
        std_under_prob = 100 - std_over_prob
        alt_over_prob = logistic_prob(avg_yds, alt_yds_line)

        prob_0 = binomial_probability(0, int(pass_attempts), p_per_attempt)
        prob_1 = binomial_probability(1, int(pass_attempts), p_per_attempt)
        under_tds_prob = round((prob_0 + prob_1) * 100, 2)

        props = [
            {"Prop": "Standard Over", "True Prob": std_over_prob, "Odds": odds_over_std},
            {"Prop": "Standard Under", "True Prob": std_under_prob, "Odds": odds_under_std},
            {"Prop": "Alt Over", "True Prob": alt_over_prob, "Odds": odds_alt_over},
            {"Prop": "Under 1.5 TDs", "True Prob": under_tds_prob, "Odds": odds_under_tds}
        ]

# === WR SECTION ===
elif position == "Wide Receiver (WR)":
    st.subheader("📊 Receiving Props")
    col1, col2, col3 = st.columns(3)
    with col1:
        rec_yds_line = st.number_input("Receiving Yards Line", value=0.0)
    with col2:
        rec_yds_odds = st.number_input("Odds Over (Yards)", value=0.0)
    with col3:
        alt_yds_line = st.number_input("Alt Receiving Yards", value=0.0)

    col4, col5 = st.columns(2)
    with col4:
        alt_yds_odds = st.number_input("Odds Alt Over Yards", value=0.0)
    with col5:
        recs_line = st.number_input("Receptions Line", value=0.0)

    col6, col7 = st.columns(2)
    with col6:
        recs_odds = st.number_input("Odds Over Receptions", value=0.0)
    with col7:
        wr_avg_yds = st.number_input("WR Yards/Game", value=0.0)

    col8, col9 = st.columns(2)
    with col8:
        wr_avg_recs = st.number_input("WR Receptions/Game", value=0.0)
    with col9:
        def_wr_yds_allowed = st.number_input("Defense Yards Allowed/Game", value=0.0)

    matchup_tier = classify_def_tier(def_wr_yds_allowed)

    if st.button("🎯 Simulate Player"):
        avg_wr_yards = (0.65 * wr_avg_yds + 0.35 * def_wr_yds_allowed)
        rec_yds_prob = logistic_prob(avg_wr_yards, rec_yds_line)
        alt_yds_prob = logistic_prob(avg_wr_yards, alt_yds_line)
        recs_prob = logistic_prob(wr_avg_recs, recs_line, scale=3.5)

        props = [
            {"Prop": "Receiving Yards Over", "True Prob": rec_yds_prob, "Odds": rec_yds_odds},
            {"Prop": "Alt Receiving Yards Over", "True Prob": alt_yds_prob, "Odds": alt_yds_odds},
            {"Prop": "Receptions Over", "True Prob": recs_prob, "Odds": recs_odds}
        ]

# === RB SECTION ===
elif position == "Running Back (RB)":
    st.subheader("📊 Rushing & Receiving Props")
    col1, col2 = st.columns(2)
    with col1:
        rush_yds_line = st.number_input("Rushing Yards Line", value=0.0)
    with col2:
        rush_yds_odds = st.number_input("Odds Over (Rushing)", value=0.0)

    col3, col4 = st.columns(2)
    with col3:
        rb_avg_rush = st.number_input("RB Rushing Yards/Game", value=0.0)
    with col4:
        def_rush_yds_allowed = st.number_input("Defense Rush Yards Allowed", value=0.0)

    col5, col6 = st.columns(2)
    with col5:
        recs_line = st.number_input("RB Receptions Line", value=0.0)
    with col6:
        recs_odds = st.number_input("Odds Over (Receptions)", value=0.0)

    col7 = st.columns(1)[0]
    with col7:
        rb_avg_recs = st.number_input("RB Receptions/Game", value=0.0)

    matchup_tier = classify_def_tier(def_rush_yds_allowed)

    if st.button("🎯 Simulate Player"):
        rush_prob = logistic_prob(rb_avg_rush, rush_yds_line)
        recs_prob = logistic_prob(rb_avg_recs, recs_line, scale=3.5)

        props = [
            {"Prop": "Rushing Yards Over", "True Prob": rush_prob, "Odds": rush_yds_odds},
            {"Prop": "Receptions Over", "True Prob": recs_prob, "Odds": recs_odds}
        ]

# === 🧮 RESULT DISPLAY ===
if props:
    results = []
    for prop in props:
        true_p = prop["True Prob"]
        imp = round(implied_prob(prop["Odds"]) * 100, 2)
        ev = ev_calc(true_p / 100, prop["Odds"])
        tier = get_tier(true_p)
        results.append({
            "Prop": prop["Prop"],
            "True Probability": f"{true_p}%",
            "Implied Probability": f"{imp}%",
            "EV %": f"{ev}%",
            "Tier": tier
        })

    st.dataframe(results)
    st.markdown(f"**📊 Matchup Risk Tier:** {matchup_tier}")

    # 🔁 Parlay Builder
    st.markdown("### 🔁 Parlay Builder: Select Props")
    selected_ids = st.multiselect("Select 2 or more props:", [prop["Prop"] for prop in props])
    if len(selected_ids) >= 2:
        selected = [p for p in props if p["Prop"] in selected_ids]
        parlay_true = 1.0
        parlay_implied = 1.0
        for s in selected:
            parlay_true *= s["True Prob"] / 100
            parlay_implied *= implied_prob(s["Odds"])
        parlay_ev = round((parlay_true - parlay_implied) * 100, 2)
        tier = get_tier(parlay_true * 100)

        st.markdown("### 🎯 Parlay Simulation Result")
        st.write(f"**True Hit Probability:** {parlay_true:.2%}")
        st.write(f"**Implied Probability:** {parlay_implied:.2%}")
        st.write(f"**EV %:** {parlay_ev}%")
        st.write(f"**Tier:** {tier}")
    elif len(selected_ids) == 1:
        st.info("Select at least 2 props to simulate parlay EV.")



   
