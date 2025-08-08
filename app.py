
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

# ✅ Top Player Board
st.markdown("---")
show_board = st.checkbox("Show Top Player Board", value=False)
if show_board:
    st.subheader("📊 Top Player Board")
    if st.session_state.all_props:
        top_by_player = {}
        for prop in st.session_state.all_props:
            player = prop["Player"]
            if player not in top_by_player:
                top_by_player[player] = []
            top_by_player[player].append(prop)

        for player, props in top_by_player.items():
            top_props = sorted(props, key=lambda x: x["True Prob"], reverse=True)[:2]
            for prop in top_props:
                ev = ev_calc(prop["True Prob"] / 100, prop["Odds"])
                tier = get_tier(prop["True Prob"])
                st.markdown(f"**{prop['Player']} – {prop['Prop']}**  ")
                st.markdown(
                    f"True Prob: `{prop['True Prob']}%` | Odds: `{prop['Odds']}` | EV: `{ev}%` | Tier: {tier}",
                    unsafe_allow_html=True
                )
    else:
        st.info("No props simulated yet. Run a player simulation to see results here.")

# ✅ Cleaned-Up Top Player Board with Expanders
st.markdown("---")
show_board = st.checkbox("📊 Show Top Player Board", value=False)

if show_board:
    if st.session_state.all_props:
        # Group props by player
        grouped = {}
        for prop in st.session_state.all_props:
            grouped.setdefault(prop['Player'], []).append(prop)

        st.subheader("📊 Top Player Board (Grouped)")

        for player, props in grouped.items():
            with st.expander(f"{player} – {len(props)} Props Simulated"):
                for prop in props:
                    ev = ev_calc(prop["True Prob"] / 100, prop["Odds"])
                    tier = get_tier(prop["True Prob"])
                    st.markdown(
                        f"- **{prop['Prop']}** → True Prob: `{prop['True Prob']}%` | Odds: `{prop['Odds']}` | EV: `{ev}%` | Tier: {tier}",
                        unsafe_allow_html=True
                    )
    else:
        st.info("No props simulated yet. Run a player simulation to see results here.")







   
