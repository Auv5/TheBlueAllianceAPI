import _util

class Regional(object):
    ## The "base" variables to download. If someone requests one of these, they most likely
    ## want the rest of them, and they're not hard or expensive to get.
    _var_access_base = ['name', 'short_name', 'event_code', 'event_type_string',
                       'event_type', 'year', 'location', 'official', 'teams', 'matches']
    _var_access_matches = 'matches'
    _var_access_teams = 'teams'
    _var_access_stats = ['oprs', 'ccwms', 'dprs']

    
    def __init__(self, key):
        """
        Initializes a regional object. This does not download the regional data.
        Downloads are done as-needed when properties are accessed.
        """
        self._key = key
        self._base_dl = False
        self._stats_dl = False
        self._match_dl = False
        self._team_dl = False

    def _complete_base(self):
        """
        An internal method to download and map all of the basic data about an event.
        """
        base_data = _util.tba_download_file('/event/' + _key)

        # Extract all the information we need from the download
        for s in Regional._var_access_base:
            setattr(self, s, base_data[s])
        
        self._base_dl = True
    

    def __getattr__(self, name):
        if name in Regional._var_access_base:
            if not object.__getattribute__(self, '_base_dl'):
                _complete_base()
            return object.__getattribute__(self, name)
        elif name in Regional._var_access_stats:
            if not object.__getattribute__(self, '_stats_dl'):
                _complete_stats()
            return object.__getattribute__(self, name)
        elif name is Regional._var_access_matches:
            if not object.__getattribute__(self, '_match_dl'):
                _complete_matches()
            return object.__getattribute__(self, name)
        elif name is Regional._var_access_teams:
            if not object.__getattribute__(self, '_team_dl'):
                _complete_teams()
            return object.__getattribute__(self, name)
        else:
            # It's nothing we need to dynamically download.
            return object.__getattribute__(self, name)
