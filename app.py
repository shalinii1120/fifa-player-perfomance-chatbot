
import streamlit as st
import pandas as pd
import os
import ollama

# Page configuration
st.set_page_config(
    page_title="FIFA Player Performance Chatbot",
    page_icon="⚽",
    layout="wide"
)

# Load dataset
DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "FIFA_CLEANED_DATASET.csv"
)

df = pd.read_csv(DATA_PATH)

# Website heading
st.title("⚽ FIFA Player Performance Chatbot")
st.caption("Explore FIFA player profiles and performance information")

st.divider()

# Player profile columns
profile_columns = [
    "player_id", "player_name", "age", "nationality",
    "team", "jersey_number", "position", "height_cm",
    "weight_kg", "preferred_foot", "club_name",
    "market_value_eur"
]

# Player search
st.subheader("🔎 Search FIFA Players")

player_names = sorted(df["player_name"].dropna().unique())

selected_player = st.selectbox(
    "Select a player",
    player_names
)

# Display player profile
player_data = df[df["player_name"] == selected_player]
player = player_data.iloc[0]

st.subheader("👤 Player Profile")

col1, col2 = st.columns(2)

for index, column in enumerate(profile_columns):
    if column in df.columns and pd.notna(player[column]):
        label = column.replace("_", " ").title()

        if index % 2 == 0:
            col1.metric(label, str(player[column]))
        else:
            col2.metric(label, str(player[column]))

st.divider()

# Chatbot
st.subheader("💬 Ask the FIFA Chatbot")

question = st.text_input(
    "Ask a question about a player",
    placeholder="Example: What is the age of Rodri Fati?"
)



# -------- ADVANCED FIFA ANALYTICS --------

def get_player_totals():

    # Create one tournament-level record per player
    if "player_id" in df.columns:

        if "total_goals_tournament" in df.columns:
            stats = df.drop_duplicates(
                subset=["player_id"]
            ).copy()

        else:
            stats = df.groupby(
                ["player_id", "player_name"],
                as_index=False
            ).agg({
                "goals": "sum",
                "assists": "sum",
                "minutes_played": "sum",
                "player_rating": "mean"
            })

    else:
        stats = df.copy()

    return stats


def advanced_fifa_answer(question):

    q = question.lower()
    stats = get_player_totals()

    # Find player names mentioned in the question
    names = [
        name for name in player_names
        if name.lower() in q
    ]

    # 1. COMPARE TWO PLAYERS
    if "compare" in q and len(names) >= 2:

        a = stats[stats["player_name"] == names[0]].iloc[0]
        b = stats[stats["player_name"] == names[1]].iloc[0]

        metrics = [
            ("Goals", "total_goals_tournament", "goals"),
            ("Assists", "total_assists_tournament", "assists"),
            ("Rating", "tournament_rating", "player_rating")
        ]

        answer = f"### ⚔️ {names[0]} vs {names[1]}\n\n"

        for label, primary, fallback in metrics:
            column = primary if primary in stats.columns else fallback

            if column in stats.columns:
                answer += (
                    f"- **{label}:** "
                    f"{names[0]}: {a[column]} | "
                    f"{names[1]}: {b[column]}\n"
                )

        return answer

    # 2. BEST GOALKEEPER
    if "goalkeeper" in q or "best keeper" in q:

        keepers = stats[
            stats["position"].astype(str).str.contains(
                "goalkeeper", case=False, na=False
            )
        ].copy()

        if keepers.empty:
            return "No goalkeeper records were found."

        if "save_percentage" in keepers.columns:
            metric = "save_percentage"
            keepers[metric] = pd.to_numeric(
                keepers[metric], errors="coerce"
            )
            keepers = keepers.dropna(subset=[metric])
            keepers = keepers.sort_values(metric, ascending=False)

        elif "saves" in keepers.columns:
            metric = "saves"
            keepers[metric] = pd.to_numeric(
                keepers[metric], errors="coerce"
            )
            keepers = keepers.sort_values(metric, ascending=False)

        else:
            return "Goalkeeper statistics are unavailable."

        best = keepers.iloc[0]

        return (
            f"🧤 Best goalkeeper by {metric.replace('_', ' ')}: "
            f"**{best['player_name']}** "
            f"({best[metric]:.2f})."
        )

    # 3. HIGHEST-RATED PLAYER
    if "highest rated" in q or "best rated" in q:

        metric = (
            "tournament_rating"
            if "tournament_rating" in stats.columns
            else "player_rating"
        )

        if metric not in stats.columns:
            return "Player rating is unavailable."

        stats[metric] = pd.to_numeric(
            stats[metric], errors="coerce"
        )

        best = stats.dropna(subset=[metric]).sort_values(
            metric, ascending=False
        ).iloc[0]

        return (
            f"⭐ Highest-rated player: **{best['player_name']}** "
            f"with a rating of {best[metric]:.2f}."
        )

    # 4. COMPARE TWO TEAMS
    if "compare" in q and ("team" in q or "country" in q):

        teams = [
            str(team) for team in df["team"].dropna().unique()
            if str(team).lower() in q
        ]

        if len(teams) < 2:
            return "Please mention two team names to compare."

        match_data = df.drop_duplicates(
            subset=["match_id", "team"]
        ).copy()

        answer = "### 🏆 Team Comparison\n\n"

        for team in teams[:2]:
            records = match_data[
                match_data["team"] == team
            ]

            wins = (
                records["match_result"].astype(str).str.upper() == "W"
            ).sum()

            draws = (
                records["match_result"].astype(str).str.upper() == "D"
            ).sum()

            losses = (
                records["match_result"].astype(str).str.upper() == "L"
            ).sum()

            answer += (
                f"**{team}**\n"
                f"- Matches: {len(records)}\n"
                f"- Wins: {wins}\n"
                f"- Draws: {draws}\n"
                f"- Losses: {losses}\n\n"
            )

        return answer

    # 5. INDIVIDUAL PLAYER PERFORMANCE
    if names and any(word in q for word in [
        "performance", "statistics", "stats", "analyze", "analysis"
    ]):

        name = names[0]
        records = df[df["player_name"] == name]

        answer = f"### 📊 Performance Analysis: {name}\n\n"

        metrics = [
            "goals", "assists", "minutes_played",
            "shots", "tackles", "interceptions",
            "player_rating", "performance_score"
        ]

        for metric in metrics:
            if metric in records.columns:
                values = pd.to_numeric(
                    records[metric], errors="coerce"
                ).dropna()

                if not values.empty:
                    if metric in [
                        "player_rating", "performance_score"
                    ]:
                        value = values.mean()
                    else:
                        value = values.sum()

                    answer += (
                        f"- **{metric.replace('_', ' ').title()}:** "
                        f"{value:.2f}\n"
                    )

        return answer

    return None

# -------- OLLAMA CONNECTION --------

def get_ollama_client():

    # Check for hosted API key in Streamlit Cloud
    try:
        api_key = st.secrets.get("OLLAMA_API_KEY", "")
    except Exception:
        api_key = ""

    # Also allow an environment variable for local testing
    api_key = api_key or os.getenv("OLLAMA_API_KEY", "")

    if api_key:
        client = ollama.Client(
            host="https://ollama.com",
            headers={
                "Authorization": f"Bearer {api_key}"
            }
        )
        model_name = "gemma4:31b"

    else:
        # Use your local Ollama installation
        client = ollama.Client(
            host="http://localhost:11434"
        )
        model_name = "llama3.2:3b"

    return client, model_name

# -------- OLLAMA AI INTEGRATION --------

def is_football_related(question):
    prompt = f"""
    Decide whether this question is related to FIFA,
    football, soccer, football players, clubs, teams,
    tournaments, rules, tactics or football history.

    Reply with ONLY YES or NO.

    Question: {question}
    """

    try:
        client, model_name = get_ollama_client()

        response = client.chat(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You classify questions. Reply only YES or NO."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={"temperature": 0}
        )

        result = response["message"]["content"].strip().upper()
        return result.startswith("YES")

    except Exception as e:
        print("Ollama classification error:", e)
        return None


def generate_football_answer(question):

    try:
        client, model_name = get_ollama_client()

        response = client.chat(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are FIFA Club AI, a football knowledge assistant.

                    Answer only questions about FIFA, football and soccer.

                    Explain football rules, tactics, formations,
                    tournaments, clubs and general football knowledge.

                    Never invent exact player statistics or claim
                    that information came from the project's dataset.

                    If asked for information that requires current
                    statistics, clearly mention that you cannot
                    verify live information.
                    """
                },
                {"role": "user", "content": question}
            ]
        )

        return response["message"]["content"]

    except Exception:
        return (
            "Sorry! I couldn't connect to the Ollama AI model. "
            "Please check whether Ollama is running."
        )

def answer_question(question):

    # Convert question to lowercase
    q = question.lower().strip()

    # Check advanced FIFA questions
    advanced_answer = advanced_fifa_answer(question)

    if advanced_answer is not None:
        return advanced_answer

    # 1. GREETINGS
    greetings = {
        "hi": "Hi! Welcome to FIFA Club ⚽ How can I help you explore football today?",
        "hello": "Hello! ⚽ Welcome to FIFA Club. Ask me anything about FIFA players and performances!",
        "hey": "Hey there! Welcome to FIFA Club. What would you like to know about football?",
        "good morning": "Good morning! ⚽ Welcome to FIFA Club. Let's explore football!",
        "good afternoon": "Good afternoon! Welcome to FIFA Club ⚽",
        "good evening": "Good evening! Ready to explore FIFA statistics? ⚽",
        "thanks": "You're welcome! Keep enjoying football ⚽",
        "thank you": "My pleasure! Let me know if you have another FIFA question.",
        "bye": "Goodbye! Thanks for visiting FIFA Club. See you again! ⚽"
    }

    if q in greetings:
        return greetings[q]

    # 2. FIND PLAYER NAME
    matched_players = [
        name for name in player_names
        if name.lower() in q
    ]

    player_name = matched_players[0] if matched_players else None

    # 3. IDENTIFY STATISTICS REQUESTED
    stat_mapping = {
        "goals": {
            "keywords": ["goal", "goals", "scored", "score", "scorer"],
            "column": "total_goals_tournament",
            "fallback": "goals",
            "aggregation": "sum"
        },
        "assists": {
            "keywords": ["assist", "assists"],
            "column": "total_assists_tournament",
            "fallback": "assists",
            "aggregation": "sum"
        },
        "minutes played": {
            "keywords": ["minutes", "playing time"],
            "column": "total_minutes_tournament",
            "fallback": "minutes_played",
            "aggregation": "sum"
        },
        "shots": {
            "keywords": ["shots", "shooting"],
            "column": "shots",
            "fallback": "shots",
            "aggregation": "sum"
        },
        "saves": {
            "keywords": ["saves", "save"],
            "column": "saves",
            "fallback": "saves",
            "aggregation": "sum"
        },
        "tackles": {
            "keywords": ["tackle", "tackles"],
            "column": "tackles",
            "fallback": "tackles",
            "aggregation": "sum"
        },
        "rating": {
            "keywords": ["rating", "rated"],
            "column": "tournament_rating",
            "fallback": "player_rating",
            "aggregation": "mean"
        },
        "pass accuracy": {
            "keywords": ["pass accuracy", "passing accuracy"],
            "column": "pass_accuracy",
            "fallback": "pass_accuracy",
            "aggregation": "mean"
        }
    }

    selected_stat = None

    # Check longer phrases first
    for stat, details in sorted(
        stat_mapping.items(),
        key=lambda item: max(len(k) for k in item[1]["keywords"]),
        reverse=True
    ):
        if any(keyword in q for keyword in details["keywords"]):
            selected_stat = stat
            break

    # 4. PLAYER-SPECIFIC QUESTIONS
    if player_name:

        player_records = df[
            df["player_name"] == player_name
        ]

        if selected_stat:

            details = stat_mapping[selected_stat]

            # Prefer tournament total when available
            column = details["column"]

            if column not in df.columns:
                column = details["fallback"]

            if column not in df.columns:
                return "Sorry, this statistic is not available in my dataset."

            values = pd.to_numeric(
                player_records[column],
                errors="coerce"
            ).dropna()

            if values.empty:
                return "This statistic is not available for this player."

            if column in [
                "total_goals_tournament",
                "total_assists_tournament",
                "total_minutes_tournament",
                "tournament_rating"
            ]:
                result = values.iloc[0]

            elif details["aggregation"] == "sum":
                result = values.sum()

            else:
                result = values.mean()

            return (
                f"⚽ {player_name} has {result:g} "
                f"{selected_stat} according to the dataset."
            )

        # Profile only when explicitly requested
        if any(word in q for word in [
            "profile", "details", "information", "about"
        ]):
            record = player_records.iloc[0]

            fields = [
                "age", "nationality", "team", "position",
                "club_name", "jersey_number"
            ]

            answer = f"Player information: {player_name}\n\n"

            for field in fields:
                if field in df.columns and pd.notna(record[field]):
                    answer += (
                        f"{field.replace('_', ' ').title()}: "
                        f"{record[field]}\n"
                    )

            return answer

        return (
            f"I found {player_name} in the dataset! "
            "What would you like to know: goals, assists, "
            "age, nationality, position or performance?"
        )

    # 5. GENERAL FIFA QUESTIONS: STATISTICS AND RANKINGS

    if selected_stat:

        details = stat_mapping[selected_stat]
        column = details["column"]

        if column not in df.columns:
            column = details["fallback"]

        if column not in df.columns:
            return "Sorry, this statistic is not available in my dataset."

        # Prepare player-wise statistics
        if column in [
            "total_goals_tournament",
            "total_assists_tournament",
            "total_minutes_tournament",
            "tournament_rating"
        ]:
            player_stats = df[
                ["player_id", "player_name", column]
            ].drop_duplicates(subset=["player_id"]).copy()

            player_stats[column] = pd.to_numeric(
                player_stats[column], errors="coerce"
            )

        else:
            player_stats = df.groupby(
                ["player_id", "player_name"],
                as_index=False
            )[column].agg(details["aggregation"])

        player_stats = player_stats.dropna(subset=[column])

        if player_stats.empty:
            return "No statistics found in the dataset."

        # Understand what the user is asking
        lowest_words = [
            "least", "minimum", "lowest", "fewest",
            "smallest", "minimum number"
        ]

        highest_words = [
            "most", "maximum", "highest", "top",
            "best", "more", "leading"
        ]

        average_words = [
            "average", "avg", "mean"
        ]

        total_words = [
            "total", "overall"
        ]

        # LOWEST PERFORMER
        if any(word in q for word in lowest_words):

            result = player_stats.sort_values(
                column, ascending=True
            ).iloc[0]

            return (
                f"📉 The player with the fewest {selected_stat} "
                f"in the dataset is {result['player_name']} "
                f"with {result[column]:g}."
            )

        # AVERAGE
        elif any(word in q for word in average_words):

            average_value = player_stats[column].mean()

            return (
                f"📊 The average {selected_stat} per player "
                f"in the dataset is {average_value:.2f}."
            )

        # TOTAL ACROSS ALL PLAYERS
        elif any(word in q for word in total_words):

            total_value = player_stats[column].sum()

            return (
                f"📊 The total {selected_stat} across all "
                f"players in the dataset is {total_value:g}."
            )

        # HIGHEST PERFORMER (DEFAULT)
        else:

            result = player_stats.sort_values(
                column, ascending=False
            ).iloc[0]

            return (
                f"🏆 The player with the most {selected_stat} "
                f"in the dataset is {result['player_name']} "
                f"with {result[column]:g}."
            )
    # 6. TEAM-RELATED QUESTIONS
    if "team" in q or "country" in q:

        teams = sorted(df["team"].dropna().unique())

        return (
            "I can answer questions about teams in the dataset. "
            "Available teams include: "
            + ", ".join(map(str, teams[:15]))
        )

    # 7. OLLAMA FALLBACK FOR QUESTIONS NOT ANSWERED BY DATASET

    football_related = is_football_related(question)

    # Ollama connection problem
    if football_related is None:
        return (
            "Sorry! I couldn't connect to my AI assistant. "
            "Please make sure Ollama is running."
        )

    # Football-related question: generate an answer using Ollama
    if football_related:
        return generate_football_answer(question)

    # Unrelated question
    return (
        "Sorry! This question is not related to FIFA or football ⚽ "
        "Please visit https://chatgpt.com/ for assistance. "
        "I'm here to help with FIFA players, football knowledge "
        "and performance statistics!"
    )


if question:
    st.markdown("### 🤖 Chatbot Response")
    st.markdown(answer_question(question))

st.divider()

st.caption("FIFA Player Performance Chatbot | Academic Project")
