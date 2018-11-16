import pandas as pd
import yaml
import os


def generate_stats(player_folder, stats_file, team=False, region=False):
    with open(stats_file, "r") as stat_file:
        stats = yaml.safe_load(stat_file)
    print(stats)
    for player_file in os.listdir(player_folder):
        if ("Player" in player_file and team is False) or ("Team" in player_file and team):
            with open(player_folder + "//" + player_file, "r") as p_file:
                players = yaml.safe_load(p_file)
            for player in players:
                players[player]["spp"] = get_spp(players[player])
                for element in stats:
                    if len(element) > 1:
                        print(element)
                        players[player][element[0] + "/" + element[1]] = get_stat(element[0], element[1], players[player])
                        if element[0] in ["turns"]:
                            players[player][element[0] + "/" + element[1]] /= (16 * (1 + 10 * team))
                            players[player][element[0] + "/" + element[1]] = \
                                round(players[player][element[0] + "/" + element[1]], 2)
                        if region and element[0] in ["turns"] and False:
                            players[player][element[0] + "/" + element[1]] /= players[player]["teams"]
                            players[player][element[0] + "/" + element[1]] = \
                                round(players[player][element[0] + "/" + element[1]], 2)
            with open(player_file, "w") as p_file:
                yaml.safe_dump(players, p_file)


#                         Need to Redo ##################################################################
def get_spp(stats):
    return 1 * stats["completions"] + 2 * stats["casualties"] + 3 * stats["touchdowns"] + 5 * stats["mvps"]


def get_stat(numerator, denominator, stats):
    return 0.0 if int(stats[denominator]) == 0 else round(float(stats[numerator]) / float(stats[denominator]), 2)


def sort_regions(stat_file, player_file, league_file, team_file, table):
    sort_players(stat_file, player_file, league_file, table, pkl_file=True, region="overall")
    sort_players(stat_file, team_file, league_file, table, team=True, pkl_file=True, region="overall")
    create_league_tables(league_file, stat_file, table)


# TODO: Tidy this function up a lot, doing far too much.
# TODO: Make a get segmented dataframe section and a sort section?
def sort_players(stat_file, player_folder, pkl_folder, n=3, team=False, pkl_file=False, region="overall"):
    with open(stat_file, "r") as file:
        stats = yaml.safe_load(file)
    # TODO: Need to amalgamate all the player files into one
    players = {}
    for player_file in os.listdir(player_folder):
        if (team and "Team" in player_file) or (team is False and "Player" in player_file):
            with open(player_file, "r") as file:
                players.update(yaml.safe_load(file))

    dataframe = pd.DataFrame(players).transpose()

    values_req = {"games": 3, "turns": 30, "blocks": 10}
    for stat in stats:
        temp = dataframe.copy(deep=True)
        if len(stat) > 1 and stat[1] in ["games", "turns", "blocks"]:
            temp_2 = temp[temp.loc[:, stat[1]] >= values_req[stat[1]] * (1 + team * 9 * (stat[1] != "games"))]
        if len(temp_2) != 0:
            temp = temp_2
        if not team and len(stat) > 1:
            cols = ["name", "team", "position name", "skills", stat[0] + "/" + stat[1],
                    stat[0], stat[1], "team id"]
        elif not team:
            cols = ["name", "team", "position name", "skills", stat[0], "team id"]
        elif len(stat) > 1:
            cols = ["name",  stat[0] + "/" + stat[1], stat[0], stat[1]]
        else:
            cols = ["name",  stat[0]]
        temp = temp[cols]
        append_list = []

        sort_stat = stat[0] if len(stat) == 1 else stat[0] + "/" + stat[1]
        sec_stat = stat[-1]
        temp_split = dict()

        temp_split["Good"] = temp.sort_values(by=[sort_stat, sec_stat], ascending=[False, False]).head(n)

        if not team and len(temp) > 0:
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


# TODO: player file will need to reference multiple files, team we can do  total stat as before?
# TODO: Remove divisions as not relevant
# TODO:  Deal with the fact that turns not always a stat? Remove, start only after maybe and only allow them
# TODO:  Could be difficult but worth a shot
team_file = "LongTerm"
total_stat_file = "utility/stats.yaml"
league_file = "LongTerm/Totals.yaml"
tables_folder = "LongTermTables"
player_fold = "LongTerm"
generate_stats(player_fold, total_stat_file)
generate_stats(team_file, total_stat_file, team=True)
sort_regions(total_stat_file, player_fold, league_file, team_file, tables_folder)
