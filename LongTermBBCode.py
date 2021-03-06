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


def make_table(pickle_file, rows, name):
    with open("utility/region_colours.yaml", "r") as file:
        region_colours = yaml.safe_load(file)
    base_string = \
        "[block=panel floatleft width=410px][block=panelheader center]{}[/block][table width=100%]".format(name)
    title_col = "[tr]"
    dataframe = pd.read_pickle(pickle_file)
    title_col += "[th]no[/th]"
    for column in dataframe:
        if column not in ["team id", "division"]:
            title_col += "[th]{}[/th]".format(column)
    title_col += "[/tr]"

    row_strings = []

    for i in range(min(rows, len(dataframe))):
        colour = region_colours.get(dataframe.iloc[i].get("division", ""), "FFFFFF")
        row_strings.append("[tr bg=#{}]".format(colour))
        if str(dataframe.index[i]) != "-1":
            if "team" in dataframe:
                try:
                    if int(dataframe.index[i]) == -1:
                        raise ValueError("Star player and so no team link")
                    row_strings[i] += "[td]{}[/td][td][url=https://fumbbl.com/p/player?player_id={}]".format(i+1, dataframe.index[i]) +\
                                      str(dataframe.iloc[i][0]) + "[/url][/td]"
                except ValueError:
                    row_strings[i] += "[td]" + str(dataframe.iloc[i][0]) + "[/td]"
            else:
                row_strings[i] += \
                        "[td]{}[/td][td][url=https://fumbbl.com/p/team?op=view&team_id={}]".format(i+1, dataframe.index[i]) + \
                        str(dataframe.iloc[i][0]) + "[/url][/td]"
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


def initial_toggles():
    return """
    [block display=none]Set up the buttons[/block]
"""


def section_toggles(section):
    return """[toggle group={} block=Bash{} label=Bashing]
[toggle group={} block=Score{} label=Scoring]
[toggle group={} block=Misc{} label=Misc.]""".format(section, section, section, section, section, section)


def generate_division(yaml_file=None):
    initial_section = "[block group=initial id={}]".format("overall") + section_toggles("overall")
    for element in ["Bash", "Score", "Misc"]:
        initial_section += generate_section(element, yaml_file=yaml_file)
    initial_section += "[/block]"
    return initial_section


def generate_section(section, yaml_file=None):
    fluff = {}
    if yaml_file:
        with open(yaml_file, "r") as file:
            fluff = yaml.safe_load(file)
    with open("utility/stat_names.yaml", "r") as stat_file:
        cats = yaml.safe_load(stat_file)
    elements = cats[section]
    initial_section = "[block group={} id={}][block=floatcontainer]".format("overall", section+"overall")
    for i in range(len(elements)):
        if "turns" in elements[i]["name"]:
            continue
        initial_section += \
            "[block display=none]Here is {} {} {}[/block]".format("overall", section, elements[i]["name"])
        if section + elements[i]["name"] in fluff:
            initial_section += fluff["overall" + section + elements[i]["name"]]
        for up_down in ["Good", "Bad"]:
            initial_section += "[block=floatcontainer]"
            if elements[i][up_down]["Individual"]:
                initial_section += "[block=floatleft pad5]"
                initial_section += make_table("LongTerm/LongTermTables/" +
                                              elements[i]["name"].replace("/", "-") +
                                              up_down + ".pkl", 10, elements[i][up_down]["name"][0])
                initial_section += "[/block]"

            if elements[i][up_down]["Team"]:
                initial_section += "[block=floatright pad5]"
                initial_section += make_table("LongTerm/LongTermTables/" +
                                              elements[i]["name"].replace("/", "-") + "Team" +
                                              up_down + ".pkl", 10, elements[i][up_down]["name"][-1])
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


def generate_full_tables():
    season = input("Enter in Season number")
    round_no = input("Enter in round number")
    main_string = initial_block("Season stats", round_no, season) + initial_toggles()

    main_string += generate_division(yaml_file="tables/fluff.yaml")
    main_string.replace("[block=floatcontainer][/block]", "")
    print(main_string)
    return main_string


generate_full_tables()
