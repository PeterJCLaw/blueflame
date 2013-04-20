
import sys
import collections

TEAMS = [x.strip() for x in open('../match-scheduler/data/2013/teams-2013')]

MATCH_COUNT = 102
TEAMS_PER_MATCH = 4
# total appearances / teams => max appearances per team
MATCH_LIMIT = int(round(1.0 * MATCH_COUNT * TEAMS_PER_MATCH / len(TEAMS)))
print 'Match Count:', MATCH_LIMIT
print 'Team Count:', len(TEAMS)
print 'Teams Per Match:', TEAMS_PER_MATCH
print 'Match limit:', MATCH_LIMIT

def reverse(a_list):
    copy = a_list[:]
    copy.reverse()
    return copy

def invert(dictionary):
    new = collections.defaultdict(list)
    for k, v in dictionary.iteritems():
        new[v].append(k)
    return new

def keys_sorted_by_value(dictionary, reverse = False):
    s = sorted(dictionary, key=lambda key: dictionary[key], reverse = reverse)
    return s

def match_recently(matches, tla):
    """
    Returns how recently a team has had a match.
    High numbers mean the last match was a long time ago
    """
    i = 1
    for m in reverse(matches):
        if tla in m:
            return i
        # TODO: more than just addition?
        i += 1
    return float('inf')

def match_count(matches, tla):
    """
    Returns the number of matches a team is in.
    """
    i = 0
    for m in reverse(matches):
        if tla in m:
            i += 1
    return i

def get_opponents(matches, tla):
    c = collections.Counter()
    for match in matches:
        if tla in match:
            for other in match:
                c[other] += 1
    del c[tla]
    return c

def is_valid(match):
    # TODO: also check match counts in here?
    return len(set(match)) == TEAMS_PER_MATCH

def weight_teams(matches, teams):
    weighted_candidates = []

    for tla in teams:
        recent = match_recently(matches, tla)
        count = match_count(matches, tla)
        weight = (1.0 / recent) + count
        weighted_candidates.append((tla, weight))

    sorted_candidates = sorted(weighted_candidates, key = lambda x: x[1])
    #print sorted_candidates

    return sorted_candidates

def get_available_teams(weighted_teams):
    first_tla, first_weight = weighted_teams[0]
    print 'Lowest weighted:', first_tla, first_weight
    # TODO: investigate what happens when we adjust these limits
    top = first_weight + 2
    bottom  = first_weight - 2
    available = [x[0] for x in weighted_teams if x[1] < top and x[1] > bottom]
    if len(available) < TEAMS_PER_MATCH:
        # Add on the next N as well if there aren't enough
        more = weighted_teams[len(available):len(available)+TEAMS_PER_MATCH]
        available += [x[0] for x in more]
    print 'available:', available
    return available

def find_best_opponents(prev_matches, available_teams):
    available = set(available_teams)
    print available
    not_faced = {}
    for tla in available_teams:
        opps_raw = get_opponents(prev_matches, tla)
        all_faced = set(opps_raw.keys())
        not_faced_count = len(available - all_faced)
        not_faced[tla] = not_faced_count

    #print not_faced
    best = keys_sorted_by_value(not_faced)
    print 'Best opponents:', best
    return best[:4]

def generate_match(prev_matches, teams):
    weighted_teams = weight_teams(prev_matches, teams)
    print 'Complete weightings:', weighted_teams
    available = get_available_teams(weighted_teams)

    proposed_match = find_best_opponents(prev_matches, available)
    print 'Proposing:', proposed_match
    return proposed_match

if __name__ == '__main__':

    matches = [['GMR', 'MAI', 'BGR', 'CLY']]

    # We want to pick teams that haven't had a match recently,
    # And/or who haven't had very many matches

    for i in range(MATCH_COUNT):
        print '---------------------------'
        print 'Working on', i
        match = []
        while not is_valid(match):
            match = generate_match(matches, TEAMS)
        matches.append(match)

    opps = get_opponents(matches, 'GMR')

    print 'Done'

    with open('out', 'w') as f:
        for match in matches:
            print >> f, '|'.join(match)
