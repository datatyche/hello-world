import pandas as pd

# Train data
ball_by_ball = pd.read_csv("D:/Arunsankar/My Knowledge Base/Analytics Vidhya/IPL/train/ball_by_ball_data.csv")
key_teams = pd.read_csv("D:/Arunsankar/My Knowledge Base/Analytics Vidhya/IPL/train/key_teams.csv")
match_data = pd.read_csv("D:/Arunsankar/My Knowledge Base/Analytics Vidhya/IPL/train/match_data.csv")
player_rosters = pd.read_csv("D:/Arunsankar/My Knowledge Base/Analytics Vidhya/IPL/train/player_rosters.csv")

# Test data
player_predictions = pd.read_csv("D:/Arunsankar/My Knowledge Base/Analytics Vidhya/IPL/test/player_predictions.csv")
matches_2018 = pd.read_csv("D:/Arunsankar/My Knowledge Base/Analytics Vidhya/IPL/test/matches_2018.csv")
total_extras = pd.read_csv("D:/Arunsankar/My Knowledge Base/Analytics Vidhya/IPL/test/total_extras.csv")


# Prediction of playing XI

# Test Data preparation
df_test = pd.merge(player_predictions,
                   matches_2018,
                   how='left',
                   on='match_id')

df_test.drop(['runs_scored_bat_first', 'wickets_taken_bowl_first', 'runs_scored_bat_second', 'wickets_taken_bowl_second', 'unique_id', 'venue'],
             axis=1,
             inplace=True)

df_test['season'] = 2018

# Training Data preparation
df_train = pd.DataFrame(columns=['match_id', 'season', 'team_id', 'date', 'team1_id', 'team2_id', 'venue_id'])

for match in match_data['match_id'].unique():
    temp = match_data[match_data['match_id']==match][['match_id', 'season', 'date', 'team1_id', 'team2_id', 'venue_id']]

    temp['team_id'] = match_data[match_data['match_id']==match]['team1_id']
    df_train = df_train.append(temp)

    temp['team_id'] = match_data[match_data['match_id']==match]['team2_id']
    df_train = df_train.append(temp)
    
df_train = df_train.groupby(['season', 'team_id']).apply(lambda x: pd.merge(x, player_rosters, left_on=['season', 'team_id'], right_on=['Season', 'Team'], how='left')).reset_index(level = (0,1), drop = True)

df_train.drop(['Player', 'Season', 'Team'],
             axis=1,
             inplace=True)

df_temp1 = ball_by_ball.groupby(['match_id', 'batting_team', 'batsman_id'], as_index=False)['ball'].count().reset_index()
df_temp1.drop(['index', 'ball'], axis=1, inplace=True)
df_temp1.rename(columns={'match_id': 'match_id', 'batting_team': 'team_id', 'batsman_id':'player_id'}, inplace=True)

df_temp2 = ball_by_ball.groupby(['match_id', 'batting_team', 'non_striker_id'], as_index=False)['ball'].count().reset_index()
df_temp2.drop(['index', 'ball'], axis=1, inplace=True)
df_temp2.rename(columns={'match_id': 'match_id', 'batting_team': 'team_id', 'non_striker_id':'player_id'}, inplace=True)

df_temp3 = ball_by_ball.groupby(['match_id', 'bowling_team', 'bowler_id'], as_index=False)['ball'].count().reset_index()
df_temp3.drop(['index', 'ball'], axis=1, inplace=True)
df_temp3.rename(columns={'match_id': 'match_id', 'bowling_team': 'team_id', 'bowler_id':'player_id'}, inplace=True)

df_temp = pd.concat([df_temp1, df_temp2, df_temp3]).drop_duplicates().reset_index(drop=True)

df_temp['playing_xi_flag'] = 1

df_train = pd.merge(df_train,
                    df_temp,
                    how='left',
                    on=['match_id', 'team_id', 'player_id'])

df_train.fillna(value=0,
               inplace=True)

df_train.to_csv("D:/Arunsankar/My Knowledge Base/Analytics Vidhya/IPL/train_playing_eleven.csv", index=False)
df_test.to_csv("D:/Arunsankar/My Knowledge Base/Analytics Vidhya/IPL/test_playing_eleven.csv", index=False)