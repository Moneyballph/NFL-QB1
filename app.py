
import streamlit as st
import math
import matplotlib.pyplot as plt
import base64

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

st.title("🏈 Moneyball Phil: NFL Prop Simulator (v1.2)")
st.markdown("Simulate **Under 1.5 Passing TDs** and **Alt/Standard Over Passing Yards** props for any QB.")

st.header("📋 Input Player & Matchup Data")

col1, col2 = st.columns(2)
with col1:
    qb_name = st.text_input("Quarterback Name", value="Kenny Pickett")
    opponent_team = st.text_input("Opponent Team", value="Texans")

st.subheader("📊 Passing Yards Props")
col3, col4, col5 = st.columns(3)
with col3:
    standard_yds_line = st.number_input("Standard Passing Yards Line", value=210)
with col4:
    odds_over_std = st.number_input("Odds for Over (Standard Line)", value=-115)
with col5:
    odds_under_std = st.number_input("Odds for Under (Standard Line)", value=-105)

col6, col7 = st.columns(2)
with col6:
    alt_yds_line = st.number_input("Alt Over Yards Line", value=199)
with col7:
    odds_alt_over = st.number_input("Odds for Alt Over Line", value=-145)

st.subheader("🎯 Touchdown Props")
col8, col9 = st.columns(2)
with col8:
    td_line = st.number_input("Passing TD Line", value=1.5)
with col9:
    odds_under_tds = st.number_input("Odds for Under TDs", value=100)

st.subheader("📈 QB & Defense Stats")
col10, col11, col12 = st.columns(3)
with col10:
    qb_yards = st.number_input("QB Yards/Game", value=188.0)
with col11:
    qb_td = st.number_input("QB TD/Game", value=0.7)
with col12:
    pass_attempts = st.number_input("Pass Attempts/Game", value=27.6)

col13, col14 = st.columns(2)
with col13:
    def_yds_allowed = st.number_input("Defense Yards Allowed/Game", value=237.0)
with col14:
    def_td_allowed = st.number_input("Defense Pass TDs/Game", value=1.1)

# ✅ Auto Defense Tier
def classify_def_tier(yards_allowed):
    if yards_allowed < 205:
        return "🔴 Tough"
    elif yards_allowed <= 240:
        return "🟡 Average"
    else:
        return "🟢 Easy"

def_pass_rank = classify_def_tier(def_yds_allowed)

# === Helper Functions ===
def implied_prob(odds):
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)

def ev_calc(true_prob, odds):
    imp_prob = implied_prob(odds)
    return round((true_prob - imp_prob) * 100, 2)

def get_tier(prob):
    if prob >= 80:
        return "🟢 Elite"
    elif prob >= 65:
        return "🟡 Strong"
    elif prob >= 50:
        return "🟠 Moderate"
    else:
        return "🔴 Risky"

def binomial_probability(k, n, p):
    comb = math.comb(n, k)
    return comb * (p ** k) * ((1 - p) ** (n - k))

def logistic_prob(x, line, scale=15):
    return round((1 / (1 + math.exp(-(x - line) / scale))) * 100, 2)

# === Simulate Button ===
if st.button("🎯 Simulate Player"):
    st.header("📋 Player Prop Simulation Results")

    # 🎯 Pro-level average calculation for passing yards
# Weighted average favoring QB's skill + bump for high volume QBs
base_avg = (0.65 * qb_yards) + (0.35 * def_yds_allowed)

# Volume adjustment based on pass attempts per game
if pass_attempts >= 40:
    avg_yds = base_avg * 1.12  # heavy volume bump
elif pass_attempts >= 36:
    avg_yds = base_avg * 1.08  # moderate bump
else:
    avg_yds = base_avg

    avg_tds = (qb_td + def_td_allowed) / 2
    n_attempts = pass_attempts
    p_per_attempt = avg_tds / n_attempts if n_attempts > 0 else 0

    # ✅ Safe yard probability logic (no negatives)
    std_over_prob = logistic_prob(avg_yds, standard_yds_line)
    std_under_prob = round(100 - std_over_prob, 2)
    alt_over_prob = logistic_prob(avg_yds, alt_yds_line)

    # ✅ Binomial passing TD logic
    prob_0 = binomial_probability(0, int(n_attempts), p_per_attempt)
    prob_1 = binomial_probability(1, int(n_attempts), p_per_attempt)
    under_tds_prob = round((prob_0 + prob_1) * 100, 2)

    # ✅ Clear previous props/results
    props = []
    results = []

    props = [
        {"Prop": "Standard Over", "True Prob": std_over_prob, "Odds": odds_over_std},
        {"Prop": "Standard Under", "True Prob": std_under_prob, "Odds": odds_under_std},
        {"Prop": "Alt Over", "True Prob": alt_over_prob, "Odds": odds_alt_over},
        {"Prop": "Under 1.5 TDs", "True Prob": under_tds_prob, "Odds": odds_under_tds},
    ]

    for prop in props:
        true_p = prop["True Prob"]
        implied_p = round(implied_prob(prop["Odds"]) * 100, 2)
        ev = ev_calc(true_p / 100, prop["Odds"])
        tier = get_tier(true_p)
        results.append({
            "Prop": prop["Prop"],
            "True Probability": f"{true_p}%",
            "Implied Probability": f"{implied_p}%",
            "EV %": f"{ev}%",
            "Tier": tier
        })

    st.dataframe(results)
    st.markdown(f"**📊 Matchup Risk Tier:** {def_pass_rank}")

    # 🔁 Parlay Builder Section
    st.markdown("**🔁 Parlay Builder: Select Props**")

    selected_ids = st.multiselect(
        "Select 2 or more props to simulate parlay EV:",
        [prop["Prop"] for prop in props]
    )

    if len(selected_ids) >= 2:
        selected_props = [p for p in props if p["Prop"] in selected_ids]
        parlay_true_prob = 1.0
        parlay_implied_prob = 1.0

        for sp in selected_props:
            parlay_true_prob *= sp["True Prob"] / 100
            parlay_implied_prob *= implied_prob(sp["Odds"])

        parlay_ev = round((parlay_true_prob - parlay_implied_prob) * 100, 2)
        tier = get_tier(parlay_true_prob * 100)

        st.markdown("### 🎯 Parlay Simulation Result")
        st.write(f"**True Hit Probability:** {parlay_true_prob:.2%}")
        st.write(f"**Implied Probability:** {parlay_implied_prob:.2%}")
        st.write(f"**EV %:** {parlay_ev}%")
        st.write(f"**Tier:** {tier}")

    elif len(selected_ids) == 1:
        st.info("Please select at least 2 props for the parlay simulation.")


   
