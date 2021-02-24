from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import csv
import parse
import requests
from selenium import webdriver

match_id = 1
pt_format = '{}/{} ({})'
rb_format = '{}+{} {}'
date_format = '{} {}'


# Reorganises key match information to the desired format/order
def defineGameinfo(home, away, info, rodada, fase, att, income, h_sc, a_sc):
    # MATCH_ID | HOME_T | AWAY_T | DATE | TIME | HOME_SC | AWAY_SC | LOCAL | LEAGUE_ED | HOME_CH | AWAY_CH | REF1 | REF2 | REF3 | STAGE | ATT | MONEY
    global match_id
    #data/hora, local, campeonato, arb1, arb2, arb3, tec_home, tec_away
    # print(info)
    date, time = parse.parse(date_format, info[0])
    info = [match_id, home, away, date, time, h_sc, a_sc, info[1], info[2],
            info[6], info[7], info[3], info[4], info[5], fase, rodada, att, income]

    return info


# Reorganises player stats row to the desired format/order
def defineScoreboard(raw, qtr):
    global match_id
    if qtr == 'general':
        qtr = 0
    # MATCH_ID | PLAYER | TEAM | N# | MIN | DR | OR | AST | 3PM | 3PA | 2PM | 2PA | FTM | FTA | STL | BLK | FC | FR | TO | DNK | +/- | EFF
    sb = [match_id, raw[1], raw[9], qtr, raw[0], raw[3], raw[4], raw[5], raw[6], raw[18], raw[19], raw[20],
          raw[21], raw[7], raw[8], raw[10], raw[11], raw[12], raw[13], raw[14], raw[15], raw[16], raw[17]]

    return sb


# Get general stats from match when quarterly data isn't available
def getGeneralStats(soup, round, stage, league, home_score, away_score):
    global match_id
    home, away, info = transferGameData(
        soup, round, stage, home_score, away_score)
    transferData(soup, "general", "home", home)
    transferData(soup, "general", "away", away)
    match_id += 1


# Get game stats from quarterly data
def getQuarterlyStats(soup, round, stage, league, home_score, away_score):
    global match_id
    home, away, info = transferGameData(
        soup, round, stage, home_score, away_score)
    transferData(soup, "1", "home", home)
    transferData(soup, "2", "home", home)
    transferData(soup, "3", "home", home)
    transferData(soup, "4", "home", home)
    transferData(soup, "1", "away", away)
    transferData(soup, "2", "away", away)
    transferData(soup, "3", "away", away)
    transferData(soup, "4", "away", away)

    match_id += 1


# main parser function, finds table, columns and rows
def transferData(soup, idx, homeaway, name):

    homeaway_id_1 = f"team_{homeaway}_stats"
    homeaway_id_2 = f"stats_real_time_table_{homeaway}"

    try:
        team_table = soup.find(id=homeaway_id_1)
    except:
        team_table = soup.find(id=homeaway_id_2)

    try:
        step_table = team_table.find(idx=idx)
    except:
        step_table = team_table.find(idq=idx)

    cols = step_table.find_all("th")
    col_data = []
    for col in cols:
        col_data.append(col.string)

    body = step_table.find("tbody")
    rows = body.find_all("tr")

    with open('scoreboard.csv', 'a', newline='') as csvfile:
        spamwriter = csv.writer(csvfile)
        for row in rows:
            # [4] is PTM/PTA (PT%)
            # [5] is DREB+OREB REB
            # [7] is 3PM/3PA (3P%)
            # [8] is 2PM/2PA (2P%)
            # [9] is FTM/FTA (FT%)
            # MATCH_ID | PLAYER | TEAM | N# | MIN | DR | OR | 3PM | 3PA | 2PM | 2PA | FTM | FTA | STL | BLK | FC | FR | TO | DNK | +/- | EFF
            columns = [data.get_text(strip=True)
                       for data in row.find_all("td")]
            drb, orb, trb = parse.parse(rb_format, columns[5])
            p3m, p3a, p3p = parse.parse(pt_format, columns[7])
            p2m, p2a, p2p = parse.parse(pt_format, columns[8])
            ftm, fta, ftp = parse.parse(pt_format, columns[9])
            columns[4] = drb
            columns[5] = orb
            columns[7] = ftm
            columns[8] = fta
            columns[9] = name
            columns.append(p3m)
            columns.append(p3a)
            columns.append(p2m)
            columns.append(p2a)

            scoreboard = defineScoreboard(columns, idx)
            spamwriter.writerow(scoreboard)


def transferGameData(soup, round, stage, home_score, away_score):
    try:
        teams = soup.find(class_="notice_open_screen_two").find_all(
            class_="hide-for-large")
    except:
        teams = soup.find(class_="score_header").find_all(
            class_="hide-for-large")
    home = teams[0].get_text()
    away = teams[1].get_text()
    #print("HOME: " + home)
    #print("AWAY: " + away)

    stuff = []
    info = soup.find(id="infos")
    allin = info.find_all("td")
    for i in range(0, len(allin)):
        stuff.append(allin[i].get_text(strip=True))

    #date, time = parse.parse(date_format, stuff[0])
    #stuff[0] = date
    # stuff.append(time)
    #data/hora, local, campeonato, arb1, arb2, arb3, tec_home, tec_away
    # print(stuff)

    game_info = defineGameinfo(
        home, away, stuff, round, stage, '', '', home_score, away_score)

    with open('match.csv', 'a', newline='') as csvfile:
        spamwriter = csv.writer(csvfile)
        spamwriter.writerow(game_info)

    return home, away, stuff


def processURL(url, round, stage, league, home_score, away_score):
    # driver = webdriver.Firefox()
    # driver.get(url)
    # driver.set_page_load_timeout(20)
    # driver.maximize_window()
    # driver.switch_to.frame(driver.find_element_by_id('stats'))
    # elem = driver.find_element_by_id('stats')
    # print(elem.get_attribute('innerHTML'))
    resp = requests.get(url).content
    # req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    # con = urlopen(req)
    soup = BeautifulSoup(resp, "lxml")

    team_table = soup.find(id="team_away_stats")
    try:
        tt_4th = team_table.find(idx="4")
    except:
        try:
            tt_4th = team_table.find(idq="4")
        except:
            tt_4th = None

    if tt_4th == None:
        getGeneralStats(soup, round, stage, league, home_score, away_score)
    else:
        getQuarterlyStats(soup, round, stage, league, home_score, away_score)


def main():
    fname = "nbb//all.txt"
    with open(fname) as f:
        seasons = f.readlines()
    seasons = [x.strip() for x in seasons]

    print("SEASONS TO GO: " + str(seasons))

    for s in seasons:
        with open(s) as n:
            content = n.readlines()
        content = [x.strip() for x in content]
        for url in content:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            con = urlopen(req)
            soup = BeautifulSoup(con, "lxml")

            team_table = soup.find(id="team_away_stats")
            tt_4th = team_table.find(idx="4")

            if tt_4th == None:
                getGeneralStats(soup)
            else:
                getQuarterlyStats(soup)


if __name__ == "__main__":
    main()
