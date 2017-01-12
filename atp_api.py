import urllib.request
from lxml import etree
import io
from bs4 import BeautifulSoup
from random import randint
import re
import multiprocessing
import time
import csv
import datetime

def strip_html(raw_html):
    return BeautifulSoup(raw_html, 'lxml').get_text().strip()

def process_tournament_data(tree):
    url = tree.xpath("//table[@class='results-archive-table mega-table']/tbody/tr/td[8]/a/@href")
    details = tree.xpath("//table[@class='results-archive-table mega-table']/tbody/tr/td[3]/span/text()")
    surfaceIOs = tree.xpath("//table[@class='results-archive-table mega-table']/tbody/tr/td[5]/div/div/text()")
    surfaceTypes = tree.xpath("//table[@class='results-archive-table mega-table']/tbody/tr/td[5]/div/div/span/text()")
    dollars = tree.xpath("//table[@class='results-archive-table mega-table']/tbody/tr/td[6]/div/div/span/text()")
    tournaments = []
    index = 0
    for i in range(len(url)):
        title = strip_html(details[0+index])
        location = strip_html(details[1+index])
        date = strip_html(details[2+index])
        surface = strip_html(surfaceIOs[i])
        surfaceType = strip_html(surfaceTypes[i])
        dollar = strip_html(dollars[i].encode('ascii', 'ignore'))
        tournaments.append([date, title, location, surface, surfaceType, dollar, url[i]])
        index += 3
    return(tournaments)

def process_match_data(tree):
    winner = tree.xpath("//table[@class='day-table']/tbody/tr/td[3]/a/text()")
    winner_link = tree.xpath("//table[@class='day-table']/tbody/tr/td[3]/a/@href")
    loser = tree.xpath("//table[@class='day-table']/tbody/tr/td[7]/a/text()")
    loser_link = tree.xpath("//table[@class='day-table']/tbody/tr/td[7]/a/@href")
    scores = tree.xpath("//table[@class='day-table']/tbody/tr/td[8]/a")
    match_link = tree.xpath("//table[@class='day-table']/tbody/tr/td[8]/a/@href")
    matches = []
    for i in range(len(winner)):
        try:
            matches.append([winner[i], winner_link[i], loser[i], loser_link[i], etree.tostring(scores[i]), match_link[i]])
        except:
            pass
    return(matches)

def match_stats_player_table_location(tree, player_name, list_string):
    first_name = strip_html(tree.xpath("//div[@class='player-left-name']/a/span[1]/text()")[0])
    last_name = strip_html(tree.xpath("//div[@class='player-left-name']/a/span[2]/text()")[0])
    full_name = first_name + last_name
    if full_name.replace(' ', '') == player_name.replace(' ', ''):
        i = 1
    else:
        i = list_string.find('opponentStats')
    return(i)

def find_in_string(list_string, substring, i):
    s_count = list_string.find(substring, i) + len(substring) + 3
    s_result = list_string[s_count:(s_count+2)].replace(',','')
    return(s_result)

def process_match_stat_data(tree, player_name):
    list_string = strip_html(etree.tostring(tree.xpath("//script[@id='matchStatsData']")[0]))
    i = match_stats_player_table_location(tree, player_name, list_string)
    aces = find_in_string(list_string, 'Aces', i)
    double_faults = find_in_string(list_string,'DoubleFaults', i)
    first_serve_perentage = find_in_string(list_string, 'FirstServePercentage', i)
    first_serve_points_won = find_in_string(list_string, 'FirstServePointsWonPercentage', i)
    second_serve_points_won = find_in_string(list_string, 'SecondServePointsWonPercentage', i)
    break_points_saved = find_in_string(list_string, 'BreakPointsSavedPercentage', i)
    service_games_played = find_in_string(list_string, 'ServiceGamesPlayed', i)
    first_serve_return_points_won = find_in_string(list_string, 'FirstServeReturnPointsPercentage', i)
    second_serve_return_points_won = find_in_string(list_string, 'SecondServePointsPercentage', i)
    break_points_converted = find_in_string(list_string, 'BreakPointsConvertedPercentage', i)
    return_games_played = find_in_string(list_string, 'ReturnGamesPlayed', i)
    total_service_points_won = find_in_string(list_string, 'TotalServicePointsWonPercentage', i)
    total_return_points_won = find_in_string(list_string, 'TotalReturnPointsWonPercentage', i)
    total_points_won = find_in_string(list_string, 'TotalPointsWonPercentage', i)
    return([aces, double_faults, first_serve_perentage, first_serve_points_won, second_serve_points_won, break_points_saved, service_games_played, first_serve_return_points_won,
            second_serve_return_points_won, break_points_converted, return_games_played, total_service_points_won, total_return_points_won, total_points_won])

def process_player_overview(tree):
    rank = strip_html(tree.xpath("//div[@class='player-ranking-position']/div[2]/text()")[0])
    age = strip_html(tree.xpath("//div[@class='player-profile-hero-table']/div/table/tr[1]/td[1]/div/div[2]/text()")[0])
    year_pro = strip_html(tree.xpath("//div[@class='player-profile-hero-table']/div/table/tr[1]/td[2]/div/div[2]/text()")[0])
    weight = strip_html(tree.xpath("//div[@class='player-profile-hero-table']/div/table/tr[1]/td[3]/div/div[2]/span[2]/text()")[0])
    height = strip_html(tree.xpath("//div[@class='player-profile-hero-table']/div/table/tr[1]/td[4]/div/div[2]/span[2]/text()")[0])
    hand = strip_html(tree.xpath("//div[@class='player-profile-hero-table']/div/table/tr[2]/td[3]/div/div[2]/text()")[0])
    return([rank, age, year_pro, weight, height, hand])

def process_player_statistics(tree):
    first_serve = strip_html(tree.xpath("//table[@class='mega-table'][1]/tbody/tr[3]/td[2]/text()")[0])
    first_serve_points_won = strip_html(tree.xpath("//table[@class='mega-table'][1]/tbody/tr[4]/td[2]/text()")[0])
    second_serve_points_won = strip_html(tree.xpath("//table[@class='mega-table'][1]/tbody/tr[5]/td[2]/text()")[0])
    break_points_saved = strip_html(tree.xpath("//table[@class='mega-table'][1]/tbody/tr[7]/td[2]/text()")[0])
    service_points_won = strip_html(tree.xpath("//table[@class='mega-table'][1]/tbody/tr[9]/td[2]/text()")[0])
    total_service_points_won = strip_html(tree.xpath("//table[@class='mega-table'][1]/tbody/tr[10]/td[2]/text()")[0])
    first_serve_return_points_won = strip_html(tree.xpath("//table[@class='mega-table'][2]/tbody/tr[1]/td[2]/text()")[0])
    second_serve_return_points_won = strip_html(tree.xpath("//table[@class='mega-table'][2]/tbody/tr[2]/td[2]/text()")[0])
    break_points_converted = strip_html(tree.xpath("//table[@class='mega-table'][2]/tbody/tr[4]/td[2]/text()")[0])
    return_games_won = strip_html(tree.xpath("//table[@class='mega-table'][2]/tbody/tr[6]/td[2]/text()")[0])
    return_points_won = strip_html(tree.xpath("//table[@class='mega-table'][2]/tbody/tr[7]/td[2]/text()")[0])
    total_points_won = strip_html(tree.xpath("//table[@class='mega-table'][2]/tbody/tr[8]/td[2]/text()")[0])
    return([first_serve, first_serve_points_won, second_serve_points_won, break_points_saved, service_points_won, total_service_points_won,
            first_serve_return_points_won, second_serve_return_points_won, break_points_converted, return_games_won, return_points_won, total_points_won])

def process_player_winloss(tree, loc):
    overall = strip_html(tree.xpath("//table[@class='mega-table'][1]/tbody/tr[1]/td[" + loc + "]/text()")[0])
    grandslams = strip_html(tree.xpath("//table[@class='mega-table'][1]/tbody/tr[2]/td[" + loc + "]/text()")[0])
    atpworld = strip_html(tree.xpath("//table[@class='mega-table'][1]/tbody/tr[3]/td[" + loc + "]/text()")[0])
    tiebreaks = strip_html(tree.xpath("//table[@class='mega-table'][2]/tbody/tr[1]/td[" + loc + "]/text()")[0])
    vs_top_10 = strip_html(tree.xpath("//table[@class='mega-table'][2]/tbody/tr[2]/td[" + loc + "]/text()")[0])
    finals = strip_html(tree.xpath("//table[@class='mega-table'][2]/tbody/tr[3]/td[" + loc + "]/text()")[0])
    deciding_set = strip_html(tree.xpath("//table[@class='mega-table'][2]/tbody/tr[4]/td[" + loc + "]/text()")[0])
    fifth_set_record = strip_html(tree.xpath("//table[@class='mega-table'][2]/tbody/tr[5]/td[" + loc + "]/text()")[0])
    clay = strip_html(tree.xpath("//table[@class='mega-table'][3]/tbody/tr[1]/td[" + loc + "]/text()")[0])
    grass = strip_html(tree.xpath("//table[@class='mega-table'][3]/tbody/tr[2]/td[" + loc + "]/text()")[0])
    hard = strip_html(tree.xpath("//table[@class='mega-table'][3]/tbody/tr[3]/td[" + loc + "]/text()")[0])
    carpet = strip_html(tree.xpath("//table[@class='mega-table'][3]/tbody/tr[4]/td[" + loc + "]/text()")[0])
    indoor = strip_html(tree.xpath("//table[@class='mega-table'][3]/tbody/tr[5]/td[" + loc + "]/text()")[0])
    outdoor = strip_html(tree.xpath("//table[@class='mega-table'][3]/tbody/tr[6]/td[" + loc + "]/text()")[0])
    after_winning_first_set = strip_html(tree.xpath("//table[@class='mega-table'][4]/tbody/tr[1]/td[" + loc + "]/text()")[0])
    after_losing_first_set = strip_html(tree.xpath("//table[@class='mega-table'][4]/tbody/tr[2]/td[" + loc + "]/text()")[0])
    vs_right_handers = strip_html(tree.xpath("//table[@class='mega-table'][4]/tbody/tr[3]/td[" + loc + "]/text()")[0])
    vs_left_handers = strip_html(tree.xpath("//table[@class='mega-table'][4]/tbody/tr[4]/td[" + loc + "]/text()")[0])
    return([overall, grandslams, atpworld, tiebreaks, vs_top_10, finals, deciding_set, fifth_set_record, clay, grass, hard, carpet, indoor, outdoor,
            after_winning_first_set, after_losing_first_set, vs_right_handers, vs_left_handers])

def get_year_data():
    year_data = []
    for year in years:
        url = home_url + '/en/scores/results-archive?year=' + str(year)
        result = urllib.request.urlopen(url)
        html = result.read()
        parser = etree.HTMLParser()
        tree = etree.parse(io.BytesIO(html), parser)
        year_data.extend(process_tournament_data(tree))
    print("Years Complete")
    return(year_data)

def get_set_scores(scores):
    score = re.sub(r"<sup>\d+</sup>", "", bytes.decode(scores))
    score = score.replace('(W/O)', '').replace('(RET)', '').replace(" ","")
    score = strip_html(str.encode(score))
    score_list = list(score)
    if len(score_list) == 12:
        score_list[8] = score_list[8] + score_list[9]
        score_list[9] = score_list[10] + score_list[11]
        score_list = score_list[:10]
    if len(score_list) == 11:
        if int(score_list[8] + score_list[9]) < 10:
            score_list[9] = score_list[9] + score_list[10]
        else:
            score_list[8] = score_list[8] + score_list[9]
        score_list = score_list[:10]
    score_list += ['0'] * (10 - len(score_list))
    return(score_list)

def randomize_players(tournament, match):
    random = randint(1,2)
    if random == 1:
        opp1 = match[0]
        opp1_url = match[1]
        opp2 = match[2]
        opp2_url = match[3]
        w1, l1, w2, l2, w3, l3, w4, l4, w5, l5 = get_set_scores(match[4])
        winner = 1
    else:
        opp1 = match[2]
        opp1_url = match[3]
        opp2 = match[0]
        opp2_url = match[1]
        l1, w1, l2, w2, l3, w3, l4, w4, l5, w5 = get_set_scores(match[4])
        winner = 2
    return(tournament[:6] + [opp1, opp1_url, opp2, opp2_url, winner, w1, l1, w2, l2, w3, l3, w4, l4, w5, l5, match[5]])

def threaded_get_tournament(tournament):
    match_data = []
    attempts = 0
    while attempts < 3:
        try:
            url = home_url + tournament[6]
            result = urllib.request.urlopen(url)
            html = result.read()
            parser = etree.HTMLParser()
            tree = etree.parse(io.BytesIO(html), parser)
            matches = process_match_data(tree)
            for match in matches:
                match_data.append(randomize_players(tournament, match))
            print(tournament[0] + " " + tournament[1] + " process complete.")
            attempts = 3
            return(match_data)
        except Exception as e:
            attempts += 1
            print(tournament[0] + " " + tournament[1] +" process failed  -" + str(e))
            if attempts == 3: return([])
            time.sleep(2)


def get_tournament_data(year_data):
    tournament_data = []
    mp_pool = multiprocessing.Pool(processes=len(year_data))
    tournament_data.extend(mp_pool.map(threaded_get_tournament, (tournament for tournament in year_data)))
    mp_pool.close()
    print("Tournaments Complete")
    return([match for matches in tournament_data for match in matches])

def get_match_stats(link, opp1_name, opp2_name):
    url = home_url + link
    result = urllib.request.urlopen(url)
    html = result.read()
    parser = etree.HTMLParser()
    tree = etree.parse(io.BytesIO(html), parser)
    opp1_match_stats = process_match_stat_data(tree, opp1_name)
    opp2_match_stats = process_match_stat_data(tree, opp2_name)
    if opp1_match_stats == opp2_match_stats: ValueError("Matching Results for Match Stats - Player Name Error.")
    return(opp1_match_stats + opp2_match_stats)

def threaded_get_match(match):
    return(match + (['0'] * 28))
    # match_data = []
    # attempts = 0
    # string = match[0] + " " + match[1][:5] + " " + match[6] + " vs " + match[8]
    # while attempts < 3:
    #     try:
    #         match_stats = get_match_stats(match[21], match[6], match[8])
    #         attempts = 3
    #         print(string + " process completed.")
    #         return(match + match_stats)
    #     except ValueError as e:
    #         attempts = 3
    #         print(string + " process failed  -" + str(e))
    #         return(match + (['0'] * 28))
    #     except Exception as e:
    #         attempts += 1
    #         print(string + " process failed  -" + str(e))
    #         if attempts == 3: return(match + (['0'] * 28))
    #         time.sleep(3)

def get_match_data(tournament_data):
    match_data = []
    mp_pool = multiprocessing.Pool(processes=100)
    match_data.extend(mp_pool.map(threaded_get_match, (match for match in tournament_data)))
    mp_pool.close()
    print("Matches Complete")
    return(match_data)

def get_player_urls(match_data):
    player_urls = [[],[]]
    for row in match_data:
        if row[6] not in player_urls[0]:
            player_urls[0].append(row[6])
            player_urls[1].append([row[6], row[7]])
        if row[8] not in player_urls[0]:
            player_urls[0].append(row[8])
            player_urls[1].append([row[8], row[9]])
    return(player_urls[1])

def get_player_overview(player_url):
    url = home_url + player_url
    result = urllib.request.urlopen(url)
    html = result.read()
    parser = etree.HTMLParser()
    tree = etree.parse(io.BytesIO(html), parser)
    return(process_player_overview(tree))

def get_player_statistics(player_url):
    url = home_url + player_url.replace('/overview', '')  + '/player-stats?year=2016&surfaceType=all'
    result = urllib.request.urlopen(url)
    html = result.read()
    parser = etree.HTMLParser()
    tree = etree.parse(io.BytesIO(html), parser)
    return(process_player_statistics(tree))

def get_player_winloss(player_url):
    url = home_url + player_url.replace('/overview', '')  + '/fedex-atp-win-loss'
    result = urllib.request.urlopen(url)
    html = result.read()
    parser = etree.HTMLParser()
    tree = etree.parse(io.BytesIO(html), parser)
    return(process_player_winloss(tree, '3') + process_player_winloss(tree, '5'))

def threaded_get_player_data(player):
    attempts = 0
    while attempts < 3:
        try:
            overview = get_player_overview(player[1])
            statistics = get_player_statistics(player[1])
            winloss = get_player_winloss(player[1])
            print(player[0] + " process Complete")
            attempts = 3
            return([player[0]] + overview + statistics + winloss)
        except IndexError as e:
            print(player[0] + " process Failed " + str(e))
            break
        except Exception as e:
            print(player[0] + " process Failed " + str(e))
            attempts += 1
            time.sleep(3)

def get_player_data(player_urls):
    player_data = []
    players_count = len(player_urls)
    mp_pool = multiprocessing.Pool(processes=80)
    player_data.extend(mp_pool.map(threaded_get_player_data, (player for player in player_urls)))
    mp_pool.close()
    player_data = [player for player in player_data if player is not None]
    print("Player Stats Complete\n" + str(len(player_data)) + "/" + str(players_count) + " players Sucessful")
    return(player_data)

def players(row, player_data):
    p = []
    found_both = 0
    for player_search in [row[6], row[8]]:
        for player in player_data:
            if player_search == player[0]:
                ps = list(player)
                ps.pop(0)
                p.extend(ps)
                found_both += 1
    return(p, found_both)

def date_parser(date_string):
    month_dict = {'January': 1, 'Febuary': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
    date_list = date_string.split(',')
    month, day = date_list[1][1:].split(' ')
    date = datetime.date(int(date_list[2].strip()), month_dict[month], int(day))
    return(date)

def get_prediction_tournament_details(tree):
    title = strip_html(tree.xpath("//table[@class='tourney-results-wrapper']/tr[1]/td[2]/a/text()")[0])
    location = strip_html(tree.xpath("//table[@class='tourney-results-wrapper']/tr[1]/td[2]/span[1]/text()")[0])
    # dates = strip_html(tree.xpath("//table[@class='tourney-results-wrapper']/tr[1]/td[2]/span[2]/text()")[0])
    surface_type = strip_html(tree.xpath("//table[@class='tourney-results-wrapper']/tr[1]/td[3]/table[1]/tbody[1]/tr[1]/td[2]/div[2]/div/span/text()")[0])
    dollars = strip_html(tree.xpath("//table[@class='tourney-results-wrapper']/tr[1]/td[3]/table[1]/tbody[1]/tr[1]/td[4]/div[2]/div/span/text()")[0])
    return([title, location, '', surface_type, dollars])

def process_prediction_matches(tree, date):
    tournament_details = get_prediction_tournament_details(tree)
    date_string = [str(date.year) + "." + str(date.month) + "." + str(date.day)]
    opp1s = tree.xpath("//table[@class='day-table']/tbody[1]/tr/td[4]/a[1]/text()")
    opp2s = tree.xpath("//table[@class='day-table']/tbody[1]/tr/td[8]/div/a[1]/text()")
    counts = tree.xpath("//table[@class='day-table']/tbody[1]/tr/td[4]")
    vs = []
    [vs.append(date_string + tournament_details + [opp1s[i], '', opp2s[i], '']) for i in range(len(opp1s)) if len(counts[i].findall('a')) == 1]
    return(vs)

def get_prediction_matches_days(tree, link):
    day_count = len(tree.xpath("//div[@class='dropdown-holder']/ul/li"))
    matches = []
    for day in range(day_count):
        url = home_url + link + '?day=' + str(day+1)
        result = urllib.request.urlopen(url)
        html = result.read()
        parser = etree.HTMLParser()
        tree = etree.parse(io.BytesIO(html), parser)
        page_date_str = tree.xpath("//h3[@class='day-table-date']/text()")[0]
        page_date = date_parser(page_date_str)
        days = page_date - datetime.date.today()
        if days.days >= 0:
            matches.extend(process_prediction_matches(tree, page_date))
    return(matches)

def get_prediction_matches(link):
    url = home_url + link
    result = urllib.request.urlopen(url)
    html = result.read()
    parser = etree.HTMLParser()
    tree = etree.parse(io.BytesIO(html), parser)
    matches = get_prediction_matches_days(tree, link)
    return(matches)

def multi_tournament_links(link):
     url = home_url + link
     result = urllib.request.urlopen(url)
     html = result.read()
     parser = etree.HTMLParser()
     tree = etree.parse(io.BytesIO(html), parser)
     tournament_links = tree.xpath("//div[@class='last-events-played-slider royalSlider']/a/@href") #Next / Previous Link
     return(tournament_links)

def get_prediction_daily_schedule():
    url = home_url + '/en/scores/current/'
    result = urllib.request.urlopen(url)
    html = result.read()
    parser = etree.HTMLParser()
    tree = etree.parse(io.BytesIO(html), parser)
    tournament_links = tree.xpath("//div[@class='last-events-played-slider royalSlider']/a/@href") #Next / Previous Link
    [tournament_links.extend(multi_tournament_links(link)) for link in list(tournament_links) for _ in range(5)]
    daily_schedule_links = [link.replace('/results', '/daily-schedule').replace('/live-scores', '/daily-schedule')  for link in set(tournament_links)]
    matches = []
    [matches.extend(get_prediction_matches(daily_schedule_link)) for daily_schedule_link in set(daily_schedule_links)]
    return(matches)

def hist_to_csv(match_data):
    with open('../tennis/tennis_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headings)
        for row in match_data:
            player_data_info, found_both = players(row, player_data)
            if found_both == 2:
                writer.writerow(row + player_data_info)
    print("Match History Complete.")

def prediction_to_csv(prediction_matches):
    with open('../tennis/tennis_data_prediction.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headings)
        for row in prediction_matches:
            player_data_info, found_both = players(row, player_data)
            if found_both == 2:
                writer.writerow(row + ([''] * 40) + player_data_info)
    print("Match Prediction Complete.")

home_url = 'http://www.atpworldtour.com'
years = [2016, 2017]
headings = ['date', 'title', 'location', 'surface', 'surfaceType', 'dollar', 'opp1', 'opp1_url', 'opp2', 'opp2_url', 'winner', 'opp1_set1', 'opp2_set1', 'opp1_set2', 'opp2_set2', 'opp1_set3', 'opp2_set3', 'opp1_set4', 'opp2_set4', 'opp1_set5', 'opp2_set5', 'match_link',
                 'opp1_aces_match', 'opp1_double_faults_match', 'opp1_first_serve_perentage_match', 'opp1_first_serve_points_won_match', 'opp1_second_serve_points_won_match', 'opp1_break_points_saved_match', 'opp1_service_games_played_match', 'opp1_first_serve_return_points_won_match', 'opp1_second_serve_return_points_won_match', 'opp1_break_points_converted_match', 'opp1_return_games_played_match', 'opp1_total_service_points_won_match', 'opp1_total_return_points_won_match', 'opp1_total_points_won_match',
                 'opp2_aces_match', 'opp2_double_faults_match', 'opp2_first_serve_perentage_match', 'opp2_first_serve_points_won_match', 'opp2_second_serve_points_won_match', 'opp2_break_points_saved_match', 'opp2_service_games_played_match', 'opp2_first_serve_return_points_won_match', 'opp2_second_serve_return_points_won_match', 'opp2_break_points_converted_match', 'opp2_return_games_played_match', 'opp2_total_service_points_won_match', 'opp2_total_return_points_won_match', 'opp2_total_points_won_match',
                 'opp1_rank', 'opp1_age', 'opp1_year_pro', 'opp1_weight', 'opp1_height', 'opp1_hand',
                 'opp1_first_serve', 'opp1_first_serve_points_won', 'opp1_second_serve_points_won', 'opp1_break_points_saved', 'opp1_service_points_won', 'opp1_total_service_points_won', 'opp1_first_serve_return_points_won', 'opp1_second_serve_return_points_won', 'opp1_break_points_converted', 'opp1_return_games_won', 'opp1_return_points_won', 'opp1_total_points_won',
                 'opp1_overall_ytd', 'opp1_grandslams_ytd', 'opp1_atpworld_ytd', 'opp1_tiebreaks_ytd', 'opp1_vs_top_10_ytd', 'opp1_finals_ytd', 'opp1_deciding_set_ytd', 'opp1_fifth_set_record_ytd', 'opp1_clay_ytd', 'opp1_grass_ytd', 'opp1_hard_ytd', 'opp1_carpet_ytd', 'opp1_indoor_ytd', 'opp1_outdoor_ytd', 'opp1_after_winning_first_set_ytd', 'opp1_after_losing_first_set_ytd', 'opp1_vs_right_handers_ytd', 'opp1_vs_left_handers_ytd',
                 'opp1_overall_career', 'opp1_grandslams_career', 'opp1_atpworld_career', 'opp1_tiebreaks_career', 'opp1_vs_top_10_career', 'opp1_finals_career', 'opp1_deciding_set_career', 'opp1_fifth_set_record_career', 'opp1_clay_career', 'opp1_grass_career', 'opp1_hard_career', 'opp1_carpet_career', 'opp1_indoor_career', 'opp1_outdoor_career', 'opp1_after_winning_first_set_career', 'opp1_after_losing_first_set_career', 'opp1_vs_right_handers_career', 'opp1_vs_left_handers_career',
                 'opp2_rank', 'opp2_age', 'opp2_year_pro', 'opp2_weight', 'opp2_height', 'opp2_hand',
                 'opp2_first_serve', 'opp2_first_serve_points_won', 'opp2_second_serve_points_won', 'opp2_break_points_saved', 'opp2_service_points_won', 'opp2_total_service_points_won', 'opp2_first_serve_return_points_won', 'opp2_second_serve_return_points_won', 'opp2_break_points_converted', 'opp2_return_games_won', 'opp2_return_points_won', 'opp2_total_points_won',
                 'opp2_overall_ytd', 'opp2_grandslams_ytd', 'opp2_atpworld_ytd', 'opp2_tiebreaks_ytd', 'opp2_vs_top_10_ytd', 'opp2_finals_ytd', 'opp2_deciding_set_ytd', 'opp2_fifth_set_record_ytd', 'opp2_clay_ytd', 'opp2_grass_ytd', 'opp2_hard_ytd', 'opp2_carpet_ytd', 'opp2_indoor_ytd', 'opp2_outdoor_ytd', 'opp2_after_winning_first_set_ytd', 'opp2_after_losing_first_set_ytd', 'opp2_vs_right_handers_ytd', 'opp2_vs_left_handers_ytd',
                 'opp2_overall_career', 'opp2_grandslams_career', 'opp2_atpworld_career', 'opp2_tiebreaks_career', 'opp2_vs_top_10_career', 'opp2_finals_career', 'opp2_deciding_set_career', 'opp2_fifth_set_record_career', 'opp2_clay_career', 'opp2_grass_career', 'opp2_hard_career', 'opp2_carpet_career', 'opp2_indoor_career', 'opp2_outdoor_career', 'opp2_after_winning_first_set_career', 'opp2_after_losing_first_set_career', 'opp2_vs_right_handers_career', 'opp2_vs_left_handers_career'
                 ]

if __name__ == '__main__':
    year_data = get_year_data()
    # date, title, location, surface, surfaceType, dollar, opp1, opp1_url, opp2, opp2_url, winner, w1, l1, w2, l2, w3, l3, w4, l4, w5, l5, match_link
    tournament_data = get_tournament_data(year_data)

    match_data = get_match_data(tournament_data)
    # names, urls
    player_urls = get_player_urls(match_data)
    #name, rank, age, year_pro, wieght, hieght, hand, first_serve, first_serve_points_won, second_serve_points_won, break_points_saved, service_points_won, total_service_points_won, first_serve_return_points_won, second_serve_return_points_won, break_points_converted, return_games_won, return_points_won, total_points_won, overall_ytd, grandslams_ytd, atpworld_ytd, tiebreaks_ytd, vs_top_10_ytd, finals_ytd, deciding_set_ytd, fifth_set_record_ytd, clay_ytd, grass_ytd, hard_ytd, carpet_ytd, indoor_ytd, outdoor_ytd, after_winning_first_set_ytd, after_losing_first_set_ytd, vs_right_handers_ytd, vs_left_handers_ytd
    player_data = get_player_data(player_urls)

    hist_to_csv(match_data)

    prediction_matches = get_prediction_daily_schedule()
    prediction_to_csv(prediction_matches)
