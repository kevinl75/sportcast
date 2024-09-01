import pandas as pd
import streamlit as st
from scipy.stats import poisson

from utils import style_best_team_df_part, color_max
from preprocess import prepare_initial_df, prepare_home_statistics, prepare_away_statistics

st.title('Football Prediction')

# From these data.
df = prepare_initial_df()
total_nb_matches = len(df)
total_goals_score_home_team = df['FTHG'].sum()
total_goals_score_away_team = df['FTAG'].sum()
average_goals_score_home_team = total_goals_score_home_team / total_nb_matches
average_goals_score_away_team = total_goals_score_away_team / total_nb_matches

st.markdown("### Initial Data")
st.markdown("""This is the dataframe we use to realise our prediction.

All the statistics computed and used on this page come from here.""")
st.dataframe(df)

team_names = df.HomeTeam.unique().tolist()


team_home_statistics = prepare_home_statistics(df)
team_away_statistics = prepare_away_statistics(df)

st.markdown("# Attack and defense potential per team")

st.markdown("## At home")
st.markdown("""### Caption to read this table
- MPH: nb of matchs played at home
- GSH: total goals scored at home
- GCH: total goals conceded at home
- AGSH: average number of goals scored at home
- AGCH: average number of goals conceded at home
- HAFS: home attack force score (the highest the better)
- HDFS: home defense force score (the lowest the better)""")
st.dataframe(team_home_statistics)
st.markdown("Note that if a team has a HAFS score higher than its HDFS score, then the team is more comfortable at home.")

st.markdown("## Away")
st.markdown("""### Caption to read this table
- MPA: nb of matchs played away
- GSA: total goals scored away
- GCA: total goals conceded away
- AGSA: average number of goals scored away
- AGCA: average number of goals conceded away
- AAFS: away attack force score (the highest the better)
- ADFS: away defense force score (the lowest the better)""")
st.dataframe(team_away_statistics)
st.markdown("Note that if a team has a AAFS score higher than its ADFS score, then the team is more comfortable at home.")


match_probability_dict = {}

for home_team in team_names:
    for away_team in team_names:
        if away_team!= home_team:
            prediction_goal_home_team = team_home_statistics.loc[home_team, "HAFS"] * team_away_statistics.loc[away_team, "ADFS"] * average_goals_score_home_team
            prediction_goal_away_team = team_home_statistics.loc[home_team, "HDFS"] * team_away_statistics.loc[away_team, "AAFS"] * average_goals_score_away_team
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
