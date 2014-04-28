import models.match
import models.team

class Question:
    def __init__(self, qid, label, qtype, offers, optional):
        self.qid = qid
        self.label = label
        self.qtype = qtype
        self.offers = offers
        self.optional = optional

    def to_small_json(self):
        return {'id': self.qid, 'label': self.label, 'type': self.qtype, 'offers': self.offers, 'optional': self.optional}


class MatchQuestion(Question):
    def __init__(self, qid, label, qtype, offers, optional, answers=None):
        Question.__init__(self, qid, label, qtype, offers, optional)
        if answers is None:
            self.answers = {}
        else:
            self.answers = {models.team.get_team(int(key)): {models.match.get_match(int(k)):
                                v for k, v in value.items()} for key, value in answers.items()}

    def add_answer(self, team, match, answer):
        if match not in self.answers:
            self.answers[team] = {}
        self.answers[team][match] = answer

    def get(self, match, team):
        return self.answers[team][match]['value']

    def has(self, match, team):
        return team in self.answers and match in self.answers[team]

    def to_json(self):
        return {'id': self.qid, 'label': self.label, 'type': self.qtype, 'offers': self.offers, 'optional': self.optional,
                        'answers': {key.id: {k.id: v for k, v in value.items()} for key, value in
                                    self.answers.items()},
                        '__type': 'match'}

class TeamQuestion(Question):
    def __init__(self, qid, label, qtype, offers, optional, answers=None):
        Question.__init__(self, qid, label, qtype, offers, optional)
        if answers is None:
            self.answers = {}
        else:
            self.answers = {models.team.get_team(int(key)): value for key, value in answers.items()}

    def add_answer(self, team, answer):
        self.answers[team] = answer

    def get(self, t):
        return self.answers[t]['value']

    def has(self, t):
        return t in self.answers

    def to_json(self):
        return {'id': self.qid, 'label': self.label, 'type': self.qtype, 'offers': self.offers, 'optional': self.optional,
                        'answers': {key.id: value for key, value in self.answers.items()},
                        '__type': 'team'}
