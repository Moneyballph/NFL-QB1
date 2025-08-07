
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

st.title("🏈 Moneyball Phil: NFL Prop Simulator (v2.0)")
position = st.selectbox("Select Position", ["Quarterback", "Wide Receiver", "Running Back"])

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

def logistic_prob(x, line, scale=15):
    return round((1 / (1 + math.exp(-(x - line) / scale))) * 100, 2)

def classify_def_tier(val):
    if isinstance(val, int) or isinstance(val, float):
        if val < 205:
            return "🔴 Tough"
        elif val <= 240:
            return "🟡 Average"
        else:
            return "🟢 Easy"
    return "Unknown"

# ✅ Quarterback Module
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

    st.subheader("🎯 Touchdown Props")
    td_line = st.number_input("Passing TD Line", value=1.5)
    td_under_odds = st.number_input("Odds for Under TDs", value=0.0)

    st.subheader("📈 QB & Defense Stats")
    ypg = st.number_input("QB Yards/Game", value=0.0)
    tds = st.number_input("QB TD/Game", value=0.0)
    attempts = st.number_input("Pass Attempts/Game", value=0.0)
    def_yds = st.number_input("Defense Yards Allowed/Game", value=0.0)
    def_tds = st.number_input("Defense Pass TDs/Game", value=0.0)

    if st.button("Simulate QB Props"):
        std_prob = logistic_prob(ypg, std_line)
        alt_prob = logistic_prob(ypg, alt_line)
        td_prob = logistic_prob(tds, td_line, scale=0.5)
        tier = classify_def_tier(def_yds)

        st.success(f"📈 Standard Yards Hit %: {std_prob}%  | Alt Line %: {alt_prob}%")
        st.success(f"📉 Under {td_line} TDs Hit %: {100 - td_prob}%")
        st.info(f"Opponent Defense Tier: {tier}")

        st.session_state.all_props.extend([
            {"Player": name, "Prop": f"Over {std_line} Pass Yds", "True Prob": std_prob, "Odds": over_std},
            {"Player": name, "Prop": f"Over {alt_line} Alt Pass Yds", "True Prob": alt_prob, "Odds": alt_odds},
            {"Player": name, "Prop": f"Under {td_line} Pass TDs", "True Prob": 100 - td_prob, "Odds": td_under_odds},
        ])

# ✅ Wide Receiver Module
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

    st.subheader("📈 WR & Defense Stats")
    ypg = st.number_input("WR Yards/Game", value=0.0)
    rpg = st.number_input("WR Receptions/Game", value=0.0)
    def_yds = st.number_input("Defense WR Yards Allowed/Game", value=0.0)
    def_rec = st.number_input("Defense WR Receptions Allowed/Game", value=0.0)

    if st.button("Simulate WR Props"):
        std_prob = logistic_prob(ypg, std_line)
        alt_prob = logistic_prob(ypg, alt_line)
        rec_prob = logistic_prob(rpg, rec_line, scale=1.5)
        tier = classify_def_tier(def_yds)

        st.success(f"📈 Standard Yards Hit %: {std_prob}%  | Alt Line %: {alt_prob}%")
        st.success(f"🎯 Receptions Over {rec_line} Hit %: {rec_prob}%")
        st.success(f"📉 Receptions Under {rec_line} Hit %: {100 - rec_prob}%")
        st.info(f"Opponent Defense Tier: {tier} | Avg Receptions Allowed: {def_rec}")

        st.session_state.all_props.extend([
            {"Player": name, "Prop": f"Over {std_line} Rec Yds", "True Prob": std_prob, "Odds": over_std},
            {"Player": name, "Prop": f"Under {std_line} Rec Yds", "True Prob": 100 - std_prob, "Odds": under_std},
            {"Player": name, "Prop": f"Over {alt_line} Alt Rec Yds", "True Prob": alt_prob, "Odds": alt_odds},
            {"Player": name, "Prop": f"Over {rec_line} Receptions", "True Prob": rec_prob, "Odds": rec_over_odds},
            {"Player": name, "Prop": f"Under {rec_line} Receptions", "True Prob": 100 - rec_prob, "Odds": rec_under_odds},
        ])

# ✅ Running Back Module
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

    st.subheader("📈 RB & Defense Stats")
    ypg = st.number_input("RB Yards/Game", value=0.0)
    rpg = st.number_input("RB Receptions/Game", value=0.0)
    def_yds = st.number_input("Defense Rush Yards Allowed/Game", value=0.0)
    def_rec = st.number_input("Defense RB Receptions Allowed/Game", value=0.0)

    if st.button("Simulate RB Props"):
        std_prob = logistic_prob(ypg, std_line)
        alt_prob = logistic_prob(ypg, alt_line)
        rec_prob = logistic_prob(rpg, rec_line, scale=1.5)
        tier = classify_def_tier(def_yds)

        st.success(f"📈 Standard Rush Yards Hit %: {std_prob}%  | Alt Line %: {alt_prob}%")
        st.success(f"🎯 Receptions Over {rec_line} Hit %: {rec_prob}%")
        st.success(f"📉 Receptions Under {rec_line} Hit %: {100 - rec_prob}%")
        st.info(f"Opponent Defense Tier: {tier} | Avg Receptions Allowed: {def_rec}")

        st.session_state.all_props.extend([
            {"Player": name, "Prop": f"Over {std_line} Rush Yds", "True Prob": std_prob, "Odds": over_std},
            {"Player": name, "Prop": f"Under {std_line} Rush Yds", "True Prob": 100 - std_prob, "Odds": under_std},
            {"Player": name, "Prop": f"Over {alt_line} Alt Rush Yds", "True Prob": alt_prob, "Odds": alt_odds},
            {"Player": name, "Prop": f"Over {rec_line} Receptions", "True Prob": rec_prob, "Odds": rec_over_odds},
            {"Player": name, "Prop": f"Under {rec_line} Receptions", "True Prob": 100 - rec_prob, "Odds": rec_under_odds},
        ])

# ✅ Top Player Board
# st.markdown("---")
# st.subheader("📊 Top Player Board")
# if st.session_state.all_props:
#     sorted_props = sorted(st.session_state.all_props, key=lambda x: x["True Prob"], reverse=True)
#     for prop in sorted_props:
#         ev = ev_calc(prop["True Prob"] / 100, prop["Odds"])
#         tier = get_tier(prop["True Prob"])
#         st.markdown(f"**{prop['Player']} – {prop['Prop']}**  ")
#         st.markdown(f"True Prob: `{prop['True Prob']}%` | Odds: `{prop['Odds']}` | EV: `{ev}%` | Tier: {tier}", unsafe_allow_html=True)
# else:
#     st.info("No props simulated yet. Run a player simulation to see results here.")


# ✅ Parlay Builder
st.markdown("---")
st.subheader("💡 Parlay Builder")
if len(st.session_state.all_props) >= 2:
    parlay_choices = [f"{p['Player']} – {p['Prop']}" for p in st.session_state.all_props]
    selected = st.multiselect("Select Props for Parlay (2+)", parlay_choices)

    if selected and len(selected) >= 2:
        selected_props = [p for p in st.session_state.all_props if f"{p['Player']} – {p['Prop']}" in selected]
        combined_prob = 1
        combined_ev = 0

        for p in selected_props:
            combined_prob *= p["True Prob"] / 100
            combined_ev += ev_calc(p["True Prob"] / 100, p["Odds"])

        combined_prob = round(combined_prob * 100, 2)
        avg_ev = round(combined_ev / len(selected_props), 2)

        st.success(f"Parlay Hit Probability: `{combined_prob}%` | Avg EV: `{avg_ev}%")
else:
    st.info("Add at least 2 simulated props to enable the parlay builder.")






   
