#######################################################################################################
##                           WEB SCRAPING - NOVO BASQUETE BRASIL STATS                               ##
## - Acessa página "tabela" e salva informações gerais, além de recuperar o link de cada partida     ##
## - #BeLikeMarcezico                                                                                ##
## - Salva em algum lugar                                                                            ##
#######################################################################################################

from urllib.request import urlopen, Request
import requests
from bs4 import BeautifulSoup
import csv
import parse
import time
import collector

# website id for NBB editions, missing a couple playoffs
l = [1, 2, 3, 4, 8, 15, 20, 27, 34, 41, 47, 54]


def extract_data(season, phase, error_log_path, phase_name="SEASON", season_num="?"):
    """
    Extracts data from all games for given season and phase (regular/playoffs)

    Parameters
    ----------
    season : int
            Season id
    phase : int
            Phase id (usually 1 for regular season and 2 for playoffs)
    error_log_path : str
            Path for error log file
    phase_name : str
            Name of the phase (optional)
    season_num : str
            Season number (optional)
    """

    url = "http://lnb.com.br/nbb/tabela-de-jogos/?season%5B%5D={}&phase%5B%5D={}&wherePlaying=-1&played=-1".format(
        season, phase)
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    con = urlopen(req)

    soup = BeautifulSoup(con, "lxml")
    games = soup.find_all(class_="score_value show-for-medium")
    gametable = soup.find(class_="table_matches_table")

    # Print season phase and number while processing
    print("{} {}: ".format(phase_name, season_num), end="", flush=True)

    # For each match found in list
    for row in gametable.find("tbody").find_all("tr"):
        # Gets weblink for match
        weblink = row.find('a', href=True)['href']

        # Process info only if there is any
        if weblink:
            try:
                round = row.find(class_="game_value hide_value").find(
                    class_="number").get_text(strip=True)
            except:
                round = ""
            stage = row.find(class_="stage_value_abbr").get_text(strip=True)
            edition = row.find(
                class_="champ_value hide_value").get_text(strip=True)
            h_score = row.find(
                class_="score_value show-for-medium").find(class_="home").get_text(strip=True)
            a_score = row.find(
                class_="score_value show-for-medium").find(class_="away").get_text(strip=True)

            # Calls function from collector.py to process single match page
            try:
            collector.processURL(weblink, round, stage,
                                     edition, h_score, a_score)
            except:
                with open(error_log_path, "a") as er:
                    stg = f"{edition};{round};{stage};{weblink}\n"
                    er.write(stg)

            # Indicates completion of another game
            print("|", end="", flush=True)


# The main function will loop from 1 to 9 calling a extract_data function for each number, which
# represents a season in NBB, called functions will be responsible for extarcting and saving
# data about these seasons
def main():
    for i in range(1, 10):
        extract_data(season=l[i-1], phase=1, error_log_path="scraping_errors.txt",
                     phase_name="REGULAR ", season_num=i)
        print("")
        extract_data(season=l[i-1], phase=2, error_log_path="scraping_errors.txt",
                     phase_name="PLAYOFFS", season_num=i)
        time.sleep(.5)
        print("\nSeason %d COMPLETE!!" % i)


if __name__ == "__main__":
    main()
