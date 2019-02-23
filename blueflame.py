#!/usr/bin/env python

import sys
import logging
import argparse
import collections

LOGGER = logging.getLogger(__name__)

TEAMS_PER_MATCH = 4

def invert(dictionary):
    new = collections.defaultdict(list)
    for k, v in dictionary.iteritems():
        new[v].append(k)
    return new

def keys_sorted_by_value(dictionary, reverse = False):
    s = sorted(dictionary, key=lambda key: dictionary[key], reverse = reverse)
    return s

def match_recently(matches, team_id):
    """
    Returns how recently a team has had a match.
    High numbers mean the last match was a long time ago
    """
    i = 1
    for match in reversed(matches):
        if team_id in match:
            return i
        # TODO: more than just addition?
        i += 1
    return float('inf')

def match_count(matches, team_id):
    """
    Returns the number of matches a team is in.
    """
    i = sum(team_id in m for m in matches)
    return i

def get_opponents(matches, team_id):
    c = collections.Counter()
    for match in matches:
        if team_id in match:
            for other in match:
                c[other] += 1
    del c[team_id]
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

    for team_id in teams:
        # high 'recent' means the team is due a match
        recent = match_recently(matches, team_id)
        # low 'count' means the team is due a match
        count = match_count(matches, team_id)
        # low 'weight' means the team is due a match
        weight = (4.0 / recent) + count
        weighted_candidates.append((team_id, weight))

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
    for team_id in available_teams:
        opps_raw = get_opponents(prev_matches, team_id)
        all_faced = set(opps_raw.keys())
        not_faced_count = len(available - all_faced)
        not_faced[team_id] = not_faced_count

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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-m',
        '--num-matches',
        help="The overall number of matches",
        type=int,
        required=True,
    )
    parser.add_argument(
        '-t',
        '--num-teams',
        help="The overall number of teams",
        type=int,
        required=True,
    )
    parser.add_argument(
        '--teams-per-match',
        help="The number of teams per match (default: %(default)d)",
        type=int,
        default=TEAMS_PER_MATCH,
    )
    parser.add_argument(
        '-o',
        '--output-file',
        type=argparse.FileType(mode='w'),
        default=sys.stdout,
    )
    parser.add_argument(
        '--log-level',
        type=logging.getLevelName,
        default='INFO',
    )
    return parser.parse_args()


def main(num_matches, num_teams, teams_per_match):
    global TEAMS_PER_MATCH
    TEAMS_PER_MATCH = teams_per_match

    # total appearances / teams => max appearances per team
    match_limit = int(round(1.0 * num_matches * TEAMS_PER_MATCH / num_teams))

    teams = [str(x) for x in range(num_teams)]

    LOGGER.info("Max number of matches a team could have: %d", match_limit)

    # Bootstrap by selecting the first (N % teams_per_match) teams in order
    bootstrap_teams = num_teams - (num_teams % teams_per_match)
    matches = [
        teams[offset:offset + teams_per_match]
        for offset in range(0, bootstrap_teams, teams_per_match)
    ]

    # We want to pick teams that haven't had a match recently,
    # And/or who haven't had very many matches

    for i in range(num_matches):
        LOGGER.debug("---------------------------")
        LOGGER.debug("Working on %d", i)
        match = []
        while not is_valid(match):
            match = generate_match(matches, teams)
        matches.append(match)

    opps = get_opponents(matches, 'GMR')

    LOGGER.debug("Done")

    return matches

if __name__ == '__main__':
    args = parse_args()

    logging.basicConfig(level=args.log_level, stream=sys.stderr, format='%(message)s')

    matches = main(
        num_matches=args.num_matches,
        num_teams=args.num_teams,
        teams_per_match=args.teams_per_match,
    )

    for match in matches:
        args.output_file.write('|'.join(match))
        args.output_file.write('\n')
