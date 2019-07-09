import requests
import yaml
import xml.etree.ElementTree as Et


def matches_in_division(group_number, division_number, round_no, rerun_folder=None):
    # Make the call to get the games
    division = requests.get("https://fumbbl.com/xml:group?id={}&op=matches&t={}".format(group_number, division_number))
    print("https://fumbbl.com/xml:group?id={}&op=matches&t={}".format(group_number, division_number))
    # Data comes in as an xml, deconstruct it using the cml library
    root = Et.fromstring(division.text)
    matches = root.find("matches")
    teams_found = {}
    performances = []
    already_run = []
    # If we have already gotten information on this match we don't check again
    if rerun_folder:
        with open(rerun_folder, "r") as rerun:
            already_run = yaml.safe_load(rerun)
    for match in matches:
        if match.attrib["id"] in already_run or match.attrib["round"] > round_no:
            print("Not grabbing {} as it is already done or too late a round".format(match.attrib["id"]))
            continue
        already_run.append(match.attrib["id"])
        # We have home and away teams
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


# Make a call to the website to get the name of the team using the team's id.
def team_name(team_id):
    team = requests.get("https://fumbbl.com/xml:team?id={}".format(str(team_id)))
    root = Et.fromstring(team.text)
    name = root.find("name").text
    return name


# Find the details of an individual player
def add_player_attribs(performances, player_file, div):
    with open(player_file, "r") as file:
        players = yaml.safe_load(file)
    for element in performances:
        ident = element["player"]
        if ident not in players:
            name, star, skills, position = get_name(ident)
            ident = name if star else ident
            players[ident] = {"team": "Star Player" if star else element["team"]["id"], "division": "" if star else div,
                              "name": name, "position name": position, "skills": skills, "team id": element["team id"]} \
                if ident not in players else players[ident]
        for stat in element:
            if stat not in ["player", "team", "team id"]:
                players[ident][stat] = int(players[ident].get(stat, 0)) + int(element[stat])
        players[ident]["games"] = int(players[ident].get("games", 0)) + 1
    # Save data to the player file
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


def cycle_divisions(division_folder, player_folder, team_folder, round_no, rerun_folder=None):
    with open(division_folder, "r") as file:
        divisions = yaml.safe_load(file)
    # Run through the divisions we want to check
    for element in divisions:
        print(divisions[element], element)
        performances, team_games = matches_in_division(divisions[element]["group"], element, round_no, rerun_folder)
        add_player_attribs(performances, player_folder, divisions[element]["name"])
        add_team_performances(performances, team_folder, divisions[element]["name"], team_games)


# Teams can be of varying fantasy races, this checks which one it is
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


def kill_list_grab(division_folder, kill_list_sheet, team_folder, player_file):
    with open(player_file, "r") as players_file:
        players = yaml.safe_load(players_file)
    played = get_games_played(division_folder)
    print("played")

    with open(kill_list_sheet, "r") as file:
        kills = yaml.safe_load(file)

    if kills == {}:
        with open(team_folder, "r") as file:
            teams = yaml.safe_load(file)
        kills = {team: [] for team in teams}
    total_kill_list = []
    for team in kills:
        for kill in kills[team]:
            total_kill_list += kill
    dead_players = {}
    killed_list = []
    for team in kills:
        team_xml = requests.get("https://fumbbl.com/xml:team?id={}&past=1".format(team))
        root = Et.fromstring(team_xml.text)

        for player in root:
            if player.attrib.get("status", "") == "Dead" and str(player.attrib["id"]) not in total_kill_list:
                if team not in dead_players:
                    dead_players.update({team: [player.attrib["id"]]})
                else:
                    dead_players[team].append(player.attrib["id"])
                killed_list.append(player.attrib["id"])
    kill_sub_list = {}
    for player in killed_list:
        # TODO: Need to ensure player is not already in the list
        # I guess need to do a big dict for them and then look it up as I go???
        if player in []:
            continue
        for round_no in range(1, len(played) + 1):
            for team in played[str(round_no)]:
                if str(player) in played[str(round_no)][team]:
                    if player in players:
                        kill_sub_list.update({player: [team, players[player]["icon"], players[player]["division"]]})

    for player in kill_sub_list:

        if kill_sub_list[player][0] not in kills:
            kills[kill_sub_list[player][0]] = []
        kills[kill_sub_list[player][0]].append([player, kill_sub_list[player][1], kill_sub_list[player][2]])
    print(kills)
    with open(kill_list_sheet, "w") as file:
        yaml.safe_dump(kills, file)


def get_games_played(division_folder):
    with open(division_folder, "r") as file:
        divisions = yaml.safe_load(file)
    total = {}
    for element in divisions:
        value = requests.get("https://fumbbl.com/xml:group?id={}&op=matches&t={}".
                             format(divisions[element]["group"], element))
        root = Et.fromstring(value.text)
        matches = root.find("matches")

        for match in matches:
            round_no = match.attrib["round"]
            if round_no not in total:
                total[match.attrib["round"]] = {}
            home, away = 0, 0
            match_players = {"home": [], "away": []}
            for element_m in match:

                if element_m.tag in ["home", "away"]:
                    for player in element_m.find("performances"):

                        if element_m.tag == "home":
                            home = element_m.attrib["id"]
                            match_players["home"].append(player.attrib["player"])
                        else:
                            away = element_m.attrib["id"]
                            match_players["away"].append(player.attrib["player"])
            total[match.attrib["round"]][home] = match_players["away"]
            total[match.attrib["round"]][away] = match_players["home"]
        # print("total")
        # print(total)
    return total


def set_player_numbers(region_file, player_file):
    with open(player_file, "r") as players:
        player_list = yaml.safe_load(players)
    with open(region_file, "r") as region_list:
        regions = yaml.safe_load(region_list)
    for region in regions:
        regions[region]["players"] = 0
    for player in player_list:
        if player_list[player]["division"] != "":
            if player_list[player]["division"] not in regions:
                regions[player_list[player]["division"]] = {}
                regions[player_list[player]["division"]]["players"] = 0
            regions[player_list[player]["division"]]["players"] += 1
    with open(region_file, "w") as region_list:
        yaml.safe_dump(regions, region_list)


def set_player_icons(player_file, icon_file):
    with open(player_file, "r") as players:
        player_list = yaml.safe_load(players)
    with open(icon_file, "r") as icons:
        icon_list = yaml.safe_load(icons)
    for player in player_list:
        print(player)
        try:
            if "icon" not in player_list[player]:
                player_root = requests.get("https://fumbbl.com/api/player/get/" + str(player) + "/xml").text
                root = Et.fromstring(player_root)
                pos = root.find("position")

                player_list[player]["position"] = pos.attrib["id"]
                print()
                print(player)
                print(pos.attrib["id"])
                player_list[player]["icon"] = icon_list[int(pos.attrib["id"])]
        except (AttributeError, Et.ParseError):
            pass
    with open(player_file, "w") as players:
        yaml.safe_dump(player_list, players)


def set_player_positions(player_file):
    with open(player_file, "r") as players:
        player_list = yaml.safe_load(players)
    for player in player_list:
        if "position name" not in player_list[player]:
            try:
                text_val = requests.get("https://fumbbl.com/api/player/get/" + str(player) + "/xml").text
                print(text_val)
                print("https://fumbbl.com/api/player/get/{}".format(player))
                root = Et.fromstring(text_val)
                pos = root.find("position")
                print(pos.find("name").text)
                player_list[player]["position name"] = pos.find("name").text
            except (Et.ParseError, AttributeError):
                player_list[player]["position name"] = "Star Player"

    with open(player_file, "w") as players:
        yaml.safe_dump(player_list, players)

# set_player_positions("player_list//Player.yaml")
