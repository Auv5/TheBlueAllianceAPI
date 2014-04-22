def get_team(number, name):
    t = Team._teams.get(number, None)
    if t:
        if not t.nickname and name:
            t.nickname = name
    else:
        t = Team(number, name)
        Team._teams[number] = t
    return t

class Team:
    _teams = {}

    def __init__(self, number, nickname):
        self.number = number
        self.id = number
        self.nickname = nickname
        # To be filled in download/calc methods
        self.location = ''
        self.regionals = []
        self.matches = []
        self.awards = {}
        self.eliminated = {}
        self.oprs = {}
        self.ccwms = {}
        self.teleop_avgs = {}
        self.auto_avgs = {}
        self.foul_avgs = {}
        # Statistics. Also filled in by a method in the download section
        self.opr_glob_ranks = {}
        self.ccwm_glob_ranks = {}
        self.opr_glob_percentiles = {}
        self.ccwm_glob_percentiles = {}
        self.teleop_glob_ranks = {}
        self.auto_glob_ranks = {}
        self.foul_glob_ranks = {}
        self.teleop_glob_percentiles = {}
        self.auto_glob_percentiles = {}
        self.foul_glob_percentiles = {}

        # Lookups go year + team# + (a*lookup_counter[year])
        self.lookup_counter = {}

        Team._teams[number] = self

    def attended(self, r):
        print(r['key'], self.regionals)
        return r['key'] in self.regionals

    def __str__(self):
        print('Team #' + self.number)

    def to_json(self):
        return self.number, self.nickname

    def __eq__(self, other):
        if isinstance(other, Team):
            return other.number == self.number
        else:
            return False

    def __hash__(self):
        return self.number
