
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

def generate_match(prev_matches, teams):
    sorted_cands = weight_teams(prev_matches, teams)
    next_four = sorted_cands[:4]
    proposed_match = [x[0] for x in next_four]
    print proposed_match
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
