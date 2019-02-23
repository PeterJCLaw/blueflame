#!/usr/bin/env python

import sys
import logging
import collections

LOGGER = logging.getLogger(__name__)

NUM_TEAMS = 9
TEAMS = [str(x) for x in range(NUM_TEAMS)]

MATCH_COUNT = 102
TEAMS_PER_MATCH = 4
# total appearances / teams => max appearances per team
MATCH_LIMIT = int(round(1.0 * MATCH_COUNT * TEAMS_PER_MATCH / len(TEAMS)))


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
    for match in reversed(matches):
        if tla in match:
            return i
        # TODO: more than just addition?
        i += 1
    return float('inf')

def match_count(matches, tla):
    """
    Returns the number of matches a team is in.
    """
    i = sum(tla in m for m in matches)
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
    """
    Return a list of teams sorted by whether they should have a match soon.

    Teams most due a match are at the start of the list

    Reasons a team _shouldn't_ have match soon are:
     * they have had one recently
     * they have already had lots of matches
    """
    weighted_candidates = []

    for tla in teams:
        # high 'recent' means the team is due a match
        recent = match_recently(matches, tla)
        # low 'count' means the team is due a match
        count = match_count(matches, tla)
        # low 'weight' means the team is due a match
        weight = (4.0 / recent) + count
        weighted_candidates.append((tla, weight))

    sorted_candidates = sorted(weighted_candidates, key = lambda x: x[1])
    #print sorted_candidates

    return sorted_candidates

def get_available_teams(weighted_teams):
    first_tla, first_weight = weighted_teams[0]
    LOGGER.debug("Lowest weighted: %s %s", first_tla, first_weight)
    # TODO: investigate what happens when we adjust these limits
    top = first_weight + 2
    bottom  = first_weight - 2
    available = [x[0] for x in weighted_teams if x[1] < top and x[1] > bottom]
    if len(available) < TEAMS_PER_MATCH:
        # Add on the next N as well if there aren't enough
        more = weighted_teams[len(available):len(available)+TEAMS_PER_MATCH]
        available += [x[0] for x in more]
    LOGGER.debug("available: %s", available)
    return available

def find_best_opponents(prev_matches, available_teams):
    available = set(available_teams)
    LOGGER.debug(available)
    not_faced = {}
    for tla in available_teams:
        opps_raw = get_opponents(prev_matches, tla)
        all_faced = set(opps_raw.keys())
        not_faced_count = len(available - all_faced)
        not_faced[tla] = not_faced_count

    #print not_faced
    best = keys_sorted_by_value(not_faced)
    LOGGER.debug("Best opponents: %s", best)
    return best[:4]

def generate_match(prev_matches, teams):
    weighted_teams = weight_teams(prev_matches, teams)
    LOGGER.debug("Complete weightings: %s", weighted_teams)
    available = get_available_teams(weighted_teams)

    proposed_match = find_best_opponents(prev_matches, available)
    LOGGER.debug("Proposing: %s", proposed_match)
    return proposed_match

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(message)s')

    LOGGER.info("Match Count: %d", MATCH_LIMIT)
    LOGGER.info("Team Count: %d", len(TEAMS))
    LOGGER.info("Teams Per Match: %d", TEAMS_PER_MATCH)
    LOGGER.info("Match limit: %d", MATCH_LIMIT)

    matches = [TEAMS[:4]]

    # We want to pick teams that haven't had a match recently,
    # And/or who haven't had very many matches

    for i in range(MATCH_COUNT):
        LOGGER.debug("---------------------------")
        LOGGER.info("Working on %d", i)
        match = []
        while not is_valid(match):
            match = generate_match(matches, TEAMS)
        matches.append(match)

    opps = get_opponents(matches, 'GMR')

    LOGGER.info("Done")

    with open('out', 'w') as f:
        for match in matches:
            print >> f, '|'.join(match)
