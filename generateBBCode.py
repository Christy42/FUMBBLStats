import yaml
import pandas as pd


# Note 114, 34 pixels for pics Careful with text placement, size 9 writing
# #EF82ED Great Albion
# #ADD7F0 Albany
# Morien #9ACE2E
# Lion #B8860B
# Unicorn #696969
# Premier #CACFCB
# Leagues #FFFFFF
# """
#     [block display=none]Set up the buttons[/block]
# [block=center][toggle group=initial block=overall label=Overall]
# [toggle=image src=/i/558896 group=initial block=premier]
# [toggle=image src=/i/558401 group=initial block=lion]\
# [toggle=image src=/i/558403 group=initial block=unicorn]
# [toggle=image src=/i/558399 group=initial block=albany]\
# [toggle=image src=/i/558400 group=initial block=greatalbion]\
# [toggle=image src=/i/558398 group=initial block=morien]
# [toggle=image src=/i/558897 group=initial block=Leagues][/block]"""


# Need to deal with potentially different number of regions each season

def make_table(pickle_file, rows, name, divisions):
    base_string = \
        "[block=panel floatleft width=400px][block=panelheader center]{}[/block][table width=100%]".format(name)
    title_col = "[tr]".format(name)
    dataframe = pd.read_pickle(pickle_file)
    for column in dataframe:
        if column not in ["team id", "division"]:
            title_col += "[th]{}[/th]".format(column)
    title_col += "[/tr]"

    row_strings = []
    for i in range(min(rows, len(dataframe))):
        div = ""
        for element in divisions:
            if divisions[element]["name"] == dataframe.iloc[i].get("division", ""):
                div = element
        colour = divisions.get(div, {}).get("colour", "FFFFFF")
        row_strings.append("[tr bg=#{}]".format(colour))
        if str(dataframe.index[i]) != "-1":
            if "team" in dataframe:
                try:
                    if int(dataframe.index[i]) == -1:
                        raise ValueError("Star player and so no team link")
                    row_strings[i] += "[td][url=https://fumbbl.com/p/player?player_id={}]".format(dataframe.index[i]) +\
                                      str(dataframe.iloc[i][0]) + "[/url][/td]"
                except ValueError:
                    row_strings[i] += "[td]" + str(dataframe.iloc[i][0]) + "[/td]"
            elif "overall" not in dataframe["name"]:
                row_strings[i] += \
                        "[td][url=https://fumbbl.com/p/team?op=view&team_id={}]".format(dataframe.index[i]) + \
                        str(dataframe.iloc[i][0]) + "[/url][/td]"
            else:
                row_strings[i] += "[td]" + str(dataframe.iloc[i][0]) + "[/td]"
        else:
            row_strings[i] += "[td]League[/td]"
        for j in range(1, min(2 + 2 * ("team" in dataframe), len(dataframe.columns))):
            if j == 1 and "team" in dataframe.columns:
                if int(dataframe.iloc[i][-1]) != -1:
                    row_strings[i] += \
                        "[td][url=https://fumbbl.com/p/team?op=view&team_id={}]".format(dataframe.iloc[i][-1]) + \
                        str(dataframe.iloc[i][1]) + "[/url][/td]"
                else:
                    row_strings[i] += "[td]" + str(dataframe.iloc[i][1]) + "[/td]"
            else:

                row_strings[i] += "[td]" + str(dataframe.iloc[i][j]) + "[/td]"
        row_strings[i] += "[/tr]"
    base_string += title_col
    for i in range(len(row_strings)):
        base_string += row_strings[i]
    base_string += "[/table][/block]"
    return base_string


def initial_toggles(division_list):
    # TODO: Here need to check the divisions to do.  Need to plan it out better.  Need  checks, Need levels.
    text = "[block display=none]Set up the buttons[/block]" \
           "[block=center][toggle group=initial block=overall label=Overall]" \
           "" \
           ""
    levels = 0
    for element in division_list:
        levels = max(levels, division_list[element]["level"])
    for i in range(1, levels+1):
        for element in division_list:
            if division_list[element]["level"] == i:
                text += "[toggle=image src=/i/{} group=initial block={}]"\
                    .format(division_list[element]["src"], division_list[element]["shortname"])
        if i != levels + 1:
            text += "\n"
    text += "[toggle=image src=/i/558897 group=initial block=Leagues][/block]"
    return text
# return """
# [block display=none]Set up the buttons[/block]
# [block=center][toggle group=initial block=overall label=Overall]
# [toggle=image src=/i/558896 group=initial block=premier]
# [toggle=image src=/i/558401 group=initial block=lion]\
# [toggle=image src=/i/558403 group=initial block=unicorn]
# [toggle=image src=/i/558399 group=initial block=albany]\
# [toggle=image src=/i/558400 group=initial block=greatalbion]\
# [toggle=image src=/i/558398 group=initial block=morien]
# [toggle=image src=/i/558897 group=initial block=Leagues][/block]"""


def section_toggles(section):
    return """[toggle group={} block=Bash{} label=Bashing]
[toggle group={} block=Score{} label=Scoring]
[toggle group={} block=Misc{} label=Misc.]""".format(section, section, section, section, section, section)


def generate_division(division, formal_division, div_list, yaml_file=None):
    initial_section = "[block=hidden group=initial id={}]".format(division) + section_toggles(division)
    for element in ["Bash", "Score", "Misc"]:
        initial_section += generate_section(division, element, formal_division, div_list, yaml_file=yaml_file)
    initial_section += "[/block]"
    return initial_section


def generate_section(division, section, formal_division, div_list, yaml_file=None):
    fluff = {}
    if yaml_file:
        with open(yaml_file, "r") as file:
            fluff = yaml.safe_load(file)
    with open("utility/stat_names.yaml", "r") as stat_file:
        cats = yaml.safe_load(stat_file)
    elements = cats[section]
    initial_section = "[block=hidden group={} id={}][block=floatcontainer]".format(division, section+division)
    for i in range(len(elements)):
        initial_section += "[block display=none]Here is {} {} {}[/block]".format(division, section, elements[i]["name"])
        if division + section + elements[i]["name"] in fluff:
            initial_section += fluff[division + section + elements[i]["name"]]
        for up_down in ["Good", "Bad"]:
            initial_section += "[block=floatcontainer]"
            if elements[i][up_down]["Individual"] and division != "Leagues":
                initial_section += "[block=floatleft pad5]"
                initial_section += make_table("tables/" + formal_division + "/" +
                                              elements[i]["name"].replace("/", "-") +
                                              up_down + ".pkl", 4, elements[i][up_down]["name"][0], div_list)
                initial_section += "[/block]"

            if elements[i][up_down]["Team"] and division != "Leagues":
                initial_section += "[block=floatright pad5]"
                initial_section += make_table("tables/" + formal_division + "/" +
                                              elements[i]["name"].replace("/", "-") + "Team" +
                                              up_down + ".pkl", 4, elements[i][up_down]["name"][-1], div_list)
                initial_section += "[/block]"
            if elements[i][up_down]["League"] and division == "Leagues":
                initial_section += "[block=floatright pad5]"
                initial_section += make_table("tables/" + formal_division + "/" +
                                              elements[i]["name"].replace("/", "-") +
                                              ".pkl", 40, elements[i][up_down]["name"][-1], div_list)
                initial_section += "[/block]"
            initial_section += "[/block]"

    initial_section += "[/block][/block]"
    return initial_section


def initial_block(style, round_no, season):
    return """

    [block=center][url=FUMBBL.php?page=group&op=view&group=3449][img]http://fumbbl.com/teams/123844.jpg[/img][/url][url=index.php?name=PNphpBB2&file=viewtopic&t=8098][img]http://fumbbl.com/teams/123851.jpg[/img][/url][url=FUMBBL.
    php?page=group&op=view&group=3699][img]http://fumbbl.com/teams/123846.jpg[/img][/url][url=index.php?name=PNphpBB2&
    file=viewtopic&p=274761#274761][img]http://fumbbl.com/teams/123850.jpg[/img][/url][url=index.php?name=PNphpBB2&fil
    e=viewtopic&t=9482][img]http://fumbbl.com/teams/123848.jpg[/img][/url]

[url=FUMBBL.php?page=group&op=view&group=3449][img]http://fumbbl.com/teams/98322.jpg[/img][/url]

[table automargin][tr][td colspan=2 bg=lightblue][block=center][b]{}: [i]Current as of round {} of Season {}[/i][/b]
[/block][/td][/tr]\
[tr][td bg=lightblue][url=FUMBBL.php?page=group&op=view&group=4683]Kill List[/url][/td][td rowspan=6 valign=middle]
Current top and all-time legendary players in the [url=FUMBBL.php?page=group&op=view&group=3449]White Isle League[/url].
 British or based in Britain?  Want to compete in your own nation's league?  Go to our [url=index.php?name=PNphpBB2&file
 =viewtopic&p=274761#274761]recruitment thread[/url] or the [url=FUMBBL.php?page=group&op=view&group=6340]WIL Fringe
 [/url], and get involved in [i]your[/i] local, friendly league.[/td][/tr]\
[tr][td bg=lightblue][url=FUMBBL.php?page=group&op=view&group=3699]Season's Stats[/url][/td][/tr]\
[tr][td bg=lightblue][url=FUMBBL.php?page=group&op=view&group=4360]League Champions[/url][/td][/tr]\
[tr][td bg=lightblue][url=FUMBBL.php?page=group&op=view&group=5573]All Time Stats[/url][/td][/tr]\
[tr][td bg=lightblue][url=FUMBBL.php?page=group&op=view&group=5574]Trivia[/url][/td][/tr][/table]"""\
        .format(style, round_no, season)


#     for element in [["overall", "overall"], ["premier", "Premier Division"], ["lion", "Lion Conference"],
#                     ["unicorn", "Unicorn Conference"], ["albany", "Albany Regional"],
#                     ["greatalbion", "Great Albion Regional"], ["morien", "Morien Regional"], ["Leagues", "Leagues"]]:

def generate_full_tables(round_no, season, division_list):
    main_string = initial_block("Season stats", round_no, season) + initial_toggles(division_list)
    # Need to create this list on the fly from known divisions.  Does ordering matter?  Maybe not.
    div_list = [["overall", "overall"]]
    for element in division_list:
        div_list += [[division_list[element]["shortname"], division_list[element]["name"]]]
    div_list += [["Leagues", "Leagues"]]
    for element in div_list:
        main_string += generate_division(element[0], element[1], division_list, yaml_file="tables/fluff.yaml")
        # main_string += "[/block]"
    main_string.replace("[block=floatcontainer][/block]", "")
    print(main_string)
    return main_string


def generate_kill_list(kill_list_file, team_file, player_files, round_no, season, division_list):
    total_string = initial_block("Kill List", round_no, season) + initial_toggles(division_list)
    with open(player_files, "r") as player_file:
        players = yaml.safe_load(player_file)
    with open(kill_list_file, "r") as kill_file:
        kills = yaml.safe_load(kill_file)
    with open(team_file, "r") as team_f:
        teams = yaml.safe_load(team_f)
    print(teams)
    colour_list = {division_list[element]["name"]: division_list[element]["colour"] for element in division_list}
    for team in kills:

        total_string += "[block=floatcontainer][block bg=#{}]"\
                        .format(colour_list[teams[team]["division"]]) + \
                        "[url=https://fumbbl.com/p/team?team_id={}]{}[/url]"\
                        .format(team, teams[team]["name"]) + "[/block]"
        for i in range(len(kills[team])):
            total_string += "[block=floatleft pad5 bg=#{}][url=https://fumbbl.com/p/player?player_id={}]" \
                            "[picon={} x=1 y=1 title={}][/img][/url][/block] "\
                .format(colour_list[kills[team][i][2]], kills[team][i][0], kills[team][i][1],
                        players[kills[team][i][0]]["name"])
        total_string += "[/block]"
    print(total_string)
