import pandas as pd
import streamlit as st
from scipy.stats import poisson

from utils import style_best_team_df_part, color_max

st.title('Football Prediction')

# From these data.
df = pd.read_csv('https://www.football-data.co.uk/mmz4281/2324/F1.csv')

st.markdown("## Initial Data")
st.dataframe(df)

team_names = df.HomeTeam.unique().tolist()
nb_of_matches = len(df['HomeTeam'])

nb_home_goal = df['FTHG'].sum() / nb_of_matches
nb_away_goal = df['FTAG'].sum() / nb_of_matches

st.write()

# NB goals scored at home per team
attack_force_home = df[["HomeTeam", "FTHG"]].groupby("HomeTeam").sum()
attack_force_home["AHG"] = attack_force_home["FTHG"] / 19
attack_force_home["AttackForceHome"] = attack_force_home["AHG"] / nb_home_goal

# NB goals conceded away per team
defense_force_away = df[["AwayTeam", "FTHG"]].groupby("AwayTeam").sum()
defense_force_away["AHGC"] = defense_force_away["FTHG"] / 19
defense_force_away["DefenseForceAway"] = defense_force_away["AHGC"] / nb_home_goal

# NB goals scored at home per team
defense_force_home = df[["HomeTeam", "FTAG"]].groupby("HomeTeam").sum()
defense_force_home["AAGC"] = defense_force_home["FTAG"] / 19
defense_force_home["DefenseForceHome"] = defense_force_home["AAGC"] / nb_away_goal

# NB goals scored at home per team
attack_force_away = df[["AwayTeam", "FTAG"]].groupby("AwayTeam").sum()
attack_force_away["AAG"] = attack_force_away["FTAG"] / 19
attack_force_away["AttackForceAway"] = attack_force_away["AAG"] / nb_away_goal

st.markdown("## Attack and defense Home Team statistics:")
st.dataframe(attack_force_home.merge(defense_force_home, how="inner", on="HomeTeam"))
st.markdown("## Attack and defense Away Team statistics:")
st.dataframe(attack_force_away.merge(defense_force_away, how="inner", on="AwayTeam"))

match_probability_dict = {}

for home_team in team_names:
    for away_team in team_names:
        if away_team!= home_team:
            prediction_goal_home_team = attack_force_home.loc[home_team, "AttackForceHome"] * defense_force_away.loc[away_team, "DefenseForceAway"] * nb_home_goal
            prediction_goal_away_team = defense_force_home.loc[home_team, "DefenseForceHome"] * attack_force_away.loc[away_team, "AttackForceAway"] * nb_away_goal
            match_probability_dict[f"{home_team} vs {away_team}"] = [prediction_goal_home_team, prediction_goal_away_team]

match_probability_df = pd.DataFrame.from_dict(match_probability_dict, orient='index')

st.write("# Choose your matchup:")

home_team_options = st.selectbox(
    "Home team choice:",
    team_names,
    index=None
)

away_team_options = st.selectbox(
    "Away team choice:",
    team_names,
    index=None
)

if away_team_options and home_team_options:

    df_key = f"{home_team_options} vs {away_team_options}"

    st.markdown("## Some Statistics about your matchup")
    st.dataframe(match_probability_df.loc[df_key])

    lambda_param_home = match_probability_df.loc[df_key, 0]
    lambda_param_away = match_probability_df.loc[df_key, 1]

    expected_goal = [i for i in range(0, 6)]
    home_team_goal_probs = poisson.pmf(expected_goal, mu=lambda_param_home)
    away_team_goal_probs = poisson.pmf(expected_goal, mu=lambda_param_away)

    st.write("### Goal expectations probability for each team:")
    st.dataframe(pd.DataFrame(data={
        home_team_options:home_team_goal_probs,
        away_team_options:away_team_goal_probs
    }))

    exact_score_probs_dict = {}

    home_sum_prob = 0
    away_sum_prob = 0
    draw_sum_prob = 0

    st.write("### Score matrix probability:")
    for index_h, home_prob in enumerate(home_team_goal_probs.tolist()):
        home_goal_dict = {}
        for index_a, away_prob in enumerate(away_team_goal_probs.tolist()):
            exact_score_prob = home_prob * away_prob * 100
            home_goal_dict[f"{away_team_options} {index_a}"] = exact_score_prob
            if index_h == index_a:
                draw_sum_prob += exact_score_prob
            elif index_h > index_a:
                home_sum_prob += exact_score_prob
            elif index_h < index_a:
                away_sum_prob += exact_score_prob

        exact_score_probs_dict[f"{home_team_options} {index_h}"] = home_goal_dict

    exact_score_probs_df = pd.DataFrame.from_dict(exact_score_probs_dict)

    df_part = ""
    if draw_sum_prob > home_sum_prob and draw_sum_prob > away_sum_prob:
        df_part = "diag"
    elif home_sum_prob > draw_sum_prob and home_sum_prob > away_sum_prob:
        df_part = "upper"
    elif away_sum_prob > draw_sum_prob and away_sum_prob > home_sum_prob:
        df_part = "lower"
    
    exact_score_probs_df = exact_score_probs_df.style.apply(
        style_best_team_df_part, df_part=df_part, axis=None
    ).apply(color_max, axis=None)

    st.dataframe(exact_score_probs_df)

    st.write("Want to add some odds?")

    col1, col2, col3 = st.columns(3)
    with col1:
        home_team_odd = st.number_input("Home team win odd:", min_value=0, max_value=500)

    with col2:
        draw_odd = st.number_input("Draw odd:", min_value=0, max_value=500)

    with col3:
        away_team_odd = st.number_input("Away team win odd:", min_value=0, max_value=500)

    if home_team_odd and draw_odd and away_team_odd:

        exact_score_odds_weighted_probs_dict = {}

        home_sum_prob_odds = 0
        away_sum_prob_odds = 0
        draw_sum_prob_odds = 0

        st.write("### Score matrix probability weighted with the odds:")
        for index_h, home_prob in enumerate(home_team_goal_probs.tolist()):
            home_goal_dict = {}
            for index_a, away_prob in enumerate(away_team_goal_probs.tolist()):
                exact_score_prob_odds = 0
                if index_a > index_h:
                    exact_score_prob_odds = home_prob * away_prob * away_team_odd
                    home_goal_dict[f"{away_team_options} {index_a}"] = exact_score_prob_odds
                    away_sum_prob_odds += exact_score_prob_odds
                elif index_a == index_h:
                    exact_score_prob_odds = home_prob * away_prob * draw_odd
                    home_goal_dict[f"{away_team_options} {index_a}"] = exact_score_prob_odds
                    draw_sum_prob_odds += exact_score_prob_odds
                elif index_h > index_a:
                    exact_score_prob_odds = home_prob * away_prob * home_team_odd
                    home_goal_dict[f"{away_team_options} {index_a}"] = exact_score_prob_odds
                    home_sum_prob_odds += exact_score_prob_odds

            exact_score_odds_weighted_probs_dict[f"{home_team_options} {index_h}"] = home_goal_dict
        
        exact_score_odds_weighted_probs_df = pd.DataFrame.from_dict(exact_score_odds_weighted_probs_dict)
        
        df_part = ""
        if draw_sum_prob_odds > home_sum_prob_odds and draw_sum_prob_odds > away_sum_prob_odds:
            df_part = "diag"
        elif home_sum_prob_odds > draw_sum_prob_odds and home_sum_prob_odds > away_sum_prob_odds:
            df_part = "upper"
        elif away_sum_prob_odds > draw_sum_prob_odds and away_sum_prob_odds > home_sum_prob_odds:
            df_part = "lower"
        
        exact_score_odds_weighted_probs_df = exact_score_odds_weighted_probs_df.style.apply(
            style_best_team_df_part, df_part=df_part, axis=None
        ).apply(color_max, axis=None)
        
        st.dataframe(exact_score_odds_weighted_probs_df)
