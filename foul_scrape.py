import csv
import main
import scrape
from models.match import Match

def parse_match_spreadsheet(filename=None):
    if not filename:
        filename = main.vinput('Filename to import', lambda f: f.endswith('.csv'))

    read = csv.reader(open(filename, newline=''))

    # Read the headers and find the column positions
    headers = read.__next__()
    index_red = [headers.index('red1'), headers.index('red2'), headers.index('red3')]
    index_blue = [headers.index('blue1'), headers.index('blue2'), headers.index('blue3')]
    index_matchno = headers.index('match')
    index_rtotal = headers.index('redfinal')
    index_btotal = headers.index('bluefinal')
    index_rfouls = headers.index('rfpts')
    index_bfouls = headers.index('bfpts')
    index_rauto = headers.index('rhpts')
    index_bauto = headers.index('bhpts')
    index_rteleop = headers.index('rtpts')
    index_bteleop = headers.index('btpts')
    index_date = headers.index('date')
    matches = []

    for row in read:
        red = []
        blue = []
        for i, column in enumerate(row):
            if i in index_red:
                red.append(int(column))
            elif i in index_blue:
                blue.append(int(column))
            elif i == index_matchno:
                id = int(column)
            elif i == index_bauto:
                bauto = int(column)
            elif i == index_rauto:
                rauto = int(column)
            elif i == index_bfouls:
                bfouls = int(column)
            elif i == index_rfouls:
                rfouls = int(column)
            elif i == index_btotal:
                btotal = int(column)
            elif i == index_rtotal:
                rtotal = int(column)
            elif i == index_bteleop:
                bteleop = int(column)
            elif i == index_rteleop:
                rteleop = int(column)
            elif i == index_date:
                date = column
        match = Match(id, date, red, blue, rtotal, btotal)
        match.rfouls = rfouls
        match.bfouls = bfouls
        match.rteleop = rteleop
        match.bteleop = bteleop
        match.rauto = rauto
        match.bauto = bauto

        matches.append(match)

    return matches

def main_f():
    matches = parse_match_spreadsheet()
    fouls = {}

    reg = main.read_regional()

    reg_teams = [t.number for t in scrape.download_teams(reg)]

    for m in matches:
        for t in m.red:
            if t in reg_teams:
                if t not in fouls:
                    fouls[t] = [m.rfouls, 1]
                else:
                    fouls[t][0] += m.rfouls
                    fouls[t][1] += 1
        for t in m.blue:
            if t in reg_teams:
                if t not in fouls:
                    fouls[t] = [m.bfouls, 1]
                else:
                    fouls[t][0] += m.bfouls
                    fouls[t][1] += 1

    print(max(fouls.values(), key=lambda a: a[0]))
    fouls = {t: ((f_tpl[0]/f_tpl[1]) if f_tpl[1] != 0 else '') for t, f_tpl in fouls.items()}
    main.mk_csv(['Team', 'Average Fouls'], [lambda t: t, lambda t: fouls[t]], 'avg_fouls.csv', fouls)

if __name__ == '__main__':
    main_f()
