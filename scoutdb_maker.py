import scrape
import csv

from datetime import date

def main():
    year = date.today().year
    # Look back three years
    regs = scrape.download_regionals(range(year-6, year+1), True, True)

    rows = []

    writer = csv.writer(open('prescout_' + str(date.today()) + '.csv', 'w'))

    for r in regs:
        for t in r.teams:
            column = []
            column.append(str(t.number))
            column.append(t.nickname)
            column.append(t.location)
            # Lookup
            if r.year not in t.lookup_counter:
                t.lookup_counter[r.year] = 0
            column.append(str(r.year) + str(t.number) + ('a'*(t.lookup_counter[r.year]+1)))
            t.lookup_counter[r.year] += 1
            # Rookie year - we don't have data on this...
            column.append('N/A')
            column.append(r.short_name)
            column.append(str(r.year))
            if len(r.matches):
                column.append(t.eliminated[r.key])
                column.append(t.oprs[r.key])
                column.append(r.opr_loc_ranks.index(t)+1)
                column.append(r.opr_loc_percentiles[t])
                column.append(t.ccwms[r.key])
                column.append(r.ccwm_loc_ranks.index(t)+1)
                column.append(r.ccwm_loc_percentiles[t])
            else:
                column.append('N/A')
                column.append('N/A')
                column.append('N/A')
                column.append('N/A')
                column.append('N/A')
                column.append('N/A')
                column.append('N/A')
            if r.year == 2014:
                column.append(r.teleop_avgs[t])
                column.append(r.teleop_loc_ranks.index(t)+1)
                column.append(r.teleop_loc_percentiles[t])
                column.append(r.auto_avgs[t])
                column.append(r.auto_loc_ranks.index(t)+1)
                column.append(r.auto_loc_percentiles[t])
                column.append(r.foul_avgs[t])
                column.append(r.foul_loc_ranks.index(t)+1)
                column.append(r.foul_loc_percentiles[t])
            else:
                column.append('N/A')
                column.append('N/A')
                column.append('N/A')
                column.append('N/A')
                column.append('N/A')
                column.append('N/A')
                column.append('N/A')
                column.append('N/A')
                column.append('N/A')
            column.append('N/A')
            column.append('N/A')
            column.append('N/A')
            for award in t.awards[r.key]:
                column.append(award)
            rows.append(column)

    writer.writerows(rows)

if __name__ == '__main__':
    main()
