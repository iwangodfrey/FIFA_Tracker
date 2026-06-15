import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DB_FILE = "fifa_tracker.db"

st.set_page_config(page_title="FIFA World Cup 2026", page_icon="⚽", layout="wide")

st.markdown("""
<style>
    /* Dark background */
    .stApp { background-color: #0a0e1a; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0d1424;
        border-right: 1px solid #1e2d4a;
    }
    [data-testid="stSidebar"] * { color: #c8d6e5 !important; }

    /* All text */
    html, body, [class*="css"] { color: #e8edf5; }

    /* Header banner */
    .fifa-header {
        background: linear-gradient(135deg, #0a1628 0%, #1a3a6e 50%, #0a1628 100%);
        border: 1px solid #2a4a8e;
        border-radius: 12px;
        padding: 28px 36px;
        margin-bottom: 28px;
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .fifa-header h1 {
        color: #f0c040 !important;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .fifa-header p {
        color: #8da8cc;
        margin: 4px 0 0 0;
        font-size: 0.95rem;
    }

    /* Section headers */
    h2, h3 { color: #f0c040 !important; font-weight: 700; }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #0f1e36 0%, #162847 100%);
        border: 1px solid #1e3a6e;
        border-radius: 10px;
        padding: 20px 24px;
        text-align: center;
    }
    .metric-card .value {
        font-size: 2.4rem;
        font-weight: 800;
        color: #f0c040;
        line-height: 1;
    }
    .metric-card .label {
        font-size: 0.8rem;
        color: #8da8cc;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 6px;
    }

    /* Divider */
    .section-divider {
        border: none;
        border-top: 1px solid #1e2d4a;
        margin: 28px 0;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
    .stDataFrame { background-color: #0f1e36; }

    /* Radio buttons */
    [data-testid="stRadio"] label { color: #c8d6e5 !important; }

    /* Inputs */
    .stSelectbox > div, .stNumberInput > div { background-color: #0f1e36; }

    /* Top header bar */
    header[data-testid="stHeader"] {
        background-color: #0a0e1a;
        border-bottom: 1px solid #1e2d4a;
    }

    /* Toolbar icons */
    [data-testid="stToolbar"] { color: #8da8cc; }

    /* Remove default streamlit padding */
    .block-container { padding-top: 3.5rem; }
</style>
""", unsafe_allow_html=True)

COLORS = {
    "gold": "#f0c040",
    "blue": "#1a6eb5",
    "dark": "#0a0e1a",
    "card": "#0f1e36",
    "text": "#e8edf5",
    "muted": "#8da8cc",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,30,54,0.6)",
    font=dict(color=COLORS["text"], family="Inter, sans-serif"),
    xaxis=dict(gridcolor="#1e2d4a", linecolor="#1e2d4a"),
    yaxis=dict(gridcolor="#1e2d4a", linecolor="#1e2d4a"),
    margin=dict(l=20, r=20, t=40, b=20),
)

@st.cache_data
def query(sql, params=()):
    con = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(sql, con, params=params)
    con.close()
    return df

def metric_card(label, value):
    return f"""
    <div class="metric-card">
        <div class="value">{value}</div>
        <div class="label">{label}</div>
    </div>"""

st.markdown("""
<div class="fifa-header">
    <div>
        <h1>⚽ FIFA World Cup 2026</h1>
        <p>Player Performance Tracker &nbsp;·&nbsp; USA · Canada · Mexico</p>
    </div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("", ["Overview", "Top Scorers", "Team Stats", "Player Lookup", "Player Comparison", "Match Results"])
st.sidebar.markdown("<hr style='border-color:#1e2d4a'>", unsafe_allow_html=True)
st.sidebar.markdown("<span style='color:#8da8cc;font-size:0.75rem'>FIFA World Cup 2026 · Data Analytics</span>", unsafe_allow_html=True)

# ── OVERVIEW ────────────────────────────────────────────────────────────────
if page == "Overview":
    totals = query("""
        SELECT
            COUNT(DISTINCT player_id) AS players,
            COUNT(DISTINCT match_id) AS matches,
            COUNT(DISTINCT team) AS teams,
            SUM(goals) AS goals
        FROM player_stats
    """)

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(metric_card("Players", f"{int(totals['players'][0]):,}"), unsafe_allow_html=True)
    col2.markdown(metric_card("Matches", f"{int(totals['matches'][0]):,}"), unsafe_allow_html=True)
    col3.markdown(metric_card("Teams", f"{int(totals['teams'][0]):,}"), unsafe_allow_html=True)
    col4.markdown(metric_card("Goals Scored", f"{int(totals['goals'][0]):,}"), unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("### Top 10 Scorers")
        top10 = query("SELECT player_name, team, total_goals, total_assists, matches_played FROM top_scorers LIMIT 10")
        fig = px.bar(
            top10, x="total_goals", y="player_name", orientation="h",
            color="total_goals", color_continuous_scale=["#1a3a6e", "#f0c040"],
            labels={"total_goals": "Goals", "player_name": ""},
            text="total_goals",
        )
        fig.update_traces(textposition="outside", textfont_color=COLORS["text"])
        fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False, height=380)
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### Goals by Stage")
        stage_goals = query("""
            SELECT tournament_stage, SUM(goals) AS goals
            FROM player_stats GROUP BY tournament_stage ORDER BY goals DESC
        """)
        fig2 = px.pie(
            stage_goals, names="tournament_stage", values="goals",
            color_discrete_sequence=px.colors.sequential.Blues_r,
            hole=0.45,
        )
        fig2.update_layout(**PLOTLY_LAYOUT, height=380, showlegend=True,
                           legend=dict(font=dict(color=COLORS["text"])))
        fig2.update_traces(textfont_color="white")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("### Goals & Assists — Top 15 Players")
    top15 = query("SELECT player_name, total_goals, total_assists FROM top_scorers LIMIT 15")
    fig3 = go.Figure(data=[
        go.Bar(name="Goals", x=top15["player_name"], y=top15["total_goals"], marker_color=COLORS["gold"]),
        go.Bar(name="Assists", x=top15["player_name"], y=top15["total_assists"], marker_color=COLORS["blue"]),
    ])
    fig3.update_layout(**PLOTLY_LAYOUT, barmode="group", height=340,
                       legend=dict(font=dict(color=COLORS["text"])))
    st.plotly_chart(fig3, use_container_width=True)

# ── TOP SCORERS ──────────────────────────────────────────────────────────────
elif page == "Top Scorers":
    st.markdown("## Top Scorers & Assisters")

    col1, col2, col3 = st.columns(3)
    with col1:
        min_goals = st.number_input("Min goals", min_value=0, value=1)
    with col2:
        positions = ["All"] + query("SELECT DISTINCT position FROM player_stats ORDER BY position")["position"].tolist()
        pos_filter = st.selectbox("Position", positions)
    with col3:
        nations = ["All"] + query("SELECT DISTINCT nationality FROM player_stats ORDER BY nationality")["nationality"].tolist()
        nat_filter = st.selectbox("Nationality", nations)

    sql = "SELECT player_name, team, nationality, position, total_goals, total_assists, total_shots_on_target, matches_played FROM top_scorers WHERE total_goals >= ?"
    params = [min_goals]
    if pos_filter != "All":
        sql += " AND position = ?"; params.append(pos_filter)
    if nat_filter != "All":
        sql += " AND nationality = ?"; params.append(nat_filter)

    df = query(sql, params)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1.4])
    with col_l:
        st.dataframe(df, use_container_width=True, hide_index=True)
    with col_r:
        fig = px.scatter(
            df.head(30), x="total_goals", y="total_assists",
            size="matches_played", color="total_goals",
            hover_name="player_name", text="player_name",
            color_continuous_scale=["#1a3a6e", "#f0c040"],
            labels={"total_goals": "Goals", "total_assists": "Assists"},
            title="Goals vs Assists (top 30)",
        )
        fig.update_traces(textposition="top center", textfont=dict(size=9, color=COLORS["muted"]))
        fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False, height=460)
        st.plotly_chart(fig, use_container_width=True)

# ── TEAM STATS ───────────────────────────────────────────────────────────────
elif page == "Team Stats":
    st.markdown("## Team Statistics")

    df = query("SELECT * FROM team_stats")

    col1, col2, col3 = st.columns(3)
    col1.markdown(metric_card("Total Teams", len(df)), unsafe_allow_html=True)
    col2.markdown(metric_card("Highest Wins", int(df["wins"].max())), unsafe_allow_html=True)
    col3.markdown(metric_card("Most Goals", int(df["goals_scored"].max())), unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    col_l, col_r = st.columns([1.5, 1])
    with col_l:
        top_teams = df.nlargest(15, "wins")
        fig = px.bar(
            top_teams, x="team", y=["wins", "draws", "losses"],
            color_discrete_map={"wins": COLORS["gold"], "draws": COLORS["blue"], "losses": "#c0392b"},
            labels={"value": "Matches", "variable": "Result"},
            title="Win/Draw/Loss — Top 15 Teams",
            barmode="stack",
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=400, legend=dict(font=dict(color=COLORS["text"])))
        st.plotly_chart(fig, use_container_width=True)
    with col_r:
        fig2 = px.bar(
            df.nlargest(15, "goals_scored"), x="goals_scored", y="team",
            orientation="h", color="goals_scored",
            color_continuous_scale=["#1a3a6e", "#f0c040"],
            title="Goals Scored — Top 15",
            labels={"goals_scored": "Goals", "team": ""},
        )
        fig2.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False, height=400)
        fig2.update_yaxes(autorange="reversed")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("### Full Table")
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── PLAYER LOOKUP ────────────────────────────────────────────────────────────
elif page == "Player Lookup":
    st.markdown("## Player Lookup")

    player_names = query("SELECT DISTINCT player_name FROM player_stats ORDER BY player_name")["player_name"].tolist()
    selected = st.selectbox("Search for a player", player_names)

    if selected:
        info = query("""
            SELECT DISTINCT age, nationality, team, position, club_name, preferred_foot, height_cm, weight_kg
            FROM player_stats WHERE player_name = ?
        """, [selected])

        totals = query("""
            SELECT SUM(goals) AS goals, SUM(assists) AS assists,
                   SUM(minutes_played) AS minutes, ROUND(AVG(player_rating), 2) AS avg_rating,
                   COUNT(DISTINCT match_id) AS matches
            FROM player_stats WHERE player_name = ?
        """, [selected])

        st.markdown(f"### {selected}")
        detail = info.iloc[0]
        st.markdown(f"<span style='color:{COLORS['muted']}'>{detail['team']} &nbsp;·&nbsp; {detail['position']} &nbsp;·&nbsp; {detail['nationality']} &nbsp;·&nbsp; {detail['club_name']}</span>", unsafe_allow_html=True)
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.markdown(metric_card("Goals", int(totals["goals"][0])), unsafe_allow_html=True)
        col2.markdown(metric_card("Assists", int(totals["assists"][0])), unsafe_allow_html=True)
        col3.markdown(metric_card("Minutes", f"{int(totals['minutes'][0]):,}"), unsafe_allow_html=True)
        col4.markdown(metric_card("Matches", int(totals["matches"][0])), unsafe_allow_html=True)
        col5.markdown(metric_card("Avg Rating", totals["avg_rating"][0]), unsafe_allow_html=True)

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        stats = query("""
            SELECT match_date, opponent_team, tournament_stage, match_result,
                   minutes_played, goals, assists, shots_on_target, pass_accuracy,
                   tackles, interceptions, player_rating
            FROM player_stats WHERE player_name = ? ORDER BY match_date
        """, [selected])

        col_l, col_r = st.columns([1.2, 1])
        with col_l:
            st.markdown("### Match by Match")
            st.dataframe(stats, use_container_width=True, hide_index=True)
        with col_r:
            fig = px.line(
                stats, x="match_date", y="player_rating",
                markers=True, title="Player Rating per Match",
                labels={"player_rating": "Rating", "match_date": "Date"},
                color_discrete_sequence=[COLORS["gold"]],
            )
            fig.update_layout(**PLOTLY_LAYOUT, height=300)
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.bar(
                stats, x="match_date", y=["goals", "assists"],
                color_discrete_map={"goals": COLORS["gold"], "assists": COLORS["blue"]},
                title="Goals & Assists per Match",
                labels={"value": "", "match_date": "Date"},
                barmode="stack",
            )
            fig2.update_layout(**PLOTLY_LAYOUT, height=260, legend=dict(font=dict(color=COLORS["text"])))
            st.plotly_chart(fig2, use_container_width=True)

# ── PLAYER COMPARISON ────────────────────────────────────────────────────────
elif page == "Player Comparison":
    st.markdown("## Player Comparison")

    player_names = query("SELECT DISTINCT player_name FROM player_stats ORDER BY player_name")["player_name"].tolist()

    col1, col2 = st.columns(2)
    with col1:
        player_a = st.selectbox("Player A", player_names, index=0)
    with col2:
        player_b = st.selectbox("Player B", player_names, index=1)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    def get_totals(name):
        return query("""
            SELECT
                SUM(goals) AS goals,
                SUM(assists) AS assists,
                SUM(shots_on_target) AS shots_on_target,
                SUM(minutes_played) AS minutes,
                ROUND(AVG(player_rating), 2) AS avg_rating,
                COUNT(DISTINCT match_id) AS matches,
                ROUND(AVG(pass_accuracy) * 100, 1) AS pass_accuracy,
                SUM(tackles) AS tackles,
                SUM(interceptions) AS interceptions,
                ROUND(AVG(distance_covered_km), 2) AS avg_distance_km,
                ROUND(MAX(top_speed_kmh), 1) AS top_speed,
                SUM(yellow_cards) AS yellow_cards,
                SUM(red_cards) AS red_cards
            FROM player_stats WHERE player_name = ?
        """, [name]).iloc[0]

    def get_info(name):
        return query("""
            SELECT DISTINCT team, position, nationality, club_name, age
            FROM player_stats WHERE player_name = ?
        """, [name]).iloc[0]

    st.markdown("<br>", unsafe_allow_html=True)
    compare_clicked = st.button("Compare Players", type="primary", use_container_width=False)

    if not compare_clicked:
        st.stop()

    if player_a == player_b:
        st.error("Please select two different players to compare.")
        st.stop()

    ta = get_totals(player_a)
    tb = get_totals(player_b)
    ia = get_info(player_a)
    ib = get_info(player_b)

    # Player headers
    col_a, col_vs, col_b = st.columns([5, 1, 5])
    with col_a:
        st.markdown(f"### {player_a}")
        st.markdown(f"<span style='color:{COLORS['muted']}'>{ia['team']} · {ia['position']} · {ia['nationality']}</span>", unsafe_allow_html=True)
    with col_vs:
        st.markdown("<div style='text-align:center;font-size:1.8rem;font-weight:800;color:#f0c040;padding-top:8px'>VS</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"### {player_b}")
        st.markdown(f"<span style='color:{COLORS['muted']}'>{ib['team']} · {ib['position']} · {ib['nationality']}</span>", unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # stat_row takes raw numeric values for comparison, display strings for rendering
    def stat_row(label, raw_a, raw_b, display_a=None, display_b=None, higher_is_better=True):
        a, b = float(raw_a), float(raw_b)
        if higher_is_better:
            color_a = COLORS["gold"] if a >= b else COLORS["muted"]
            color_b = COLORS["gold"] if b >= a else COLORS["muted"]
        else:
            color_a = COLORS["gold"] if a <= b else COLORS["muted"]
            color_b = COLORS["gold"] if b <= a else COLORS["muted"]
        show_a = display_a if display_a is not None else raw_a
        show_b = display_b if display_b is not None else raw_b
        return f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:10px 0;border-bottom:1px solid #1e2d4a;">
            <span style="font-size:1.3rem;font-weight:700;color:{color_a};width:100px;text-align:left">{show_a}</span>
            <span style="color:{COLORS['muted']};font-size:0.8rem;text-transform:uppercase;
                         letter-spacing:1px;text-align:center;flex:1">{label}</span>
            <span style="font-size:1.3rem;font-weight:700;color:{color_b};width:100px;text-align:right">{show_b}</span>
        </div>"""

    html = ""
    html += stat_row("Goals", int(ta["goals"]), int(tb["goals"]))
    html += stat_row("Assists", int(ta["assists"]), int(tb["assists"]))
    html += stat_row("Shots on Target", int(ta["shots_on_target"]), int(tb["shots_on_target"]))
    html += stat_row("Avg Rating", ta["avg_rating"], tb["avg_rating"])
    html += stat_row("Matches Played", int(ta["matches"]), int(tb["matches"]))
    html += stat_row("Minutes Played", int(ta["minutes"]), int(tb["minutes"]),
                     display_a=f"{int(ta['minutes']):,}", display_b=f"{int(tb['minutes']):,}")
    html += stat_row("Pass Accuracy %", ta["pass_accuracy"], tb["pass_accuracy"])
    html += stat_row("Tackles", int(ta["tackles"]), int(tb["tackles"]))
    html += stat_row("Interceptions", int(ta["interceptions"]), int(tb["interceptions"]))
    html += stat_row("Avg Distance (km)", ta["avg_distance_km"], tb["avg_distance_km"])
    html += stat_row("Top Speed (km/h)", ta["top_speed"], tb["top_speed"])
    html += stat_row("Yellow Cards", int(ta["yellow_cards"]), int(tb["yellow_cards"]), higher_is_better=False)
    html += stat_row("Red Cards", int(ta["red_cards"]), int(tb["red_cards"]), higher_is_better=False)
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # Radar chart
    st.markdown("### Radar Comparison")
    categories = ["Goals", "Assists", "Avg Rating", "Pass Acc %", "Tackles", "Interceptions"]

    def normalise(val, max_val):
        return round((float(val) / max_val) * 10, 2) if max_val > 0 else 0

    max_goals = max(float(ta["goals"]), float(tb["goals"]), 1)
    max_assists = max(float(ta["assists"]), float(tb["assists"]), 1)
    max_rating = 10
    max_pass = 100
    max_tackles = max(float(ta["tackles"]), float(tb["tackles"]), 1)
    max_intercept = max(float(ta["interceptions"]), float(tb["interceptions"]), 1)

    vals_a = [
        normalise(ta["goals"], max_goals),
        normalise(ta["assists"], max_assists),
        normalise(ta["avg_rating"], max_rating),
        normalise(ta["pass_accuracy"], max_pass),
        normalise(ta["tackles"], max_tackles),
        normalise(ta["interceptions"], max_intercept),
    ]
    vals_b = [
        normalise(tb["goals"], max_goals),
        normalise(tb["assists"], max_assists),
        normalise(tb["avg_rating"], max_rating),
        normalise(tb["pass_accuracy"], max_pass),
        normalise(tb["tackles"], max_tackles),
        normalise(tb["interceptions"], max_intercept),
    ]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals_a + [vals_a[0]], theta=categories + [categories[0]],
        fill="toself", name=player_a,
        line=dict(color=COLORS["gold"]), fillcolor="rgba(240,192,64,0.15)"
    ))
    fig.add_trace(go.Scatterpolar(
        r=vals_b + [vals_b[0]], theta=categories + [categories[0]],
        fill="toself", name=player_b,
        line=dict(color=COLORS["blue"]), fillcolor="rgba(26,110,181,0.15)"
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(
            bgcolor="#0f1e36",
            radialaxis=dict(visible=True, range=[0, 10], gridcolor="#1e2d4a", color=COLORS["muted"]),
            angularaxis=dict(gridcolor="#1e2d4a", color=COLORS["text"]),
        ),
        legend=dict(font=dict(color=COLORS["text"])),
        height=480,
    )
    st.plotly_chart(fig, use_container_width=True)

# ── MATCH RESULTS ────────────────────────────────────────────────────────────
elif page == "Match Results":
    st.markdown("## Match Results")

    stages = ["All"] + query("SELECT DISTINCT tournament_stage FROM player_stats ORDER BY tournament_stage")["tournament_stage"].tolist()

    col1, col2 = st.columns([1, 3])
    with col1:
        stage = st.selectbox("Tournament Stage", stages)

    if stage == "All":
        df = query("SELECT * FROM match_results ORDER BY match_date")
    else:
        df = query("SELECT * FROM match_results WHERE tournament_stage = ? ORDER BY match_date", [stage])

    result_color = {"W": "#27ae60", "D": "#f39c12", "L": "#c0392b"}

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("### Results Breakdown")
    result_counts = df["match_result"].value_counts().reset_index()
    result_counts.columns = ["result", "count"]
    fig = px.pie(
        result_counts, names="result", values="count", hole=0.4,
        color="result",
        color_discrete_map={"W": COLORS["gold"], "D": COLORS["blue"], "L": "#c0392b"},
    )
    fig.update_layout(**PLOTLY_LAYOUT, height=320, legend=dict(font=dict(color=COLORS["text"])))
    fig.update_traces(textfont_color="white")
    st.plotly_chart(fig, use_container_width=True)
