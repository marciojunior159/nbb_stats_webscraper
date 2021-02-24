from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import csv, parse
import collector
# missing couple playoffs
l = [1,2,3,4,8,15,20,27,34,41]

abbs = {}

def clear_txt(file):
	with open(file, "w") as f:
		f.write("")

def addNew(key, name):
	global abbs
	a = abbs.get(key)

	if a is not None:
		for t in abbs[key]:
			if t == name:
				return
		abbs[key].append(name)
	else:
		abbs[key] = [name]
	
	return

for i in [1,2,3,4,8,15,20,27,34,41,47,54,59]:
	url_regular = "http://lnb.com.br/nbb/tabela-de-jogos/?season%5B%5D=" + str(l[i-1]) + "&phase%5B%5D=1&wherePlaying=-1&played=-1"
	url_playoff = "http://lnb.com.br/nbb/tabela-de-jogos/?season%5B%5D=" + str(l[i-1]) + "&phase%5B%5D=2&wherePlaying=-1&played=-1"
	req = Request(url_regular, headers={'User-Agent' : 'Mozilla/5.0'})
	con = urlopen(req)
	soup = BeautifulSoup(con, "lxml")
	gametable = soup.find(class_ = "table_matches_table")
	
	for row in gametable.find("tbody").find_all("tr"):
		home = row.find(class_ = "home_team_value show-for-medium").find(class_ = "team-shortname").get_text(strip=True)
		away = row.find(class_ = "visitor_team_value show-for-medium").find(class_ = "team-shortname").get_text(strip=True)
		temp = row.find(class_ = "hide-for-medium matche_for_small").find_all(class_ = "small-4 columns float-left")
		home_abbv = temp[0].get_text(strip=True)
		away_abbv = temp[1].get_text(strip=True)
		
		addNew(home_abbv, home)
		addNew(away_abbv, away)
		#print("HOME: %s | %s" % (home_abbv, home))
		#print("AWAY: %s | %s" % (away_abbv, away))
	
	
	print("\nSeason %d COMPLETE!!" % i)



with open('dict_abbv.csv', 'w', newline='') as csvfile:
	writer = csv.writer(csvfile)
	for key, values in abbs.items():
		writer.writerow([key, *values])
		# print("{0},{1}".format(key, values))
		# csvfile.write("{0},{1}".format(key, values))

	