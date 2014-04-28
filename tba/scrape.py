### Scrape for The Blue Alliance's v2 API.

DEF_HEADERS = {'User-Agent': 'TrueBlue bluealliance Scraper',
        'X-TBA-App-Id': 'frc2994:scouting:v2'}

BLUEALLIANCE_DOMAIN = 'www.thebluealliance.com'
BASEPATH = '/api/v2'

## False if caching is not desired for JSON downloads.
CACHE = True
## Force "quiet" mode on cache_or_get_json.
QUIET = False
## If false, simulate caching behaviour
memcache = {}

from http.client import HTTPConnection
from models.match import Match
from models.team import Team, get_team
from models.regional import Regional

import json
import os
import csv
import numpy as np

## Caches expensive operations if the option CACHE is set.
def cache_or_get_json(name, func, *args, **kwargs):
    if not CACHE:
        # If they don't want to cache to the filesystem, cache to memory.
        if name not in memcache:
            if not QUIET:
                print('Generating: ' + name)
            return json.loads(func(*args))
        else:
            if not QUIET:
                print('Using cached: ' + name)
            return memcache[name]

    if 'quiet' in kwargs:
        quiet = kwargs['quiet']
    else:
        quiet = QUIET

    if not os.path.isdir('cache'):
        os.mkdir('cache')

    filename = 'cache/' + name + '.json'

    if os.path.exists(filename):
        if not quiet:
            print('Using cached: ' + name)
        return json.loads(open(filename, 'r').read())
    else:
        if not quiet:
            print('Generating: ' + name)
        value = func(*args)
        open(filename, 'w').write(value)
        return json.loads(value)

def download_regional(key):
    return download_regionals_impl([key])[0]

def download_regionals(years, full_teams=False, calcs=False):
    reg_keys = [cache_or_get_json('regionals' + str(year), bluealliance_download_file, '/events/' + str(year)) for year in years]
    # Flatten the list of lists
    reg_keys = [item for sublist in reg_keys for item in sublist]

    return download_regionals_impl(reg_keys, full_teams, calcs)

def download_regionals_impl(reg_keys, full_teams=False, calcs=False):
    spread = _load_spreadsheet('export_breakdown_week7.csv')
    regs = [download_regional_basics(reg) for reg in reg_keys]

    # We don't support off season or unofficial events because some of them are organized by Satan and break the script
    regs = [r for r in regs if r.raw['official']]

    for r in regs:
        if full_teams:
            _complete_matches_teams(r)
        else:
            _minimal_complete_teams(r)
        if calcs:
            _calc_oprs(r)
            _calc_ccwms(r)
        if r.year == 2014 and calcs:
            _complete_match_info(r, spread)
        if calcs:
            _local_stats(r)
    # _calc_global_stats(Team._teams)

    return regs

def rank(teams, get_stat):
    return sorted(teams, key=get_stat, reverse=True)

def percentiles(ranks):
    l = len(ranks)

    # Percentile = rank/total teams

    ret = {team: (rank+1)/l for rank, team in enumerate(ranks)}

    return ret

# def _calc_global_stats(teams, regionals):
#     for r in regionals:
#         opr_glob_ranks = rank(teams, lambda t: t.oprs[r.key])
#         opr_glob_percentiles = percentiles(opr_glob_ranks[r.key])

#         ccwm_glob_ranks = rank(teams, lambda t: t.ccwms[r.key])
#         ccwm_glob_percentiles = percentiles(ccwm_glob_ranks[r.key])

#         teleop_glob_ranks = rank(teams, lambda t: t.teleop_avgs[r.key])
#         teleop_glob_percentiles = percentiles(teleop_glob_ranks[r.key])

#         auto_glob_ranks = rank(teams, lambda t: t.auto_avgs[r.key])
#         auto_glob_percentiles = percentiles(auto_glob_ranks[r.key])

#         foul_glob_ranks = rank(teams, lambda t: t.foul_avgs[r.key])
#         foul_glob_percentiles = percentiles(foul_glob_ranks[r.key])

#         for t in teams:
#             t.opr_glob_ranks[r.key] = opr_glob_ranks.index(t)+1
#             t.opr_glob_percentiles[r.key] = opr_glob_percentiles[t]

#             t.ccwm_glob_ranks[r.key] = ccwm_glob_ranks.index(t)+1
#             t.ccwm_glob_percentiles[r.key] = ccwm_glob_percentiles[t]

#             t.teleop_glob_ranks[r.key] = teleop_glob_ranks.index(t)+1
#             t.teleop_glob_percentiles[r.key] = teleop_glob_percentiles[t]

#             t.auto_glob_ranks[r.key] = auto_glob_ranks.index(t)+1
#             t.auto_glob_percentiles[r.key] = auto_glob_percentiles[t]

#             t.foul_glob_ranks[r.key] = foul_glob_ranks.index(t)+1
#             t.foul_glob_percentiles[r.key] = foul_glob_percentiles[t]

def _local_stats(r):
    if len(r.matches):
        r.opr_loc_ranks = rank(r.teams, lambda t: t.oprs[r.key])
        r.opr_loc_percentiles = percentiles(r.opr_loc_ranks)

        r.ccwm_loc_ranks = rank(r.teams, lambda t: t.ccwms[r.key])
        r.ccwm_loc_percentiles = percentiles(r.ccwm_loc_ranks)

    ## We only have data for year = 2014
    if r.year == 2014:
        r.teleop_loc_ranks = rank(r.teams, lambda t: t.teleop_avgs[r.key])
        r.teleop_loc_percentiles = percentiles(r.teleop_loc_ranks)

        r.auto_loc_ranks = rank(r.teams, lambda t: t.auto_avgs[r.key])
        r.auto_loc_percentiles = percentiles(r.auto_loc_ranks)

        r.foul_loc_ranks = rank(r.teams, lambda t: t.foul_avgs[r.key])
        r.foul_loc_percentiles = percentiles(r.foul_loc_ranks)


def _complete_match_info(r, spread):
    relevant = [m for m in spread if m['event'] == r.event_code]

    for t in r.teams:
        red_matches = [m for m in relevant if m['red1'] == t.number or m['red2'] == t.number or m['red3'] == t.number]
        blue_matches = [m for m in relevant if m['blue1'] == t.number or m['blue2'] == t.number or m['blue3'] == t.number]
        num = len(red_matches) + len(blue_matches)
        if num:
            teleop = (sum(m['rtpts'] for m in red_matches) + sum(m['btpts'] for m in blue_matches)) / num
            auto = (sum(m['rhpts'] for m in red_matches) + sum(m['bhpts'] for m in blue_matches)) / num
            fouls = (sum(m['rfpts'] for m in red_matches) + sum(m['bfpts'] for m in blue_matches)) / num
        else:
            teleop = 0
            auto = 0
            fouls = 0

        r.teleop_avgs[t] = int(teleop)
        r.auto_avgs[t] = int(auto)
        r.foul_avgs[t] = int(fouls)

        t.teleop_avgs[r.key] = int(teleop)
        t.auto_avgs[r.key] = int(auto)
        t.foul_avgs[r.key] = int(fouls)

def _load_spreadsheet(filename):
    read = csv.reader(open(filename, newline=''))

    headers = read.__next__()
    indexes = {headers.index('red1'): 'red1', headers.index('red2'): 'red2', headers.index('red3'): 'red3', headers.index('blue1'): 'blue1', headers.index('match'): 'match', headers.index('redfinal'): 'redfinal', headers.index('bluefinal'): 'bluefinal', headers.index('rfpts'): 'rfpts', headers.index('bfpts'): 'bfpts', headers.index('rhpts'): 'rhpts', headers.index('bhpts'): 'bhpts', headers.index('rtpts'): 'rtpts', headers.index('btpts'): 'btpts', headers.index('date'): 'date'}

    ret = []

    for row in read:
        ret_sub = {}
        for i in indexes:
            ret_sub[indexes[i]] = row[i]

    return ret

def _minimal_complete_teams(r):
    r.teams =  [get_team(t_raw['team_number'], t_raw['nickname']) for t_raw in
                cache_or_get_json('teams' + r.key, bluealliance_download_file, '/event/' + r.key + '/teams')]

def _complete_matches_teams(r):
    # Keep track of match numbers for fast lookup of if a match has already been added
    mtrack = {}

    event_teams = cache_or_get_json('teams' + r.key, bluealliance_download_file, '/event/' + r.key + '/teams')

    for t_small in event_teams:
        t = get_team(t_small['team_number'], t_small['nickname'])
        t.regionals.append(r.key)
        t.location = t_small['location']
        t_large = cache_or_get_json('team' + str(t.number) + '_' + str(r.year), bluealliance_download_file, '/team/frc' + str(t.number) + '/' + str(r.year))
        event = next(ev for ev in t_large['events'] if ev['key'] == r.key)
        eliminated_in = 'Quals'
        curr_index = 0
        MAPPINGS = {'qm': 'Quals', 'qf': 'Quarters', 'sf': 'Semis', 'f': 'Finals'}
        ORDER = ['qm', 'qf', 'sf', 'f']

        for m in event['matches']:
            ind = ORDER.index(m['comp_level'])
            if ind > curr_index:
                curr_index = ind
                eliminated_in = MAPPINGS[m['comp_level']]

            mtrack_id = str(m['match_number']) + m['comp_level']
            if mtrack_id not in mtrack:
                # Create a match object from the match model.
                m_obj = Match(m['match_number'], [get_team(int(t.replace('frc', '')), None) for t in m['alliances']['red']['teams']], [get_team(int(t.replace('frc', '')), None) for t in m['alliances']['blue']['teams']], int(m['alliances']['red']['score']), int(m['alliances']['blue']['score']))
                t.matches.append(m_obj)
                mtrack[mtrack_id] = len(r.matches)
                r.matches.append(m_obj)
            else:
                t.matches.append(r.matches[mtrack[mtrack_id]])

        t.eliminated[r.key] = eliminated_in

        # Locate any awards for this team...
        t.awards[r.key] = []
        for award in event['awards']:
            for recipient in award['recipient_list']:
                if recipient['team_number'] == t.number:
                    if recipient['awardee']:
                        t.awards[r.key].append(award['name'] + ' (to ' + recipient['awardee'] + ')')
                        if 'winner' in award['name'].lower():
                            t.elimiated = 'Win'
                    else:
                        t.awards[r.key].append(award['name'])

        r.teams.append(t)

def __frc_linalg_metric(r, base_func, metric_name):
    """
    __frc_linalg_metric(Regional, lambda) -> [number, number, number, number...]

    A base function for the various linear algebra metrics used in FRC scouting (OPR, CCWM, etc)

    base_func: base_func(red_score, blue_score, alliance ('red' or 'blue')) -> an int representing an alliance's 'score' for that match.
    """
    teams = r.teams
    matches = r.matches

    to_match_count = [[0 for t in teams] for t in teams]

    to_vert_matrix = [0 for t in teams]

    for m in matches:
        for t in m.red:
            if m.red_score != -1:
                for t2 in m.red:
                    to_match_count[teams.index(t)][teams.index(t2)] += 1
                to_vert_matrix[teams.index(t)] += base_func(m.red_score, m.blue_score, 'red')
        for t in m.blue:
            if m.blue_score != -1:
                for t2 in m.blue:
                    to_match_count[teams.index(t)][teams.index(t2)] += 1
                to_vert_matrix[teams.index(t)] += base_func(m.red_score, m.blue_score, 'blue')

    try:
        stats = np.linalg.solve(to_match_count, to_vert_matrix)
    except:
        print('WARN: Unsolveable OPR matrix for ' + r.key + '. Using least-square approximation.')
        # Disregard the (hopefully slight) error values
        stats = np.linalg.lstsq(to_match_count, to_vert_matrix)[0]

    stats = dict([(teams[i], opr) for i, opr in enumerate(stats.tolist())])

    return stats

def _calc_oprs(r):
    if len(r.matches):
        oprs = __frc_linalg_metric(r, lambda red, blue, alliance: red if alliance == 'red' else blue, 'OPR')
        r.oprs = oprs
        for t in r.teams:
            t.oprs[r.key] = oprs[t]
    else:
        r.oprs = {}
        for t in r.teams:
            t.oprs[r.key] = 0

def _calc_ccwms(r):
    if len(r.matches):
        ccwms = __frc_linalg_metric(r, lambda red, blue, alliance: red - blue if alliance == 'red' else blue - red, 'CCWM')
        r.ccwms = ccwms
        for t in r.teams:
            t.ccwms[r.key] = ccwms[t]
    else:
        r.ccwms = {}
        for t in r.teams:
            t.ccwms[r.key] = 0

def download_regional_basics(reg):
    reg_raw = cache_or_get_json(reg + 'info', bluealliance_download_file, '/event/' + str(reg))

    return Regional(reg_raw['key'], reg_raw['name'], reg_raw['short_name'], reg_raw['event_code'], reg_raw['year'], reg_raw['start_date'], reg_raw)


def bluealliance_download_file(path):
    conn = HTTPConnection(BLUEALLIANCE_DOMAIN)
    conn.request('GET', BASEPATH + path, headers=DEF_HEADERS)

    r = conn.getresponse()
    answer = r.read().decode('utf-8')

    return answer
