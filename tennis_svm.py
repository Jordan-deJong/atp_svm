import numpy as np
from sklearn import preprocessing, model_selection, neighbors, svm
import pandas as pd
import math
import datetime
from dateutil.relativedelta import relativedelta

def date_in_rolling_period(date):
    date = datetime.datetime.strptime(date, '%Y.%m.%d')
    if date >= (datetime.datetime.now()-relativedelta(months=+rolling_monthly_period)):
        return(True)

def clean_age_weight_height(row):
    clean_row = str(row).replace('(','')
    clean_row = clean_row.replace(')','')
    clean_row = clean_row.replace('cm','')
    clean_row = clean_row.replace('kg','')
    clean_row = clean_row.replace(' ','')
    return(clean_row)

def normalization_age_weight_height(df):
    normalization = {}
    distribution_lists = {'age': [], 'weight': [], 'height': []}
    distribution_columns = ['opp1_age', 'opp1_weight', 'opp1_height', 'opp2_age', 'opp2_weight', 'opp2_height']
    for column in distribution_columns:
        players_id = []
        i = 0
        for row in df[column]:
            try:
                if df[column[:4]][i] not in players_id:
                    clean_row = clean_age_weight_height(row)
                    distribution_lists[column.replace('opp1_', '').replace('opp2_', '')].append(int(clean_row.split('.')[0]))
                    players_id.append(df[column[:4]][i])
            except:
                pass
            i += 1
    for column in distribution_columns:
        normalization[column] = [np.mean(distribution_lists[column.replace('opp1_', '').replace('opp2_', '')]), np.std(distribution_lists[column.replace('opp1_', '').replace('opp2_', '')])]
    print("Age Weight Hieght Normalized")
    return(normalization)

def get_player_dict(df):
    players_dict = {}
    for column in ['opp1', 'opp2']:
        for row in df[column]:
            if row not in players_dict:
                players_dict[row] = {}
    return(players_dict)

def normalization_overall_winloss(df):
    players_dict = get_player_dict(df)
    for player in players_dict:
        players_dict[player] = [0, 0, 0]
    for i in range(len(df.index)):
        if date_in_rolling_period(df['date'][i]):
            opp1 = df['opp1'][i]
            opp2 = df['opp2'][i]
            if df['winner'][i] == 1:
                players_dict[opp1][0] += 1
                players_dict[opp2][1] += 1
            else:
                players_dict[opp1][1] += 1
                players_dict[opp2][0] += 1
            players_dict[opp1][2] += 1
            players_dict[opp2][2] += 1
    normalization = {'overall': players_dict}
    print("Overall WinLoss Normalized")
    return(normalization)

def normalization_title_location(df):
    normalization = {}
    for column in ['title', 'location']:
        players_dict = get_player_dict(df)
        i = 0
        for row in df[column]:
            for opp_num in [1, 2]:
                opp = df['opp'+str(opp_num)][i]
                if row not in players_dict[opp]:
                    players_dict[opp][row] = [0, 0, 0]  # Win, Loss, Sum
                if df['winner'][i] == opp_num:
                    players_dict[opp][row][0] += 1
                else:
                    players_dict[opp][row][1] += 1
                players_dict[opp][row][2] += 1
            i += 1
        normalization[column] = players_dict
    print("Title & Location Normalized")
    return(normalization)

def normalization_opps(df):
    players_dict = get_player_dict(df)
    for i in range(len(df.index)):
        opp1 = df['opp1'][i]
        opp2 = df['opp2'][i]
        if opp2 not in players_dict[opp1]:
            players_dict[opp1][opp2] = [0, 0, 0]  # Win, Loss, Sum
        if opp1 not in players_dict[opp2]:
            players_dict[opp2][opp1] = [0, 0, 0]  # Win, Loss, Sum
        if df['winner'][i] == 1:
            players_dict[opp1][opp2][0] += 1
            players_dict[opp2][opp1][1] += 1
        else:
            players_dict[opp2][opp1][0] += 1
            players_dict[opp1][opp2][1] += 1
        players_dict[opp1][opp2][2] += 1
        players_dict[opp2][opp1][2] += 1
    normalization = {'opp': players_dict}
    print("Opps Normalized")
    return(normalization)

def normalization_surface_and_surface_type(df):
    normalization = {}
    players_dict = get_player_dict(df)
    for surfaces in ['surface', 'surfaceType']:
        for i in range(len(df.index)):
            if date_in_rolling_period(df['date'][i]):
                opp1 = df['opp1'][i]
                opp2 = df['opp2'][i]
                surface = str(df[surfaces][i]).lower()
                if surface not in players_dict[opp1]:
                    players_dict[opp1][surface] = [0, 0, 0]
                if surface not in players_dict[opp2]:
                    players_dict[opp2][surface] = [0, 0, 0]
                if df['winner'][i] == 1:
                    players_dict[opp1][surface][0] += 1
                    players_dict[opp2][surface][1] += 1
                else:
                    players_dict[opp2][surface][0] += 1
                    players_dict[opp1][surface][1] += 1
                players_dict[opp1][surface][2] += 1
                players_dict[opp2][surface][2] += 1
        normalization[surfaces] = players_dict
    print("surfaces Normalized")
    return(normalization)

def normalization_hand(df):
    players_dict = get_player_dict(df)
    for player in players_dict:
        players_dict[player] = {'Right-Handed': [0, 0, 0], 'Left-Handed': [0, 0, 0], 'nan': [0, 0, 0]}
    for i in range(len(df.index)):
        if date_in_rolling_period(df['date'][i]):
            opp1 = df['opp1'][i]
            opp1_hand = str(df['opp1_hand'][i]).split(",")[0]
            opp2 = df['opp2'][i]
            opp2_hand = str(df['opp2_hand'][i]).split(",")[0]
            if df['winner'][i] == 1:
                players_dict[opp1][opp2_hand][0] += 1
                players_dict[opp2][opp1_hand][1] += 1
            else:
                players_dict[opp1][opp2_hand][1] += 1
                players_dict[opp2][opp1_hand][0] += 1
            players_dict[opp1][opp2_hand][2] += 1
            players_dict[opp2][opp1_hand][2] += 1
    normalization = {'hand': players_dict}
    print("Hands Normalized")
    return(normalization)

def normalization_sets(df):
    players_dict = get_player_dict(df)
    for player in players_dict:
        for set_num in ["1","2","3","4","5"]:
            players_dict[player]["set" + set_num] = [0, 0, 0]
    for i in range(len(df.index)):
        opp1 = df['opp1'][i]
        opp2 = df['opp2'][i]
        for set_num in ['1','2','3','4','5']:
            if df['opp1_set' + set_num][i] > df['opp2_set' + set_num][i]:
                players_dict[opp1]['set'+set_num][0] += 1
                players_dict[opp2]['set'+set_num][1] += 1
            else:
                players_dict[opp1]['set'+set_num][1] += 1
                players_dict[opp2]['set'+set_num][0] += 1
            players_dict[opp1]['set'+set_num][2] += 1
            players_dict[opp2]['set'+set_num][2] += 1
    normalization = {'set': players_dict}
    print("Sets Normalized")
    return(normalization)

def normalization_set_avg(df):
    players_dict = get_player_dict(df)
    for player in players_dict:
        for set_num in ["1","2","3","4","5"]:
            players_dict[player]["set" + set_num] = []
    for i in range(len(df.index)):
        opp1 = df['opp1'][i]
        opp2 = df['opp2'][i]
        for set_num in ['1','2','3','4','5']:
            players_dict[opp1]["set" + set_num].append(int(df['opp1_set' + set_num][i]))
            players_dict[opp2]["set" + set_num].append(int(df['opp2_set' + set_num][i]))
    normalization = {'set_avg': players_dict}
    return(normalization)

def normalization(df):
    normalizations = {**normalization_overall_winloss(df), **normalization_age_weight_height(df), **normalization_title_location(df), **normalization_opps(df),
                      **normalization_surface_and_surface_type(df), **normalization_hand(df), **normalization_sets(df), **normalization_set_avg(df)}
    print("Normalization Complete")
    return(normalizations)

def apply_winloss_columns(df, print_status):
    winloss_columns = ['opp1_overall_ytd', 'opp1_grandslams_ytd', 'opp1_atpworld_ytd', 'opp1_tiebreaks_ytd', 'opp1_vs_top_10_ytd', 'opp1_finals_ytd', 'opp1_deciding_set_ytd', 'opp1_fifth_set_record_ytd', 'opp1_clay_ytd', 'opp1_grass_ytd', 'opp1_hard_ytd', 'opp1_carpet_ytd', 'opp1_indoor_ytd', 'opp1_outdoor_ytd', 'opp1_after_winning_first_set_ytd', 'opp1_after_losing_first_set_ytd', 'opp1_vs_right_handers_ytd', 'opp1_vs_left_handers_ytd',
                       'opp1_overall_career', 'opp1_grandslams_career', 'opp1_atpworld_career', 'opp1_tiebreaks_career', 'opp1_vs_top_10_career', 'opp1_finals_career', 'opp1_deciding_set_career', 'opp1_fifth_set_record_career', 'opp1_clay_career', 'opp1_grass_career', 'opp1_hard_career', 'opp1_carpet_career', 'opp1_indoor_career', 'opp1_outdoor_career', 'opp1_after_winning_first_set_career', 'opp1_after_losing_first_set_career', 'opp1_vs_right_handers_career', 'opp1_vs_left_handers_career',
                       'opp2_overall_ytd', 'opp2_grandslams_ytd', 'opp2_atpworld_ytd', 'opp2_tiebreaks_ytd', 'opp2_vs_top_10_ytd', 'opp2_finals_ytd', 'opp2_deciding_set_ytd', 'opp2_fifth_set_record_ytd', 'opp2_clay_ytd', 'opp2_grass_ytd', 'opp2_hard_ytd', 'opp2_carpet_ytd', 'opp2_indoor_ytd', 'opp2_outdoor_ytd', 'opp2_after_winning_first_set_ytd', 'opp2_after_losing_first_set_ytd', 'opp2_vs_right_handers_ytd', 'opp2_vs_left_handers_ytd',
                       'opp2_overall_career', 'opp2_grandslams_career', 'opp2_atpworld_career', 'opp2_tiebreaks_career', 'opp2_vs_top_10_career', 'opp2_finals_career', 'opp2_deciding_set_career', 'opp2_fifth_set_record_career', 'opp2_clay_career', 'opp2_grass_career', 'opp2_hard_career', 'opp2_carpet_career', 'opp2_indoor_career', 'opp2_outdoor_career', 'opp2_after_winning_first_set_career', 'opp2_after_losing_first_set_career', 'opp2_vs_right_handers_career', 'opp2_vs_left_handers_career']
    for column in winloss_columns:
        i = 0
        for row in df[column]:
            df.loc[i, column] = round(row*10)
            i += 1
    if print_status: print("Win Loss Applied")

def apply_overall(df, normalization, print_status):
    import collections
    names = []
    for i in range(len(df.index)):
        try:
            opp1 = df['opp1'][i]
            opp1_norm = normalization['overall'][opp1]
            opp1_rate = round((opp1_norm[0]/opp1_norm[2])*10)
            if opp1_rate == 0: ValueError("Can't be zero")
            if opp1_rate != df['opp1_overall_ytd'][i]: names.append(opp1)
            opp2 = df['opp2'][i]
            opp2_norm = normalization['overall'][opp2]
            opp2_rate = round((opp2_norm[0]/opp2_norm[2])*10)
            if opp2_rate == 0: ValueError("Can't be zero")
        except:
            opp1_rate = df['opp1_overall_career'][i]
            opp2_rate = df['opp2_overall_career'][i]
        df['opp1_overall_wl_rolling'] = opp1_rate
        df['opp2_overall_wl_rolling'] = opp2_rate
    print(len(collections.Counter(names)))
    if print_status: print("Overall Applied")

def apply_surface(df, normalization, print_status):
    for column in ['surface', 'surfaceType']:
        i = 0
        for row in df[column]:
            row = str(row)
            try:
                opp1 = df['opp1'][i]
                opp1_norm = normalization[column][opp1][row.lower()]
                opp1_rate = round((opp1_norm[0]/opp1_norm[2])*10)
                if opp1_rate == 0: opp1_rate = df['opp1_' + row.lower() + '_career'][i]
                opp2 = df['opp2'][i]
                opp2_norm = normalization[column][opp2][row.lower()]
                opp2_rate = round((opp2_norm[0]/opp2_norm[2])*10)
                if opp2_rate == 0: opp2_rate = df['opp2_' + row.lower() + '_career'][i]
            except:
                opp1_rate =  df['opp1_overall_career'][i]
                opp2_rate =  df['opp2_overall_career'][i]
            df.loc[i, 'opp1_' + column + '_winloss'] =  opp1_rate
            df.loc[i, 'opp2_' + column + '_winloss'] =  opp2_rate
            i += 1
    if print_status: print("Surface Applied")

def apply_dollars(df, print_status):
    amounts = []
    i = 0
    for row in df['dollar']:
        clean_row = str(row).replace('$','')
        clean_row = clean_row.replace(',','')
        clean_row = clean_row.replace('A','')
        try:
            clean_row = int(clean_row)
        except:
            clean_row = 0
        df.loc[i, 'dollar'] = clean_row
        amounts.append(clean_row)
        i += 1

    i = 0
    for row in df['dollar']:
        df.loc[i, 'dollar'] = math.ceil(row/max(amounts)*10)
        i += 1
    if print_status: print("Dollars Applied")

def apply_rankings(df, print_status):
    ranking_weight = {(1, 5): 10, (6, 20): 9, (21, 50): 8, (51, 100): 7, (101, 150): 6, (151, 200): 5, (201, 300): 4, (301, 400): 3, (401, 500): 2, (501, 10000): 1}
    for column in ['opp1_rank', 'opp2_rank']:
        i = 0
        for row in df[column]:
            for k, v in ranking_weight.items():
                if row >= k[0] and row <= k[1]:
                    df.loc[i, column] = v
                else:
                    df.loc[i, column] = 1
            i += 1
    if print_status: print("Rankings Applied")

def apply_percent_columns(df, print_status):
    percent_columns = ['opp1_first_serve', 'opp1_first_serve_points_won', 'opp1_second_serve_points_won', 'opp1_break_points_saved', 'opp1_service_points_won', 'opp1_total_service_points_won', 'opp1_first_serve_return_points_won', 'opp1_second_serve_return_points_won', 'opp1_break_points_converted', 'opp1_return_games_won', 'opp1_return_points_won', 'opp1_total_points_won',
                       'opp2_first_serve', 'opp2_first_serve_points_won', 'opp2_second_serve_points_won', 'opp2_break_points_saved', 'opp2_service_points_won', 'opp2_total_service_points_won', 'opp2_first_serve_return_points_won', 'opp2_second_serve_return_points_won', 'opp2_break_points_converted', 'opp2_return_games_won', 'opp2_return_points_won', 'opp2_total_points_won']
    for column in percent_columns:
        i = 0
        for row in df[column]:
            df.loc[i, column] = round(int(row.replace('%',''))/10)
            i += 1
    if print_status: print("Percentage Columns Applied")

def apply_title_location(df, normalization, print_status):
    for column in ['title', 'location']:
        for i in range(len(df.index)):
            for opp_ref in ['opp1', 'opp2']:
                try:
                    opp_stats = normalization[column][df[opp_ref][i]][df[column][i]]
                    opp_win_rate = ((opp_stats[0]/opp_stats[2])*10)
                except:
                    opp_win_rate = df["opp1_overall_ytd"][i]
                df.loc[i, opp_ref + '_' + column + '_win_rate'] = int(opp_win_rate)
    if print_status: print("Title & Location Applied")

def apply_opps(df, normalization, print_status):
    for i in range(len(df.index)):
        opp1 = df['opp1'][i]
        opp2 = df['opp2'][i]
        opp1_stats = normalization['opp'][opp1][opp2]
        opp2_stats = normalization['opp'][opp2][opp1]
        opp1_win_rate = ((opp1_stats[0]/opp1_stats[2])*10)
        opp2_win_rate = ((opp2_stats[0]/opp2_stats[2])*10)
        df.loc[i, 'opp1_vs_opp2_win_rate'] = int(opp1_win_rate)
        df.loc[i, 'opp2_vs_opp1_win_rate'] = int(opp2_win_rate)
    if print_status: print("Opps Win Rate Applied")

def apply_sets(df, normalization, print_status):
    for i in range(len(df.index)):
        for opp_ref in ['opp1', 'opp2']:
            opp = df[opp_ref][i]
            for set_num in ["1","2","3","4","5"]:
                opp_stats = normalization['set'][opp]['set'+set_num]
                opp_set_win_rate = ((opp_stats[0]/opp_stats[2])*10)
                df.loc[i, opp_ref + '_set' + set_num + '_win_rate'] = int(opp_set_win_rate)
    if print_status: print("Sets Win Rate Applied")

def apply_first_set_winner(df, print_status):
    for i in range(len(df.index)):
        if df['opp1_set1'][i] > df['opp2_set1'][i]:
            df.loc[i, 'first_set_winner'] = 1
        else:
            df.loc[i, 'first_set_winner'] = 2
    if print_status: print("First Set Winner Applied")

def apply_age_weight_height(df, normalization, print_status):
    for column in ['opp1_age', 'opp1_weight', 'opp1_height', 'opp2_age', 'opp2_weight', 'opp2_height']:
        i = 0
        for row in df[column]:
            clean_row = clean_age_weight_height(row)
            if clean_row == '':
                clean_row = normalization[column][0]
            else:
                clean_row = int(clean_row.split('.')[0])
            column_norm = math.ceil(abs((clean_row - normalization[column][0])/normalization[column][1]))
            if column_norm > 10:
                column_norm = 10
            df.loc[i, column] = abs(column_norm-11)
            i += 1
    if print_status: print("Age Weight Height Applied")

def apply_year_pro(df, print_status):
    for column in ['opp1_year_pro', 'opp2_year_pro']:
        i = 0
        for row in df[column]:
            try:
                date = datetime.datetime.strptime(str(row), '%Y')
                years_pro = datetime.datetime.now().year - date.year
            except:
                years_pro = abs(df[column.replace('year_pro', 'age')][i] - 18)
            if years_pro > 10:
                years_pro = 10
            df.loc[i, column] = math.ceil(years_pro)
            i += 1
    if print_status: print("Year Pro Applied")

def apply_hand(df, normalization, print_status):
    hand_ref = {'Right-Handed': 'right_handers', 'Left-Handed': 'left_handers'}
    for i in range(len(df.index)):
        try:
            opp1 = df['opp1'][i]
            opp2 = df['opp2'][i]
            opp1_norm = normalization['hand'][opp1][df['opp2_hand'][i].split(',')[0]]
            opp2_norm = normalization['hand'][opp2][df['opp1_hand'][i].split(',')[0]]
            opp1_rate = round((opp1_norm[0]/opp1_norm[2])*10)
            opp2_rate = round((opp2_norm[0]/opp2_norm[2])*10)
        # opp1_rate = df["opp1_vs_" + hand_ref[df['opp2_hand'][i].split(',')[0]] + "_ytd"][i]
        # opp2_rate = df["opp2_vs_" + hand_ref[df['opp1_hand'][i].split(',')[0]] + "_ytd"][i]
        except:
            opp1_rate = df["opp1_overall_career"][i]
            opp2_rate = df["opp2_overall_career"][i]
        df.loc[i, "opp1_vs_opp2_hand"] = opp1_rate
        df.loc[i, "opp2_vs_opp1_hand"] = opp2_rate
    if print_status: print("Hand Win Rate Applied")

def apply_normalization(df, normalization, print_status):
    apply_winloss_columns(df, print_status)
    apply_overall(df, normalization, print_status)
    apply_surface(df, normalization, print_status)
    apply_dollars(df, print_status)
    apply_rankings(df, print_status)
    apply_percent_columns(df, print_status)
    # apply_title_location(df, normalization, print_status)
    apply_opps(df, normalization, print_status)
    apply_sets(df, normalization, print_status)
    apply_first_set_winner(df, print_status)
    apply_age_weight_height(df, normalization, print_status)
    apply_year_pro(df, print_status)
    apply_hand(df, normalization, print_status)
    df.drop(['date', 'title', 'location', 'surface', 'surfaceType', 'opp1_url', 'opp2_url',
            'opp1_set1', 'opp2_set1', 'opp1_set2', 'opp2_set2', 'opp1_set3', 'opp2_set3', 'opp1_set4', 'opp2_set4', 'opp1_set5', 'opp2_set5',
            'opp1_clay_ytd', 'opp1_grass_ytd', 'opp1_hard_ytd', 'opp1_carpet_ytd', 'opp1_indoor_ytd', 'opp1_outdoor_ytd',
            'opp1_clay_career', 'opp1_grass_career', 'opp1_hard_career', 'opp1_carpet_career', 'opp1_indoor_career', 'opp1_outdoor_career',
            'opp1_hand', 'opp1_vs_right_handers_ytd', 'opp1_vs_left_handers_ytd', 'opp1_vs_right_handers_career', 'opp1_vs_left_handers_career',
            'opp2_clay_ytd', 'opp2_grass_ytd', 'opp2_hard_ytd', 'opp2_carpet_ytd', 'opp2_indoor_ytd', 'opp2_outdoor_ytd',
            'opp2_clay_career', 'opp2_grass_career', 'opp2_hard_career', 'opp2_carpet_career', 'opp2_indoor_career', 'opp2_outdoor_career',
            'opp2_hand', 'opp2_vs_right_handers_ytd', 'opp2_vs_left_handers_ytd', 'opp2_vs_right_handers_career', 'opp2_vs_left_handers_career'
            ], 1, inplace=True)
    if print_status: print("Apply normalization Complete")
    return(df)

def train_winner(df):
    X = np.array(df.drop(['winner', 'opp1', 'opp2', 'first_set_winner'], 1))
    y = np.array(df['winner'])
    # X = preprocessing.scale(X)

    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.2) #, random_state=42)

    clf = svm.SVC(probability=True)

    clf.fit(X_train, y_train)
    accuracy = clf.score(X_test, y_test)
    accuracy = str(round(accuracy*100)) + '%'
    return(clf, accuracy)

def predict_winner(norm, clf, accuracy):
    p_df = pd.read_csv('c:/Users/jdejong/dropbox/python/tennis/tennis_data_prediction.csv', encoding = 'iso-8859-1')
    norm_p_df = apply_normalization(p_df, norm, False)
    matches = np.array(norm_p_df.drop(['opp1', 'opp2', 'winner', 'first_set_winner'], 1))
    opp1s = np.array(norm_p_df['opp1'])
    opp2s = np.array(norm_p_df['opp2'])
    # matches = preprocessing.scale(matches)

    winnerslist = []
    print("\n" + accuracy + " Accurate Winner Predictions:")
    i = 0
    for row in matches:
        row = row.reshape(1, -1)
        prediction = clf.predict(row)
        confidence = clf.decision_function(row)
        probability = clf.predict_proba(row)
        winnerslist.append([opp1s[i], opp2s[i], eval('opp' + str(prediction[0]) +'s[i]'), int(abs(probability[0][prediction[0]-1])*100), int(abs(confidence[0])*100)])
        print(opp1s[i] + " vs " + opp2s[i] + " " + str(norm['opp'][opp1s[i]][opp2s[i]]) + " - " + str(prediction[0]) + " - " + str(int(abs(probability[0][prediction[0]-1])*100))
              + '% probability - ' + str(int(abs(confidence[0])*100)) + ' Distance')
        i += 1
    print(winnerslist)

def train_set1_winner(df):
    X = np.array(df.drop(['winner', 'opp1', 'opp2', 'first_set_winner'], 1))
    y = np.array(df['first_set_winner'])
    # X = preprocessing.scale(X)

    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.2) #, random_state=42)

    clf = svm.SVC(probability=True)

    clf.fit(X_train, y_train)
    accuracy = clf.score(X_test, y_test)
    accuracy = str(round(accuracy*100)) + '%'
    print(accuracy)
    return(clf, accuracy)

def predict_set1_winner(norm, clf, accuracy):
    p_df = pd.read_csv('c:/Users/jdejong/dropbox/python/tennis/tennis_data_prediction.csv', encoding = 'iso-8859-1')
    norm_p_df = apply_normalization(p_df, norm, False)
    matches = np.array(norm_p_df.drop(['opp1', 'opp2', 'winner', 'first_set_winner'], 1))
    opp1s = np.array(norm_p_df['opp1'])
    opp2s = np.array(norm_p_df['opp2'])
    # matches = preprocessing.scale(matches)

    print("\n" + accuracy + " Accurate 1st Set Predictions:")
    i = 0
    for row in matches:
        row = row.reshape(1, -1)
        prediction = int(clf.predict(row)[0])
        confidence = clf.decision_function(row)
        probability = clf.predict_proba(row)
        print(opp1s[i] + " vs " + opp2s[i] + " - " + str(prediction) + " - " + str(int(abs(probability[0][prediction-1])*100)) + '% prob - ' + str(int(abs(confidence[0])*100)) + ' Dist'
        ' - 1s ' + str(int((norm['set'][opp1s[i]]['set1'][0]/norm['set'][opp1s[i]]['set1'][2])*100)) + "%(" + str(int(np.mean(norm['set_avg'][opp1s[i]]['set1']))) + ")"
        + " vs " + str(int((norm['set'][opp2s[i]]['set1'][0]/norm['set'][opp2s[i]]['set1'][2])*100)) + "%(" + str(int(np.mean(norm['set_avg'][opp2s[i]]['set1']))) + ")")
        i += 1

rolling_monthly_period = 12
df = pd.read_csv('c:/Users/jdejong/dropbox/python/tennis/tennis_data.csv', encoding = 'iso-8859-1')
norm = normalization(df)

# norm_df = apply_normalization(df, norm, True)
# norm_df.copy().to_csv('c:/Users/jdejong/dropbox/python/tennis/normalized_df.csv', sep=',', index=False)
norm_df = pd.read_csv('c:/Users/jdejong/dropbox/python/tennis/normalized_df.csv', encoding='utf-8')

winner_clf, accuracy = train_winner(norm_df)
predict_winner(norm, winner_clf, accuracy)

set1_winner_clf, accuracy = train_set1_winner(norm_df)
predict_set1_winner(norm, set1_winner_clf, accuracy)
