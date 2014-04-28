class Regional:
    def __init__(self, key, name, short_name, event_code, year, start_date, raw):
        self.key = key
        self.name = name
        self.short_name = short_name
        self.event_code = event_code
        self.year = int(year)
        self.start_date = start_date
        self.raw = raw
        # To be filled in download/calc methods
        self.teams = []
        self.matches = []
        self.oprs = {}
        self.ccwms = {}
        self.teleop_avgs = {}
        self.auto_avgs = {}
        self.foul_avgs = {}
        self.opr_loc_ranks = []
        self.ccwm_loc_ranks = []
        self.opr_loc_percentiles = {}
        self.ccwm_loc_percentiles = {}
        self.teleop_loc_ranks = []
        self.auto_loc_ranks = []
        self.foul_loc_ranks = []
        self.teleop_loc_percentiles = {}
        self.auto_loc_percentiles = {}
        self.foul_loc_percentiles = {}
