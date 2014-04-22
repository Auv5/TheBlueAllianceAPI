import scrape
from datetime import date
from http.client import HTTPConnection

import json

from models.team import Team, get_team

import numpy as np

def vinput(prompt, validator, default=None):
    if default:
        prompt = prompt + ' [' + default + ']:'
    else:
        prompt += ':'
    print(prompt)
    rawin = input('\t--> ').rstrip()
    val = validator(rawin)
    while ((not default) or rawin) and val == False:
        rawin = input('\t--> ').rstrip()
        val = validator(rawin)
    if rawin or not default:
        return rawin
    else:
        return default

def is_integer(s, silence=False):
    try:
        int(s)
        return s
    except ValueError:
        return False

def read_regional():
    today = date.today()
    year = today.year

    search = vinput('Search for regional', lambda s: s)

    print('Downloading regionals...')

    conn = HTTPConnection('www.thebluealliance.com')
    conn.request('GET', '/api/v1/events/list?year=' + str(year), headers=scrape.DEF_HEADERS)

    r = conn.getresponse()
    answer = r.read().decode('utf-8')
    data = json.loads(answer)

    matches = []

    for k in data:
        if (k['short_name'] and search.lower() in k['short_name'].lower()) or search.lower() in k['name'].lower():
            matches.append(k)

    print('\nResults:')
    index = 1
    for m in matches:
        print('\t' + str(index) + '. ' + (m['short_name'] or m['name']) + ' on ' + m['start_date'])
        index += 1

    number = vinput('\nEnter regional number', is_integer, '1')

    regional = matches[int(number)-1]

    print('Downloading event details...')

    conn.request('GET', '/api/v1/event/details?event=' + regional['key'], headers=scrape.DEF_HEADERS)

    r = conn.getresponse()

    answer = r.read().decode('utf-8')
    reg_data = json.loads(answer)

    return reg_data

def make_regionals(regionals_gen, curr_id, teams):
    regionals = []

    # For percentage calculation.
    total = len(regionals_gen)

    prevpercent = 0

    counter = 0

    for r in regionals_gen:
        reg = scrape.download_regional(r['key'])

        raw_teams = [int(t.replace('frc','')) for t in reg['teams']]

        reg['nteams'] = []

        for t in teams:
            if t.number in raw_teams:
                t.regionals.append(reg['key'])
                reg['nteams'].append(t)
                regionals.append(reg)
                break

    return regionals

def calc_ccwms(regional):
    if isinstance(regional, str):
        regional = scrape.download_regional(regional)
    teams = scrape.download_teams(regional)
    matches = scrape.scrape_matches(regional['key'])

    # Regional hasn't happened yet
    if len(matches) == 0:
        return []

    to_match_count = [[0 for t in teams] for t in teams]

    to_vert_matrix = [0 for t in teams]

    for m in matches:
        for t in m.red:
            if m.red_score != -1:
                for t2 in m.red:
                    to_match_count[teams.index(t)][teams.index(t2)] += 1
                to_vert_matrix[teams.index(t)] += m.red_score - m.blue_score
        for t in m.blue:
            if m.blue_score != -1:
                for t2 in m.blue:
                    to_match_count[teams.index(t)][teams.index(t2)] += 1
                to_vert_matrix[teams.index(t)] += m.blue_score - m.red_score

    try:
        ccwms = np.linalg.solve(to_match_count, to_vert_matrix)
    except:
        # Disregard the (hopefully slight) error values
        ccwms = np.linalg.lstsq(to_match_count, to_vert_matrix)[0]

    return [(teams[i], opr) for i, opr in enumerate(ccwms.tolist())]

def calc_oprs(regional):
    if isinstance(regional, str):
        regional = scrape.download_regional(regional)
    teams = scrape.download_teams(regional)
    matches = scrape.scrape_matches(regional['key'])

    # Regional hasn't happened yet
    if len(matches) == 0:
        return []

    to_match_count = [[0 for t in teams] for t in teams]

    to_vert_matrix = [0 for t in teams]

    for m in matches:
        for t in m.red:
            if m.red_score != -1:
                for t2 in m.red:
                    to_match_count[teams.index(t)][teams.index(t2)] += 1
                to_vert_matrix[teams.index(t)] += m.red_score
        for t in m.blue:
            if m.blue_score != -1:
                for t2 in m.blue:
                    to_match_count[teams.index(t)][teams.index(t2)] += 1
                to_vert_matrix[teams.index(t)] += m.blue_score

    try:
        oprs = np.linalg.solve(to_match_count, to_vert_matrix)
    except:
        # Disregard the (hopefully slight) error values
        oprs = np.linalg.lstsq(to_match_count, to_vert_matrix)[0]

    return [(teams[i], opr) for i, opr in enumerate(oprs.tolist())]

def mk_csv(headers, functions, outfname, item_list):
    outf = open(outfname, 'w')

    outf.write(','.join(headers) + ',\n')

    for t in item_list:
        for h in functions:
            val = h(t)
            if val != '':
                outf.write("\"" + str(val).replace('"', '') + '\",')
            else:
                outf.write(',')
        outf.write('\n')


def to_csv(oprs, ccwm, teams):
    mk_csv(['Team Number', 'OPR', 'CCWM'], [lambda self: self.number, lambda self: oprs[self] if self in oprs else 0, lambda self: ccwm[self] if self in ccwm else 0], 'output.csv', teams)
    print('Values written to output.csv')

def main():
    regional = read_regional()

    teams = scrape.download_teams(regional, False)

    regionals_gen = scrape.download_regionals(vinput('Year for regionals', is_integer, str(date.today().year)))

    regionals = make_regionals(regionals_gen, regional['key'], teams)

    oprs = {}
    ccwms = {}

    for r in regionals:
        for t, opr in calc_oprs(r):
            if t in teams:
                if t not in oprs:
                    oprs[t] = [opr, 1]
                else:
                    oprs[t][0] += opr
                    oprs[t][1] += 1
        for t, ccwm in calc_ccwms(r):
            if t in teams:
                if t not in ccwms:
                    ccwms[t] = [ccwm, 1]
                else:
                    ccwms[t][0] += ccwm
                    ccwms[t][1] += 1

    oprs = {t: ((opr_tup[0]/opr_tup[1]) if opr_tup[1] > 0 else 0) for t, opr_tup in oprs.items()}
    ccwms = {t: ((ccwm_tup[0]/ccwm_tup[1]) if ccwm_tup[1] > 0 else 0) for t, ccwm_tup in ccwms.items()}

    to_csv(oprs, ccwms, teams)

if __name__ == '__main__':
    main()
