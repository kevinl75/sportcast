import pandas as pd

def color_max(df):
    max_val = df.max().max()
    return df.map(lambda v: 'background-color: green' if v == max_val else '')


def style_best_team_df_part(df:pd.DataFrame, df_part:str):
   
    if df_part not in ["upper", "lower", "diag"]:
        raise ValueError("The argument must be one of 'upper', 'lower', or 'diag'.")
    
    df_styled = pd.DataFrame('', index=df.index, columns=df.columns)
    
    # Apply the style to the upper half of the DataFrame
    for i in range(len(df)):
        if df_part == "upper":
            if i != 0:
                df_styled.iloc[i-1, i:] = 'background-color: #e6ffe6; color: black'
        elif df_part == "lower":
            if i != 0:
                df_styled.iloc[i:, i-1] = 'background-color: #e6ffe6; color:black'
        elif df_part == "diag":
            df_styled.iloc[i, i] = 'background-color: #e6ffe6; color: black'
    
    return df_styled
