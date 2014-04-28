class Match:
    def __init__(self, id, red, blue, red_score, blue_score):
        self.red = red
        self.blue = blue
        self.red_score = red_score
        self.blue_score = blue_score
        self.id = id

    def to_json(self, t):
        return {'id': self.id, 'red': [r.number for r in self.red], 'blue':
            [b.number for b in self.blue], 'scout': t.number}

    def __eq__(self, m):
        if isinstance(m, Match):
            return m.id == self.id
        else:
            return False
    def __hash__(self):
        return self.id


def make_match(js):
    if js['id'] in Match._matches:
        return Match._matches[js['id']]
    else:
        return Match(js['id'], js['start_at'], [team.get_team(num) for num in js['red']], [team.get_team(num) for num in js['blue']])
