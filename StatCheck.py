import yaml
import pandas as pd

import generateBBCode


# TODO: Total Each region by itself
# TODO: Total, sum the regions together
# TODO: Top x for each region in each category given
def get_spp(stats):
    return 1 * stats["completions"] + 2 * stats["casualties"] + 3 * stats["touchdowns"] + 5 * stats["mvps"]


def get_stat(numerator, denominator, stats):
    if int(stats[denominator]) == 0:
        return 0.0
    else:
        return round(float(stats[numerator]) / float(stats[denominator]), 2)


def generate_stats(player_file, stats_file, team=False):
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

    with open(player_file, "w") as p_file:
        yaml.safe_dump(players, p_file)


def sort_players(stat_file, total_stats_file, player_file, excel_name, n=5, team=False, bbcode=False):
    if not bbcode:
        writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
    with open(stat_file, "r") as file:
        stats = yaml.safe_load(file)
    with open(player_file, "r") as file:
        players = yaml.safe_load(file)
    # stats = [["blocks", "turns"]]
    dataframe = pd.DataFrame(players).transpose()
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
        temp_good = temp.sort_values(by=[stat[0] + "/" + stat[1], stat[1]], ascending=[False, False]).head(n)
        if not team:
            del temp_good["skills"]
        if not bbcode:
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
        if not team:
            del temp_bad["skills"]
        if not bbcode:
            temp_bad.to_excel(writer, sheet_name=stat[0] + " per " + stat[1] + " Bad")
            for style in [" Good", " Bad"]:
                worksheet = writer.sheets[stat[0] + " per " + stat[1] + style]
                for col in ["A", "B"]:
                    worksheet.set_column(col + ':' + col, 20, None)
                for col in ["C", "D"] if not team else []:
                    worksheet.set_column(col + ':' + col, 24, None)
                for col in ["E", "F", "G"] if not team else ["C", "D", "E"]:
                    worksheet.set_column(col + ':' + col, 15, None)
        generateBBCode.make_table(temp_good, 3)
        generateBBCode.make_table(temp_bad, 3)
    with open(total_stats_file, "r") as file:
        total_stats = yaml.safe_load(file)
    for stat in total_stats:
        temp = dataframe.copy(deep=True)
        cols = ["name", stat] if team else ["name", "team", "position", stat]
        temp = temp[cols]
        temp = temp.sort_values(by=[stat], ascending=[False])
        temp = temp.head(n)
        if not bbcode:
            temp.to_excel(writer, sheet_name=stat)
            worksheet = writer.sheets[stat]
            for col in ["A", "B"] if not team else ["A"]:
                worksheet.set_column(col + ':' + col, 20, None)
            for col in ["C", "D"] if not team else ["B"]:
                worksheet.set_column(col + ':' + col, 24, None)
            worksheet.set_column('E:E' if not team else 'C:C', 10, None)
        generateBBCode.make_table(temp, 3)
    if not bbcode:
        writer.save()
    # TODO: Can deal with it from there


def total(player_file, totals_file, regional=False):
    with open()
    if regional:
        pass
    else:
        pass
    pass

generate_stats("player_list//Player.yaml", "utility//stats.yaml")
generate_stats("player_list//Team.yaml", "utility//stats.yaml", team=True)
# sort_players("utility/stats.yaml", "utility/total_stats.yaml",
#              "player_list/Player.yaml", "C:/Users/Mark/Documents/FUMBBL/PlayerStats.xlsx", bbcode=True)
# sort_players("utility/stats.yaml", "utility/total_stats.yaml",
#              "player_list/Team.yaml", "C:/Users/Mark/Documents/FUMBBL/TeamStats.xlsx", team=True, bbcode=True)
