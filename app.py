
import streamlit as st
import math
import base64

# === Background Setup ===
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

# === General Helpers ===
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

def classify_def_tier(yards_allowed):
    if yards_allowed < 205:
        return "🔴 Tough"
    elif yards_allowed <= 240:
        return "🟡 Average"
    else:
        return "🟢 Easy"

# === Start UI ===
st.title("🏈 Moneyball Phil: NFL Prop Simulator (v2.0)")
position = st.selectbox("Select Position", ["Quarterback", "Wide Receiver", "Running Back"])

props = []

# === QB SECTION ===
if position == "Quarterback":
    st.markdown("### 📋 QB Input & Matchup Data")
    col1, col2 = st.columns(2)
    with col1:
        qb_name = st.text_input("Quarterback Name", value="")
        opponent_team = st.text_input("Opponent Team", value="")
    st.markdown("### 📊 Passing Yards Props")
    col3, col4, col5 = st.columns(3)
    with col3:
        standard_yds_line = st.number_input("Standard Passing Yards Line", value=0.0, step=0.1)
        odds_over_std = st.number_input("Odds for Over (Standard Line)", value=0.0, step=0.1)
    with col4:
        odds_under_std = st.number_input("Odds for Under (Standard Line)", value=0.0, step=0.1)
        alt_yds_line = st.number_input("Alt Over Yards Line", value=0.0, step=0.1)
    with col5:
        odds_alt_over = st.number_input("Odds for Alt Over Line", value=0.0, step=0.1)
        td_line = st.number_input("Passing TD Line", value=1.5, step=0.1)
    odds_under_tds = st.number_input("Odds for Under TDs", value=0.0, step=0.1)

    st.markdown("### 📈 QB & Defense Stats")
    col6, col7, col8 = st.columns(3)
    with col6:
        qb_yards = st.number_input("QB Yards/Game", value=0.0, step=0.1)
    with col7:
        qb_td = st.number_input("QB TD/Game", value=0.0, step=0.1)
    with col8:
        pass_attempts = st.number_input("Pass Attempts/Game", value=0.0, step=0.1)

    col9, col10 = st.columns(2)
    with col9:
        def_yds_allowed = st.number_input("Defense Yards Allowed/Game", value=0.0, step=0.1)
    with col10:
        def_td_allowed = st.number_input("Defense Pass TDs/Game", value=0.0, step=0.1)

    def_pass_rank = classify_def_tier(def_yds_allowed)

    if st.button("🎯 Simulate Player"):
        avg_yds = (0.65 * qb_yards + 0.35 * def_yds_allowed) * (1.08 if pass_attempts >= 36 else 1.0)
        avg_tds = (qb_td + def_td_allowed) / 2
        n_attempts = pass_attempts
        p_per_attempt = avg_tds / n_attempts if n_attempts > 0 else 0

        std_over_prob = logistic_prob(avg_yds, standard_yds_line)
        std_under_prob = round(100 - std_over_prob, 2)
        alt_over_prob = logistic_prob(avg_yds, alt_yds_line)

        prob_0 = binomial_probability(0, int(n_attempts), p_per_attempt)
        prob_1 = binomial_probability(1, int(n_attempts), p_per_attempt)
        under_tds_prob = round((prob_0 + prob_1) * 100, 2)

        props = [
            {"Prop": "Standard Over", "True Prob": std_over_prob, "Odds": odds_over_std},
            {"Prop": "Standard Under", "True Prob": std_under_prob, "Odds": odds_under_std},
            {"Prop": "Alt Over", "True Prob": alt_over_prob, "Odds": odds_alt_over},
            {"Prop": "Under 1.5 TDs", "True Prob": under_tds_prob, "Odds": odds_under_tds},
        ]

# === WR SECTION ===
elif position == "Wide Receiver":
    st.markdown("### 📋 WR Input & Matchup Data")
    player = st.text_input("Receiver Name", value="")
    opponent_team = st.text_input("Opponent Team", value="")
    col1, col2 = st.columns(2)
    with col1:
        standard_rec_line = st.number_input("Receiving Yards Line", value=0.0, step=0.1)
        odds_over_rec = st.number_input("Odds Over (Receiving Yards)", value=0.0, step=0.1)
    with col2:
        odds_under_rec = st.number_input("Odds Under (Receiving Yards)", value=0.0, step=0.1)
        alt_rec_line = st.number_input("Alt Receiving Yards", value=0.0, step=0.1)
        odds_alt_rec = st.number_input("Odds for Alt Receiving Line", value=0.0, step=0.1)
    st.markdown("### 📈 WR & Defense Stats")
    rec_avg = st.number_input("Player Receiving Yards/Game", value=0.0, step=0.1)
    def_rec_yds_allowed = st.number_input("Defense Receiving Yards Allowed/Game", value=0.0, step=0.1)
    def_pass_rank = classify_def_tier(def_rec_yds_allowed)

    if st.button("🎯 Simulate Player"):
        avg_yds = (0.65 * rec_avg + 0.35 * def_rec_yds_allowed)
        std_over_prob = logistic_prob(avg_yds, standard_rec_line)
        std_under_prob = round(100 - std_over_prob, 2)
        alt_over_prob = logistic_prob(avg_yds, alt_rec_line)

        props = [
            {"Prop": "Receiving Over", "True Prob": std_over_prob, "Odds": odds_over_rec},
            {"Prop": "Receiving Under", "True Prob": std_under_prob, "Odds": odds_under_rec},
            {"Prop": "Alt Receiving Over", "True Prob": alt_over_prob, "Odds": odds_alt_rec},
        ]

# === RB SECTION ===
elif position == "Running Back":
    st.markdown("### 📋 RB Input & Matchup Data")
    player = st.text_input("Running Back Name", value="")
    opponent_team = st.text_input("Opponent Team", value="")
    st.markdown("#### 🏃 Rushing Yards")
    col1, col2 = st.columns(2)
    with col1:
        rush_line = st.number_input("Rushing Yards Line", value=0.0, step=0.1)
        odds_rush_over = st.number_input("Odds Over (Rushing Yards)", value=0.0, step=0.1)
        odds_rush_under = st.number_input("Odds Under (Rushing Yards)", value=0.0, step=0.1)
    with col2:
        alt_rush_line = st.number_input("Alt Rushing Yards", value=0.0, step=0.1)
        odds_alt_rush = st.number_input("Odds for Alt Rushing Line", value=0.0, step=0.1)
    st.markdown("#### 🤝 Receptions")
    col3, col4 = st.columns(2)
    with col3:
        recs_line = st.number_input("Receptions Line", value=0.0, step=0.1)
    with col4:
        odds_over_recs = st.number_input("Odds Over (Receptions)", value=0.0, step=0.1)
        odds_under_recs = st.number_input("Odds Under (Receptions)", value=0.0, step=0.1)

    st.markdown("### 📈 RB & Defense Stats")
    rush_avg = st.number_input("Rushing Yards/Game", value=0.0, step=0.1)
    recs_avg = st.number_input("Receptions/Game", value=0.0, step=0.1)
    def_rush_yds_allowed = st.number_input("Defense Rush Yards Allowed/Game", value=0.0, step=0.1)
    def_rec_allowed = st.number_input("Defense Receptions Allowed/Game", value=0.0, step=0.1)
    def_pass_rank = classify_def_tier(def_rush_yds_allowed)

    if st.button("🎯 Simulate Player"):
        avg_rush = (0.65 * rush_avg + 0.35 * def_rush_yds_allowed)
        avg_recs = (0.65 * recs_avg + 0.35 * def_rec_allowed)

        rush_over_prob = logistic_prob(avg_rush, rush_line)
        rush_under_prob = round(100 - rush_over_prob, 2)
        alt_rush_prob = logistic_prob(avg_rush, alt_rush_line)
        recs_over_prob = logistic_prob(avg_recs, recs_line)
        recs_under_prob = round(100 - recs_over_prob, 2)

        props = [
            {"Prop": "Rush Over", "True Prob": rush_over_prob, "Odds": odds_rush_over},
            {"Prop": "Rush Under", "True Prob": rush_under_prob, "Odds": odds_rush_under},
            {"Prop": "Alt Rush Over", "True Prob": alt_rush_prob, "Odds": odds_alt_rush},
            {"Prop": "Receptions Over", "True Prob": recs_over_prob, "Odds": odds_over_recs},
            {"Prop": "Receptions Under", "True Prob": recs_under_prob, "Odds": odds_under_recs},
        ]

# === RESULTS TABLE + PARLAY BUILDER ===
if props:
    st.markdown(f"**📊 Matchup Risk Tier:** {def_pass_rank}")
    results = []
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

    st.markdown("### 🔁 Parlay Builder: Select Props")
    selected_ids = st.multiselect("Select 2+ props to simulate parlay EV:", [p["Prop"] for p in props])
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




   
