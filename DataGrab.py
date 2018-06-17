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
# TODO: Test the already run section.  Just don't clear all data first dumbass
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
            print(match.attrib["id"])
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
    name = root.find("name").text
    return name


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


def cycle_divisions(division_folder, player_folder, team_folder, rerun_folder=None):
    with open(division_folder, "r") as file:
        divisions = yaml.safe_load(file)
    for element in divisions:
        print(divisions[element], element)
        performances, team_games = matches_in_division(divisions[element]["group"], element, rerun_folder)
        add_player_attribs(performances, player_folder, divisions[element]["name"])
        add_team_performances(performances, team_folder, divisions[element]["name"], team_games)


def race_check(team_folder):
    with open(team_folder, "r") as file:
        teams = yaml.safe_load(file)
    for team in teams:
        if "race" not in teams[team]:
            race_text = requests.get("https://fumbbl.com/api/team/get/{}/xml".format(str(team)))
            root = Et.fromstring(race_text.text)
            roster_id = root.find("roster")
            roster = roster_id.find("name").text
            teams[team]["race"] = roster
    with open(team_folder, "w") as file:
        yaml.safe_dump(teams, file)


def kill_list_grab(kill_list_sheet, team_folder):
    with open(kill_list_sheet, "r") as file:
        kills = yaml.safe_load(file)
    if kills == {}:
        with open(team_folder, "r") as file:
            teams = yaml.safe_load(file)
        kills = {team: [] for team in teams}
    dead_players = {}
    for team in kills:
        team_xml = requests.get("https://fumbbl.com/xml:team?id={}&past=1".format(team))
        root = Et.fromstring(team_xml.text)

        print(team)
        for player in root:
            if player.attrib.get("status", "") == "Dead":
                dead_players.update({team: player.attrib["id"]})
            # print(players.find["injuryList"])
    # TODO: Grab data for each tournie.
    # Just grab all of the text
    # TODO: Find out where each player drops.
    # Maybe some sort of list of players used in each round? But need the opposition teams as well


def set_player_numbers(region_file, player_file):
    with open(player_file, "r") as players:
        player_list = yaml.safe_load(players)
    with open(region_file, "r") as region_list:
        regions = yaml.safe_load(region_list)
    for region in regions:
        regions[region]["players"] = 0
    for player in player_list:
        if player_list[player]["division"] != "":
            regions[player_list[player]["division"]]["players"] += 1
    with open(region_file, "w") as region_list:
        yaml.safe_dump(regions, region_list)


# kill_list_grab("player_list//kills.yaml", "player_list//Team.yaml")
set_player_numbers("player_list//Totals.yaml", "player_list//Player.yaml")

# reset_file("player_list/Player.yaml")
# reset_file("player_list/Team.yaml")
# get_name(11103735)
# cycle_divisions("match_list/divisions.yaml", "player_list/Player.yaml", "player_list/Team.yaml",
#                 rerun_folder="match_list/run_file.yaml")
# race_check("player_list/Team.yaml")
