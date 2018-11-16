import os
import requests
import yaml
import xml.etree.ElementTree as Et
import pandas as pd

from DataGrab import team_name


def get_matches(player_folder, team_folder, rerun_folder=None):
    b = requests.get("https://fumbbl.com/xml:group?id=3449&op=matches")
    text = Et.fromstring(b.text)
    performances, team_games = matches_in_division(text, rerun_folder)
    add_player_attribs(performances, player_folder)
    add_team_performances(performances, team_folder, team_games)
    next_page = text.find("nextPage").text
    count = 0
    while next_page:
        print(next_page)
        print(count)
        b = requests.get("https://fumbbl.com/xml:group?id=3449&op=matches&paging={}".format(next_page))
        text = Et.fromstring(b.text)
        performances, team_games = matches_in_division(text, rerun_folder)
        add_player_attribs(performances, player_folder)
        add_team_performances(performances, team_folder, team_games)
        try:
            next_page = text.find("nextPage").text
        except AttributeError:
            next_page = None
        count += 1


def matches_in_division(root_text, rerun_folder=None):
    matches = root_text.find("matches")
    teams_found = {}
    performances = []
    already_run = []
    if rerun_folder:
        with open(rerun_folder, "r") as rerun:
            already_run = yaml.safe_load(rerun)
    for match in matches:
        if match.attrib["id"] in already_run:
            # print("Not grabbing {} as it is already done or too late a round".format(match.attrib["id"]))
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


def add_player_attribs(performances, player_file):
    players = open_files("LongTerm", "Player")
    for element in performances:
        ident = element["player"]
        if ident not in players:
            name, star, skills, position = get_name(ident)
            ident = name if star else ident
            players[ident] = {"team": "Star Player" if star else element["team"]["id"],
                              "name": name, "position name": position, "skills": skills, "team id": element["team id"]}\
                if ident not in players else players[ident]
        print(ident)
        for stat in element:
            if stat not in ["player", "team", "team id"]:
                try:
                    players[ident][stat] = int(players[ident].get(stat, 0)) + int(element.get(stat, 0))
                except ValueError:
                    players[ident][stat] = int(players[ident].get(stat, 0))
        players[ident]["games"] = int(players[ident].get("games", 0)) + 1
    print("YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
    write_file(players, "LongTerm", "Player")


def open_files(folder, base):
    dictionary = {}
    for filename in os.listdir(folder):
        if base in filename:
            with open(folder + "//" + filename, "r") as file:
                dictionary.update(yaml.safe_load(file))
    return dictionary


def write_file(dictionary, folder, base):
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    count = 1
    print_dict = []
    file_number = 0
    print(dictionary)
    for element in dictionary:
        if count % 500 == 0:
            file_number += 1
        try:
            print_dict[file_number].update({element: dictionary[element]})
        except IndexError:
            print_dict.append({})
        count += 1
    print("VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV")
    print(file_number)
    for i in range(file_number + 1):
        # print("printing")
        with open(folder + "//" + base + str(i) + ".yaml", "w+") as file:
            yaml.safe_dump(print_dict[i], file)


def add_team_performances(performances, team_file, team_games):
    teams_accessed = []
    with open(team_file, "r") as t_file:
        teams = yaml.safe_load(t_file)
    for player in performances:
        if player["team id"] not in teams:
            teams[player["team id"]] = {"name": player["team"]["id"]}
        teams_accessed.append(player["team id"])
        for stat in player:
            if stat not in ["name", "team", "team id", "player"]:
                try:
                    teams[player["team id"]][stat] = int(teams[player["team id"]].get(stat, 0)) + int(player[stat])
                except ValueError:
                    teams[player["team id"]][stat] = int(teams[player["team id"]].get(stat, 0))
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


# get_matches("LongTerm//Player.yaml", "LongTerm//Team.yaml", "LongTerm//run_file.yaml")
