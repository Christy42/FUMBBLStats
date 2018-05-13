import yaml
import pandas as pd

import generateBBCode


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
def sort_players(stat_file, total_stats_file, player_file, region_stats_file,
                 excel_name=None, n=3, team=False, bbcode=False, region="total"):
    with open(region_stats_file, "r") as file:
        region_line = yaml.safe_load(file)[region]
    region_line["name"] = "League"
    region_line["position"] = ""
    region_line["skills"] = ""
    region_line["team"] = ""

    if excel_name:
        writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
    with open(stat_file, "r") as file:
        stats = yaml.safe_load(file)
    with open(player_file, "r") as file:
        players = yaml.safe_load(file)
    # stats = [["blocks", "turns"]]
    dataframe = pd.DataFrame(players).transpose()
    if region != "Total":
        dataframe = dataframe[dataframe.loc[:, "division"] == region]
    for stat in stats:

        temp = dataframe.copy(deep=True)
        if stat[1] == "games":
            temp = temp[temp.loc[:, "games"] >= 3]
        elif stat[1] == "turns":
            temp = temp[temp.loc[:, "turns"] >= 30 * (1 + team * 9)]
        elif stat[1] == "blocks":
            temp = temp[temp.loc[:, "blocks"] >= 10 * (1 + team * 9)]
        cols = ["name", "team", "position", "skills", stat[0] + "/" + stat[1], stat[0], stat[1]]

        if team:
            cols = ["name", stat[0] + "/" + stat[1], stat[0], stat[1]]
        temp = temp[cols]
        append_list = []
        for element in cols:
            append_list.append(region_line[element])
        temp_good = temp.sort_values(by=[stat[0] + "/" + stat[1], stat[1]], ascending=[False, False]).head(n)
        temp_good.loc[-1] = append_list
        if not team:
            del temp_good["skills"]
        if excel_name:
            temp_good.to_excel(writer, sheet_name=stat[0] + " per " + stat[1] + " Good")
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

        temp_bad = temp.sort_values(by=[stat[0] + "/" + stat[1], stat[1]], ascending=[True, False]).head(n)
        temp_bad.loc[-1] = append_list
        if not team:
            del temp_bad["skills"]
        if excel_name:
            temp_bad.to_excel(writer, sheet_name=stat[0] + " per " + stat[1] + " Bad")
            for style in [" Good", " Bad"]:
                worksheet = writer.sheets[stat[0] + " per " + stat[1] + style]
                for col in ["A", "B"]:
                    worksheet.set_column(col + ':' + col, 20, None)
                for col in ["C", "D"] if not team else []:
                    worksheet.set_column(col + ':' + col, 24, None)
                for col in ["E", "F", "G"] if not team else ["C", "D", "E"]:
                    worksheet.set_column(col + ':' + col, 15, None)
        if bbcode:
            generateBBCode.make_table(temp_good, n+1)
            generateBBCode.make_table(temp_bad, n+1)
    with open(total_stats_file, "r") as file:
        total_stats = yaml.safe_load(file)
    for stat in total_stats:
        temp = dataframe.copy(deep=True)
        cols = ["name", stat] if team else ["name", "team", "position", stat]
        temp = temp[cols]
        append_list = []
        for element in cols:
            append_list.append(region_line[element])
        temp = temp.sort_values(by=[stat], ascending=[False])
        temp = temp.head(n)
        temp.iloc[-1] = append_list
        if excel_name:
            temp.to_excel(writer, sheet_name=stat)
            worksheet = writer.sheets[stat]
            for col in ["A", "B"] if not team else ["A"]:
                worksheet.set_column(col + ':' + col, 20, None)
            for col in ["C", "D"] if not team else ["B"]:
                worksheet.set_column(col + ':' + col, 24, None)
            worksheet.set_column('E:E' if not team else 'C:C', 10, None)
        if bbcode:
            generateBBCode.make_table(temp, 3)
    if excel_name:
        writer.save()
    # TODO: Can deal with it from there


def total(team_file, totals_file, stats_file):
    with open(team_file, "r") as file:
        team = yaml.safe_load(file)
    regions = {"total": {}}
    for element in team:
        if team[element]["division"] not in regions:
            regions[team[element]["division"]] = {}
        for stat in team[element]:
            try:
                regions[team[element]["division"]][stat] = \
                    int(regions[team[element]["division"]].get(stat, 0)) + int(team[element][stat])
                regions["total"][stat] = int(regions["total"].get(stat, 0)) + int(team[element][stat])
            except (ValueError, TypeError):
                pass
        regions[team[element]["division"]]["teams"] = regions[team[element]["division"]].get("teams", 0) + 1
        regions["total"]["teams"] = regions["total"].get("teams", 0) + 1
    with open(totals_file, "w") as file:
        yaml.safe_dump(regions, file)
    generate_stats(totals_file, stats_file, team=True)

# generate_stats("player_list//Player.yaml", "utility//stats.yaml")
# generate_stats("player_list//Team.yaml", "utility//stats.yaml", team=True)
# sort_players("utility/stats.yaml", "utility/total_stats.yaml",
#              "player_list/Player.yaml", "player_list/Totals.yaml", bbcode=True, region="Morien Regional")
sort_players("utility/stats.yaml", "utility/total_stats.yaml", "player_list/Team.yaml",
             "player_list/Totals.yaml", team=True, bbcode=True, region="Morien Regional")
# total("player_list/Team.yaml", "player_list/Totals.yaml", "utility/stats.yaml")
