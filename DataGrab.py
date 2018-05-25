import requests
import yaml
import xml.etree.ElementTree as Et

from utility_func import reset_file


# TODO: Use the dang group page instead of match pages to cut down on api requests
# &paging= gives second page.  Number from next page field on the first page
# TODO: Separate code to generate the all time greats by running through each player stats in the league
# TODO: Give each player a region as they come in, for old ones just check which page they are on - stars get blank
# Just get a list of all players in each page.  Go through them and assign appropriately - get new ones first
# TODO: Use this for historical stats.  Use Team.yaml for all team ids
def matches_in_division(group_number, division_number, rerun_folder=None):
    division = requests.get("https://fumbbl.com/xml:group?id={}&op=matches&t={}".format(group_number, division_number))
    root = Et.fromstring(division.text)
    matches = root.find("matches")
    teams_found = {}
    performances = []
    already_run = []
    if rerun_folder:
        with open(rerun_folder, "r") as rerun:
            already_run = yaml.safe_load(rerun)
    for match in matches:
        if match.attrib["id"] in already_run:
            continue
        already_run.append(match.attrib["id"])
        for element in ["home", "away"]:
            section = match.find(element)
            team_id = section.attrib["id"]
            if team_id not in teams_found:
                teams_found[team_id] = {"id": team_name(team_id), "games": 0}
            teams_found[team_id]["games"] += 1
            name = teams_found[team_id]
            team_perf = section.find("performances")
            for child in team_perf:
                individual = child.attrib
                individual.update({"team": name, "team id": team_id})
                performances.append(individual)
    if rerun_folder:
        with open(rerun_folder, "w") as file:
            yaml.safe_dump(already_run, file)
    return performances, teams_found


def team_name(team_id):
    team = requests.get("https://fumbbl.com/xml:team?id={}".format(str(team_id)))
    root = Et.fromstring(team.text)
    team_name = root.find("name").text
    return team_name


# matches_in_division(3449, 44811, "")
def get_match(match_number):
    performances = []
    match_details = requests.get("https://fumbbl.com/xml:matches?m=" + str(match_number)).text
    root = Et.fromstring(match_details)
    match = root.find("match")
    for element in ["home", "away"]:
        section = match.find(element)
        team_id = section.attrib["id"]
        name = section.find("name").text
        team_perf = section.find("performances")
        for child in team_perf:
            individual = child.attrib
            individual.update({"team": name})
            individual.update({"team id": team_id})
            performances.append(individual)
    return performances


def add_player_attribs(performances, player_file, div):
    with open(player_file, "r") as file:
        players = yaml.safe_load(file)
    for element in performances:
        ident = element["player"]
        if ident not in players:
            name, star, skills, position = get_name(ident)
            ident = name if star else ident
            players[ident] = {"team": "Star Player" if star else element["team"]["id"], "division": "" if star else div,
                              "name": name, "position": position, "skills": skills, "team id": element["team id"]} \
                if ident not in players else players[ident]
        for stat in element:
            if stat not in ["player", "team", "team id"]:
                players[ident][stat] = int(players[ident].get(stat, 0)) + int(element[stat])
        players[ident]["games"] = int(players[ident].get("games", 0)) + 1
    with open(player_file, "w") as file:
        yaml.safe_dump(players, file)


def add_team_performances(performances, team_file, division, team_games):
    teams_accessed = []
    with open(team_file, "r") as t_file:
        teams = yaml.safe_load(t_file)
    for player in performances:
        if player["team id"] not in teams:
            teams[player["team id"]] = {"name": player["team"]["id"], "division": division}
        teams_accessed.append(player["team id"])
        for stat in player:
            if stat not in ["name", "team", "team id", "player"]:
                teams[player["team id"]][stat] = int(teams[player["team id"]].get(stat, 0)) + int(player[stat])
    for team in set(teams_accessed):
        teams[team]["games"] = teams[team].get("games", 0) + team_games[team]["games"]
    with open(team_file, "w") as file:
        yaml.safe_dump(teams, file)


def get_name(player_id):
    print("https://fumbbl.com/api/player/get/" + str(player_id) + "/xml")
    player_details = requests.get("https://fumbbl.com/api/player/get/" + str(player_id) + "/xml").text
    root = Et.fromstring(player_details)
    star = True if int(root.find("number").text) >= 90 else False
    pos = root.find("position")
    position = pos.find("name").text
    base_skills = []
    section = root.find("skills")
    for child in section:
        base_skills.append(child.text)
    return root.find("name").text, star, base_skills, position


def cycle_matches(match_files, player_folder, team_folder, run_list=None):
    finished = []
    if run_list:
        with open(run_list, "r") as run_file:
            finished = yaml.safe_load(run_file)
    with open(match_files, "r") as file:
        matches = yaml.safe_load(file)
    count = 0
    for match in set(matches):
        if match not in finished:
            count += 1
            perf = get_match(match)
            add_player_attribs(perf, player_folder, "")
            add_team_performances(perf, team_folder)


def cycle_divisions(division_folder, player_folder, team_folder, rerun_folder=None):
    with open(division_folder, "r") as file:
        divisions = yaml.safe_load(file)
    for element in divisions:
        print(divisions[element], element)
        performances, team_games = matches_in_division(divisions[element]["group"], element, rerun_folder)
        add_player_attribs(performances, player_folder, divisions[element]["name"])
        add_team_performances(performances, team_folder, divisions[element]["name"], team_games)
# get_match(3986223)
# get_name(4697130)
# reset_file("player_list/Player.yaml")
# reset_file("player_list/Team.yaml")
# cycle_matches("match_list/WILSeason48.yaml", "player_list/Player.yaml", "player_list/Team.yaml")
# get_name(11103735)
# cycle_divisions("match_list/divisions.yaml", "player_list/Player.yaml", "player_list/Team.yaml")
