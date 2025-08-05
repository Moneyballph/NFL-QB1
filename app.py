
import streamlit as st
import math
import base64

# ✅ Background Setup
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

# ✅ Page Config
st.set_page_config(page_title="🏈 Moneyball Phil: NFL Prop Simulator", layout="centered")
set_background("ChatGPT Image Jul 14, 2025, 09_58_55 AM.png")

# ✅ App Title and Navigation
st.title("🏈 Moneyball Phil: NFL Prop Simulator (v2.0)")
position = st.selectbox("Select Position", ["Quarterback", "Wide Receiver", "Running Back"])

# ✅ Storage for props across simulations
if "all_props" not in st.session_state:
    st.session_state.all_props = []

# ✅ Helper Functions
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

# ✅ Quarterback Section
if position == "Quarterback":
    st.markdown("### 🎯 Quarterback Inputs")
    qb_name = st.text_input("Quarterback Name", value="")
    opponent_team = st.text_input("Opponent Team", value="")

    st.subheader("📊 Passing Yards Props")
    col1, col2, col3 = st.columns(3)
    with col1:
        standard_yds_line = st.number_input("Standard Passing Yards Line", value=0.0, step=0.1, format="%.1f")
    with col2:
        odds_over_std = st.number_input("Odds Over (Standard)", value=0.0, step=0.1, format="%.1f")
    with col3:
        odds_under_std = st.number_input("Odds Under (Standard)", value=0.0, step=0.1, format="%.1f")

    col4, col5 = st.columns(2)
    with col4:
        alt_yds_line = st.number_input("Alt Over Line", value=0.0, step=0.1, format="%.1f")
    with col5:
        odds_alt_over = st.number_input("Odds for Alt Over", value=0.0, step=0.1, format="%.1f")

    st.subheader("🎯 Touchdown Props")
    col6, col7 = st.columns(2)
    with col6:
        td_line = st.number_input("Passing TD Line", value=1.5, step=0.1, format="%.1f")
    with col7:
        odds_under_tds = st.number_input("Odds for Under TDs", value=0.0, step=0.1, format="%.1f")

    st.subheader("📈 QB & Defense Stats")
    col8, col9, col10 = st.columns(3)
    with col8:
        qb_yards = st.number_input("QB Yards/Game", value=0.0, step=0.1, format="%.1f")
    with col9:
        qb_td = st.number_input("QB TD/Game", value=0.0, step=0.1, format="%.1f")
    with col10:
        pass_attempts = st.number_input("Pass Attempts/Game", value=0.0, step=0.1, format="%.1f")

    col11, col12 = st.columns(2)
    with col11:
        def_yds_allowed = st.number_input("Defense Yards Allowed/Game", value=0.0, step=0.1, format="%.1f")
    with col12:
        def_td_allowed = st.number_input("Defense Pass TDs/Game", value=0.0, step=0.1, format="%.1f")

    if st.button("🎯 Simulate QB"):
        st.subheader("📋 QB Prop Simulation Results")
        avg_yds = (0.65 * qb_yards + 0.35 * def_yds_allowed) * (1.08 if pass_attempts >= 36 else 1.0)
        avg_tds = (qb_td + def_td_allowed) / 2
        p_per_attempt = avg_tds / pass_attempts if pass_attempts > 0 else 0

        std_over = logistic_prob(avg_yds, standard_yds_line)
        std_under = round(100 - std_over, 2)
        alt_over = logistic_prob(avg_yds, alt_yds_line)

        prob_0 = binomial_probability(0, int(pass_attempts), p_per_attempt)
        prob_1 = binomial_probability(1, int(pass_attempts), p_per_attempt)
        td_under = round((prob_0 + prob_1) * 100, 2)

        qb_props = [
            {"Player": qb_name, "Prop": "Standard Over", "True Prob": std_over, "Odds": odds_over_std},
            {"Player": qb_name, "Prop": "Standard Under", "True Prob": std_under, "Odds": odds_under_std},
            {"Player": qb_name, "Prop": "Alt Over", "True Prob": alt_over, "Odds": odds_alt_over},
            {"Player": qb_name, "Prop": "Under 1.5 TDs", "True Prob": td_under, "Odds": odds_under_tds},
        ]

        st.session_state.all_props.extend(qb_props)
        st.success("✅ QB props added to board.")

# ✅ Wide Receiver Section
if position == "Wide Receiver":
    st.markdown("### 🎯 Wide Receiver Inputs")
    wr_name = st.text_input("WR Name", value="")
    wr_yds_avg = st.number_input("Receiving Yards/Game", value=0.0, step=0.1, format="%.1f")
    wr_rec_avg = st.number_input("Receptions/Game", value=0.0, step=0.1, format="%.1f")
    def_rank_yds = st.number_input("Defense Rank vs WR Yards (1-32)", value=16)
    def_rank_rec = st.number_input("Defense Rank vs WR Receptions (1-32)", value=16)

    col1, col2, col3 = st.columns(3)
    with col1:
        std_yds_line = st.number_input("Standard Rec. Yards Line", value=0.0, step=0.1, format="%.1f")
    with col2:
        odds_std_over = st.number_input("Odds Over (Yards)", value=0.0, step=0.1, format="%.1f")
    with col3:
        odds_std_under = st.number_input("Odds Under (Yards)", value=0.0, step=0.1, format="%.1f")

    col4, col5 = st.columns(2)
    with col4:
        alt_yds_line = st.number_input("Alt Rec. Yards Line", value=0.0, step=0.1, format="%.1f")
    with col5:
        odds_alt_over = st.number_input("Odds for Alt Over Yards", value=0.0, step=0.1, format="%.1f")

    col6, col7 = st.columns(2)
    with col6:
        rec_line = st.number_input("Receptions Line", value=0.0, step=0.1, format="%.1f")
    with col7:
        odds_rec_over = st.number_input("Odds for Over Receptions", value=0.0, step=0.1, format="%.1f")

    if st.button("🎯 Simulate WR"):
        adj_yds = wr_yds_avg * (1.1 if def_rank_yds >= 24 else 1.0 if def_rank_yds >= 12 else 0.9)
        adj_rec = wr_rec_avg * (1.1 if def_rank_rec >= 24 else 1.0 if def_rank_rec >= 12 else 0.9)

        std_yds_prob = logistic_prob(adj_yds, std_yds_line)
        std_yds_under = round(100 - std_yds_prob, 2)
        alt_yds_prob = logistic_prob(adj_yds, alt_yds_line)
        rec_prob = logistic_prob(adj_rec, rec_line)

        wr_props = [
            {"Player": wr_name, "Prop": "Standard Over Yards", "True Prob": std_yds_prob, "Odds": odds_std_over},
            {"Player": wr_name, "Prop": "Standard Under Yards", "True Prob": std_yds_under, "Odds": odds_std_under},
            {"Player": wr_name, "Prop": "Alt Over Yards", "True Prob": alt_yds_prob, "Odds": odds_alt_over},
            {"Player": wr_name, "Prop": "Over Receptions", "True Prob": rec_prob, "Odds": odds_rec_over},
        ]

        st.session_state.all_props.extend(wr_props)
        st.success("✅ WR props added to board.")

# ✅ Running Back Section
if position == "Running Back":
    st.markdown("### 🎯 Running Back Inputs")
    rb_name = st.text_input("RB Name", value="")
    rush_avg = st.number_input("Rushing Yards/Game", value=0.0, step=0.1, format="%.1f")
    rec_avg = st.number_input("Receptions/Game", value=0.0, step=0.1, format="%.1f")
    def_rank_rush = st.number_input("Defense Rank vs Rush Yards (1-32)", value=16)
    def_rank_rec = st.number_input("Defense Rank vs RB Receptions (1-32)", value=16)

    col1, col2, col3 = st.columns(3)
    with col1:
        std_rush_line = st.number_input("Standard Rush Yards Line", value=0.0, step=0.1, format="%.1f")
    with col2:
        odds_rush_over = st.number_input("Odds Over (Rush)", value=0.0, step=0.1, format="%.1f")
    with col3:
        odds_rush_under = st.number_input("Odds Under (Rush)", value=0.0, step=0.1, format="%.1f")

    col4, col5 = st.columns(2)
    with col4:
        alt_rush_line = st.number_input("Alt Over Rush Yards", value=0.0, step=0.1, format="%.1f")
    with col5:
        odds_alt_rush = st.number_input("Odds Alt Over Rush", value=0.0, step=0.1, format="%.1f")

    col6, col7 = st.columns(2)
    with col6:
        rec_line = st.number_input("Receptions Line", value=0.0, step=0.1, format="%.1f")
    with col7:
        odds_rec_over = st.number_input("Odds Over Receptions", value=0.0, step=0.1, format="%.1f")

    if st.button("🎯 Simulate RB"):
        adj_rush = rush_avg * (1.1 if def_rank_rush >= 24 else 1.0 if def_rank_rush >= 12 else 0.9)
        adj_rec = rec_avg * (1.1 if def_rank_rec >= 24 else 1.0 if def_rank_rec >= 12 else 0.9)

        std_rush_prob = logistic_prob(adj_rush, std_rush_line)
        std_rush_under = round(100 - std_rush_prob, 2)
        alt_rush_prob = logistic_prob(adj_rush, alt_rush_line)
        rec_prob = logistic_prob(adj_rec, rec_line)

        rb_props = [
            {"Player": rb_name, "Prop": "Standard Over Rush", "True Prob": std_rush_prob, "Odds": odds_rush_over},
            {"Player": rb_name, "Prop": "Standard Under Rush", "True Prob": std_rush_under, "Odds": odds_rush_under},
            {"Player": rb_name, "Prop": "Alt Over Rush", "True Prob": alt_rush_prob, "Odds": odds_alt_rush},
            {"Player": rb_name, "Prop": "Over Receptions", "True Prob": rec_prob, "Odds": odds_rec_over},
        ]

        st.session_state.all_props.extend(rb_props)
        st.success("✅ RB props added to board.")

# ✅ Top Hit Board
if st.session_state.all_props:
    st.markdown("### 🧠 Top Hit Board (Ranked by True Probability)")
    sorted_props = sorted(st.session_state.all_props, key=lambda x: x["True Prob"], reverse=True)
    board_data = [
        {
            "Player": p["Player"],
            "Prop": p["Prop"],
            "True Probability": f"{p['True Prob']}%",
            "Tier": get_tier(p["True Prob"])
        }
        for p in sorted_props
    ]
    st.dataframe(board_data)

# ✅ Parlay Builder
if st.session_state.all_props:
    st.markdown("### 💥 Parlay Builder: Select Props")
    selected = st.multiselect(
        "Select 2 or more props for parlay",
        [f"{p['Player']} - {p['Prop']}" for p in st.session_state.all_props]
    )

    if len(selected) >= 2:
        chosen = [p for p in st.session_state.all_props if f"{p['Player']} - {p['Prop']}" in selected]
        true_prob = math.prod([p["True Prob"] / 100 for p in chosen])
        implied_prob_total = math.prod([implied_prob(p["Odds"]) for p in chosen])
        parlay_ev = round((true_prob - implied_prob_total) * 100, 2)
        tier = get_tier(true_prob * 100)

        st.write(f"**True Probability:** {true_prob:.2%}")
        st.write(f"**Implied Probability:** {implied_prob_total:.2%}")
        st.write(f"**EV %:** {parlay_ev}%")
        st.write(f"**Tier:** {tier}")





   
