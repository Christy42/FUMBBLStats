import yaml
import pandas as pd


# TODO: Top x for each region in each category given
def get_spp(stats):
    return 1 * stats["completions"] + 2 * stats["casualties"] + 3 * stats["touchdowns"] + 5 * stats["mvps"]


def get_stat(numerator, denominator, stats):
    return 0.0 if int(stats[denominator]) == 0 else round(float(stats[numerator]) / float(stats[denominator]), 2)


def generate_stats(player_file, stats_file, team=False, region=False):
    with open(stats_file, "r") as stat_file:
        stats = yaml.safe_load(stat_file)
    with open(player_file, "r") as p_file:
        players = yaml.safe_load(p_file)
    for player in players:
        players[player]["spp"] = get_spp(players[player])
        for element in stats:
            if len(element) > 1:
                players[player][element[0] + "/" + element[1]] = get_stat(element[0], element[1], players[player])
                if element[0] in ["turns"]:
                    players[player][element[0] + "/" + element[1]] /= (16 * (1 + 10 * team))
                    players[player][element[0] + "/" + element[1]] = \
                        round(players[player][element[0] + "/" + element[1]], 2)
                if region:
                    players[player][element[0] + "/" + element[1]] /= players[player]["teams"]

    with open(player_file, "w") as p_file:
        yaml.safe_dump(players, p_file)


# TODO: Tidy this function up a lot, doing far too much.
# TODO: Make a get segmented dataframe section and a sort section?
def sort_players(stat_file, player_file, region_stats_file, pkl_folder,
                 n=3, team=False, pkl_file=False, region="overall"):
    with open(region_stats_file, "r") as file:
        region_line = yaml.safe_load(file)[region]
    region_line.update({"name": "League", "position": "", "skills": "", "team": ""})

    with open(stat_file, "r") as file:
        stats = yaml.safe_load(file)
    with open(player_file, "r") as file:
        players = yaml.safe_load(file)
    # stats = [["blocks", "turns"]]
    dataframe = pd.DataFrame(players).transpose()
    dataframe = dataframe[dataframe.loc[:, "division"] == region] if region != "overall" else dataframe
    values_req = {"games": 3, "turns": 30, "blocks": 10}
    for stat in stats:
        temp = dataframe.copy(deep=True)
        if len(stat) > 1 and stat[1] in ["games", "turns", "blocks"]:
            temp = temp[temp.loc[:, stat[1]] >= values_req[stat[1]] * (1 + team * 9 * (stat[1] != "games"))]

        if not team and len(stat) > 1:
            cols = ["name", "team", "position", "skills", stat[0] + "/" + stat[1],
                    stat[0], stat[1], "division", "team id"]
        elif not team:
            cols = ["name", "team", "position", "skills", stat[0], "division", "team id"]
        elif len(stat) > 1:
            cols = ["name",  stat[0] + "/" + stat[1], stat[0], stat[1], "division"]
        else:
            cols = ["name",  stat[0], "division"]
        temp = temp[cols]
        append_list = []
        for element in cols:
            append_list.append(region_line[element]) if element in region_line else append_list.append(-1)
        sort_stat = stat[0] if len(stat) == 1 else stat[0] + "/" + stat[1]
        sec_stat = stat[-1]
        temp_split = dict()
        temp_split["Good"] = temp.sort_values(by=[sort_stat, sec_stat], ascending=[False, False]).head(n)

        if not team:
            if stat[0] == "turns":
                temp["Secret Weapon"] = temp.apply(lambda row: "Secret Weapon" in row.skills, axis=1)
                temp = temp[temp.loc[:, "Secret Weapon"] == 0]
                del temp["Secret Weapon"]
            elif stat[0] == "blocks":
                temp["Bombardier"] = temp.apply(lambda row: "Bombardier" in row.skills, axis=1)
                temp = temp[temp.loc[:, "Bombardier"] == 0]
                del temp["Bombardier"]
            elif stat[0] == "casualties":
                temp["Chainsaw"] = temp.apply(lambda row: "Chainsaw" in row.skills, axis=1)
                temp = temp[temp.loc[:, "Chainsaw"] == 0]
                del temp["Chainsaw"]

        temp_split["Bad"] = temp.sort_values(by=[sort_stat, sec_stat], ascending=[True, False]).head(n)
        for style in ["Good", "Bad"]:
            temp_split[style].loc[-1] = append_list
            if len(stat) > 1:
                del temp_split[style][stat[0]]
                del temp_split[style][stat[1]]
            if not team:
                del temp_split[style]["skills"]
            if pkl_file:
                temp_split[style].to_pickle(pkl_folder + "/" + region + "/" +
                                            sort_stat.replace("/", "-") + team * "Team" + style + ".pkl")


def total(team_file, totals_file, stats_file):
    with open(team_file, "r") as file:
        team = yaml.safe_load(file)
    regions = {"overall": {}}
    for element in team:
        if team[element]["division"] not in regions:
            regions[team[element]["division"]] = {}
        for stat in team[element]:
            try:
                regions[team[element]["division"]][stat] = \
                    int(regions[team[element]["division"]].get(stat, 0)) + int(team[element][stat])
                regions["overall"][stat] = int(regions["overall"].get(stat, 0)) + int(team[element][stat])
            except (ValueError, TypeError):
                pass
        regions[team[element]["division"]]["teams"] = regions[team[element]["division"]].get("teams", 0) + 1
        regions["overall"]["teams"] = regions["overall"].get("teams", 0) + 1
    with open(totals_file, "w") as file:
        yaml.safe_dump(regions, file)
    generate_stats(totals_file, stats_file, team=True)


def sort_regions(stat_file, player_file, league_file, team_file, table, division_file):
    with open(division_file, "r") as div_file:
        divisions = yaml.safe_load(div_file)
    for region in ["overall"] + [divisions[reg]["name"] for reg in divisions]:
        print(region)
        sort_players(stat_file, player_file, league_file, table, pkl_file=True, region=region)
        sort_players(stat_file, team_file, league_file, table, team=True, pkl_file=True, region=region)
        create_league_tables(league_file, stat_file, table)


def create_league_tables(region_stats_file, stat_list, pkl_folder):
    with open(region_stats_file, "r") as file:
        region_line = yaml.safe_load(file)
    with open(stat_list, "r") as file:
        stats = yaml.safe_load(file)
    dataframe = pd.DataFrame(region_line).transpose()
    dataframe["name"] = dataframe.index
    for stat in stats:
        temp = dataframe.copy(deep=True)
        cols = ["name", stat[0]] if len(stat) == 1 else ["name", stat[0] + "/" + stat[1], stat[1]]
        temp = temp[cols]
        sort_stat = cols[1]
        sec_stat = stat[-1]
        temp = temp.sort_values(by=[sort_stat, sec_stat], ascending=[False, False])
        if len(stat) > 1:
            del temp[stat[1]]
        temp.to_pickle(pkl_folder + "/Leagues/" + sort_stat.replace("/", "-") + ".pkl")
