import pandas as pd


def prepare_initial_df() -> pd.DataFrame:
    df_2324 = pd.read_csv('https://www.football-data.co.uk/mmz4281/2324/F1.csv')
    df_2425 = pd.read_csv('https://www.football-data.co.uk/mmz4281/2425/F1.csv')

    df_2324.loc[df_2324["HomeTeam"] == "Metz", "HomeTeam"] = "Auxerre"
    df_2324.loc[df_2324["AwayTeam"] == "Metz", "AwayTeam"] = "Auxerre"
    df_2324.loc[df_2324["HomeTeam"] == "Lorient", "HomeTeam"] = "Angers"
    df_2324.loc[df_2324["AwayTeam"] == "Lorient", "AwayTeam"] = "Angers"
    df_2324.loc[df_2324["HomeTeam"] == "Clermont", "HomeTeam"] = "St Etienne"
    df_2324.loc[df_2324["AwayTeam"] == "Clermont", "AwayTeam"] = "St Etienne"

    df = pd.concat([df_2324, df_2425])

    return df


def prepare_home_statistics(df: pd.DataFrame) -> pd.DataFrame:
    
    team_names = df.HomeTeam.unique().tolist()
    total_nb_matches = len(df)
    total_goals_score_home_team = df['FTHG'].sum()
    total_goals_score_away_team = df['FTAG'].sum()
    average_goals_score_home_team = total_goals_score_home_team / total_nb_matches
    average_goals_score_away_team = total_goals_score_away_team / total_nb_matches
    nb_home_matches_per_team = df["HomeTeam"].value_counts()

    home_statistics = pd.DataFrame()
    home_statistics["MPH"] = nb_home_matches_per_team
    home_statistics["GSH"] = df[["HomeTeam", "FTHG"]].groupby("HomeTeam").sum()
    home_statistics["GCH"] = df[["HomeTeam", "FTAG"]].groupby("HomeTeam").sum()
    home_statistics["AGSH"] = 0.0
    home_statistics["AGCH"] = 0.0

    for home_team in team_names:
        home_statistics.loc[home_team, "AGSH"] = home_statistics.loc[home_team, "GSH"] / nb_home_matches_per_team[home_team]
        home_statistics.loc[home_team, "AGCH"] = home_statistics.loc[home_team, "GCH"] / nb_home_matches_per_team[home_team]

    home_statistics["HAFS"] = home_statistics["AGSH"] / average_goals_score_home_team
    home_statistics["HDFS"] = home_statistics["AGCH"] / average_goals_score_away_team

    home_statistics.index.names = ["Team name"]

    return home_statistics


def prepare_away_statistics(df: pd.DataFrame) -> pd.DataFrame:
    
    team_names = df.HomeTeam.unique().tolist()
    total_nb_matches = len(df)
    total_goals_score_home_team = df['FTHG'].sum()
    total_goals_score_away_team = df['FTAG'].sum()
    average_goals_score_home_team = total_goals_score_home_team / total_nb_matches
    average_goals_score_away_team = total_goals_score_away_team / total_nb_matches
    nb_away_matches_per_team = df["AwayTeam"].value_counts()

    away_statistics = pd.DataFrame()
    away_statistics["MPA"] = nb_away_matches_per_team
    away_statistics["GSA"] = df[["AwayTeam", "FTAG"]].groupby("AwayTeam").sum()
    away_statistics["GCA"] = df[["AwayTeam", "FTHG"]].groupby("AwayTeam").sum()
    away_statistics["AGSA"] = 0.0
    away_statistics["AGCA"] = 0.0

    for home_team in team_names:
        away_statistics.loc[home_team, "AGSA"] = away_statistics.loc[home_team, "GSA"] / nb_away_matches_per_team[home_team]
        away_statistics.loc[home_team, "AGCA"] = away_statistics.loc[home_team, "GCA"] / nb_away_matches_per_team[home_team]

    away_statistics["AAFS"] = away_statistics["AGSA"] / average_goals_score_away_team
    away_statistics["ADFS"] = away_statistics["AGCA"] / average_goals_score_home_team

    away_statistics.index.names = ["Team name"]

    return away_statistics