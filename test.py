
import collections

from blueflame import get_opponents

def invert(dictionary):
    new = collections.defaultdict(list)
    for k, v in dictionary.iteritems():
        new[v].append(k)
    return new

def keys_sorted_by_value(dictionary, reverse = False):
    s = sorted(dictionary, key=lambda key: dictionary[key], reverse = reverse)
    return s

prev_matches = [
    ['A', 'B', 'L', 'M'],
    ['A', 'R', 'S', 'T'],
    ['C', 'R', 'L', 'T'],
    ['C', 'B', 'S', 'M']
]

available_teams = set(['A', 'B', 'C', 'D', 'E'])

expected_best = set(['A', 'C', 'D', 'E'])

opps = {}
number_of_available_teams_not_faced = {}
number_of_available_teams_faced = {}
for tla in available_teams:
    team_opps_data = get_opponents(prev_matches, tla)

    faced = set(team_opps_data.keys())
    not_faced_count = len(available_teams - faced)
    faced_count = len(available_teams) - not_faced_count
    print tla, faced, not_faced_count
    number_of_available_teams_not_faced[tla] = not_faced_count
    number_of_available_teams_faced[tla] = faced_count

    opps[tla] = len(faced)

s = keys_sorted_by_value(opps)
best = set(s[:4])
print best

s = keys_sorted_by_value(number_of_available_teams_not_faced, reverse = True)
print 'not-faced:', number_of_available_teams_not_faced, s
best = set(s[:4])
print best

s = keys_sorted_by_value(number_of_available_teams_faced,)
print 'not-faced:', number_of_available_teams_faced, s
best = set(s[:4])
print best

print opps

assert best == expected_best, (best, expected_best)

