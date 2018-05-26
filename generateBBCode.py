import yaml
import pandas as pd

# Alicewhite | F0F8FF] # Antiquewhite | FAEBD7 # Aqua | 00FFFF # Aquamarine | 7FFFD4 # Azure | F0FFFF # Beige | F5F5DC
# Bisque | FFE4C4 # Blanchedalmond | FFEBCD # Blue | 0000FF # Blueviolet | 8A2BE2 # Brown | A52A2A # Burlywood | DEB887
# Cadetblue | 5F9EA0 # Chartreuse | 7FFF00 # Chocolate | D2691E # Coral | FF7F50 # Cornflowerblue | 6495ED
# Cornsilk | FFF8DC # Crimson | DC143C # Cyan | 00FFFF # Darkblue | 00008B # Darkcyan | 008B8B # Darkgoldenrod | B8860B
# Darkgray | A9A9A9 # Darkgreen | 006400 # Darkkhaki | BDB76B # Darkmagenta | 8B008B # Darkolivegreen | 556B2F
# Darkorange | FF8C00 # Darkorchid | 9932CC # Darkred | 8B0000 # Darksalmon | E9967A # Darkseagreen | 8FBC8F
# Darkslateblue | 483D8B Darkslategray | 2F4F4F # Darkturquoise | 00CED1 # Darkviolet | 9400D3
# Deeppink | FF1493 # Deepskyblue | 00BFFF # Dimgray | 696969 # Dodgerblue | 1E90FF # Firebrick | B22222
# Floralwhite | FFFAF0 # Forestgreen | 228B22 # Fuchsia | FF00FF # Gainsboro | DCDCDC # Ghostwhite | F8F8FF
# Gold | FFD700 # Goldenrod | DAA520 # Gray | 808080 # Green | 008000 # Greenyellow | ADFF2F # Honeydew | F0FFF0
# Hotpink | FF69B4 # Indianred | CD5C5C # Indigo | 4B0082 # Ivory | FFFFF0 # Khaki | F0E68C # Lavender | E6E6FA
# Lavenderblush | FFF0F5 # Lawngreen | 7CFC00 # Lemonchiffon | FFFACD # Lightblue | ADD8E6 # Lightcoral | F08080
# Lightcyan | E0FFFF # Lightgoldenrodyellow | FAFAD2 # Lightgreen | 90EE90 # Lightgrey | D3D3D3	Lightpink | FFB6C1
# Lightsalmon | FFA07A # Lightseagreen | 20B2AA # Lightskyblue | 87CEFA # Lightslategray | 778899
# Lightsteelblue | B0C4DE] # Linen | FAF0E6 # Magenta | FF00FF # Maroon | 800000 # Mediumaquamarine | 66CDAA
# Mediumblue | 0000CD # Mediumorchid | BA55D3 # Mediumpurple | 9370D8 # Mediumseagreen | 3CB371
# Mediumslateblue | 7B68EE # Mediumspringgreen | 00FA9A # Mediumturquoise | 48D1CC # Mediumvioletred | C71585
# Midnightblue | 191970 # Mintcream | F5FFFA # Mistyrose | FFE4E1 # Moccasin | FFE4B5 # Navajowhite | FFDEAD
# Navy | 000080 # Oldlace | FDF5E6 # Olive | 808000 # Olivedrab | 688E23 # Orange | FFA500 # Orangered | FF4500
# Orchid | DA70D6 # Palegoldenrod | EEE8AA # Palegreen | 98FB98 # Paleturquoise | AFEEEE # Palevioletred | D87093
# Papayawhip | FFEFD5 # Peachpuff | FFDAB9 # Peru | CD853F # Pink | FFC0CB # Plum | DDA0DD # Powderblue | B0E0E6
# Purple | 800080 # Red | FF0000 # Rosybrown | BC8F8F # Royalblue | 4169E1 # Saddlebrown | 8B4513 # Salmon | FA8072
# Sandybrown | F4A460 # Seagreen | 2E8B57 # Seashell | FFF5EE # Sienna | A0522D # Silver | C0C0C0 # Skyblue | 87CEEB
# Slateblue | 6A5ACD # Slategray | 708090 # Snow | FFFAFA # Springgreen | 00FF7F # Steelblue | 4682B4 # Tan | D2B48C
# Teal | 008080 # Thistle | D8BFD8 # Tomato | FF6347 # Turquoise | 40E0D0 # Violet | EE82EE # Wheat | F5DEB3
# White | FFFFFF # Whitesmoke | F5F5F5 # Yellow | FFFF00 # Yellowgreen | 9ACD32

# Note 114, 34 pixels for pics Careful with text placement, size 9 writing
# #EF82ED Great Albion
# #ADD7F0 Albany
# Morien #9ACE2E
# Lion #B8860B
# Unicorn #696969
# Premier #FFFFFF


def make_table(pickle_file, rows, name):
    with open("utility/region_colours.yaml", "r") as file:
        region_colours = yaml.safe_load(file)
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
        colour = region_colours.get(dataframe.iloc[i]["division"], "FFFFFF")
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
            else:
                row_strings[i] += \
                        "[td][url=https://fumbbl.com/p/team?op=view&team_id={}]".format(dataframe.index[i]) + \
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

# make_table("tables/casualtiesGood.pkl", 4, "Casualties")

# [tr][td]R1C1[/td] [td]R1C2[/td] [td]Debir Dullza [/td][td]R1C4[/td][/tr]
# [tr][td]R1C1[/td] [td]R1C2[/td] [td]R1C3 [/td][td]R1C4[/td][/tr]
# [tr][td]R1C1[/td] [td]R1C2[/td] [td]R1C3 [/td][td]R1C4[/td][/tr]


def initial_toggles():
    return """

    [block display=none]Set up the buttons[/block]
[block=center][toggle group=initial block=overall label=Overall]
[toggle=image src=/i/558402 group=initial block=premier]
[toggle=image src=/i/558401 group=initial block=lion]\
[toggle=image src=/i/558403 group=initial block=unicorn]
[toggle=image src=/i/558399 group=initial block=albany]\
[toggle=image src=/i/558400 group=initial block=greatalbion]\
[toggle=image src=/i/558398 group=initial block=morien][/block]"""


def section_toggles(section):
    return """[toggle group={} block=Bash{} label=Bashing]
[toggle group={} block=Score{} label=Scoring]
[toggle group={} block=Misc{} label=Misc.]""".format(section, section, section, section, section, section)


def generate_division(division, formal_division, yaml_file=None):
    initial_section = "[block=hidden group=initial id={}]".format(division) + section_toggles(division)
    for element in ["Bash", "Score", "Misc"]:
        initial_section += generate_section(division, element, formal_division, yaml_file=yaml_file)
    initial_section += "[/block]"
    return initial_section


def generate_section(division, section, formal_division, yaml_file=None):
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
        if division + section in fluff:
            initial_section += fluff[division + section + elements[i]["name"]]
        for up_down in ["Good", "Bad"]:
            initial_section += "[block=floatcontainer]"
            if elements[i][up_down]["Individual"]:
                initial_section += "[block=floatleft pad5]"
                initial_section += make_table("tables/" + formal_division + "/" +
                                              elements[i]["name"].replace("/", "-") +
                                              up_down + ".pkl", 4, elements[i][up_down]["name"][0])
                initial_section += "[/block]"

            if elements[i][up_down]["Team"]:
                initial_section += "[block=floatright pad5]"
                initial_section += make_table("tables/" + formal_division + "/" +
                                              elements[i]["name"].replace("/", "-") + "Team" +
                                              up_down + ".pkl", 4, elements[i][up_down]["name"][-1])
                initial_section += "[/block]"
            initial_section += "[/block]"
    initial_section += "[/block][/block]"
    return initial_section


# print(generate_section("overall", "Bash"))


def generate_full_tables():
    main_string = """[block=center][url=FUMBBL.php?page=group&op=view&group=3449][img]http://fumbbl.com/teams/123844.jpg[/img][/url][url=index.php?name=PNphpBB2&file=viewtopic&t=8098][img]http://fumbbl.com/teams/123851.jpg[/img][/url][url=FUMBBL.php?page=group&op=view&group=3699][img]http://fumbbl.com/teams/123846.jpg[/img][/url][url=index.php?name=PNphpBB2&file=viewtopic&p=274761#274761][img]http://fumbbl.com/teams/123850.jpg[/img][/url][url=index.php?name=PNphpBB2&file=viewtopic&t=9482][img]http://fumbbl.com/teams/123848.jpg[/img][/url]

[url=FUMBBL.php?page=group&op=view&group=3449][img]http://fumbbl.com/teams/98322.jpg[/img][/url]

[table automargin][tr][td colspan=2 bg=lightblue][block=center][b]Hall of Fame: [i]Current as of round 5 of Season 48[/i][/b][/block][/td][/tr]\
[tr][td bg=lightblue][url=FUMBBL.php?page=group&op=view&group=4683]On Fire this Season[/url][/td][td rowspan=6 valign=middle]Current top and all-time legendary players in the [url=FUMBBL.php?page=group&op=view&group=3449]White Isle League[/url].  British or based in Britain?  Want to compete in your own nation's league?  Go to our [url=index.php?name=PNphpBB2&file=viewtopic&p=274761#274761]recruitment thread[/url] or the [url=FUMBBL.php?page=group&op=view&group=6340]WIL Fringe[/url], and get involved in [i]your[/i] local, friendly league.[/td][/tr]\
[tr][td bg=lightblue][url=FUMBBL.php?page=group&op=view&group=3699]Hall of Fame[/url][/td][/tr]\
[tr][td bg=lightblue][url=FUMBBL.php?page=group&op=view&group=4360]League Champions[/url][/td][/tr]\
[tr][td bg=lightblue][url=FUMBBL.php?page=group&op=view&group=5573]Ref's Report[/url][/td][/tr]\
[tr][td bg=lightblue][url=FUMBBL.php?page=group&op=view&group=5574]Trivia[/url][/td][/tr][/table]""" + initial_toggles()
    for element in [["overall", "overall"], ["premier", "Premier Division"], ["lion", "Lion Conference"],
                    ["unicorn", "Unicorn Conference"], ["albany", "Albany Regional"],
                    ["greatalbion", "Great Albion Regional"], ["morien", "Morien Regional"]]:
        main_string += generate_division(element[0], element[1], yaml_file="tables/fluff.yaml")
        # main_string += "[/block]"
    main_string.replace("[block=floatcontainer][/block]", "")
    return main_string

print(generate_full_tables())
