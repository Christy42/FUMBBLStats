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


def make_table(pickle_file, rows, name):
    base_string = \
        "[block=panel floatleft width=400px][block=panelheader center]{}[/block][table width=100%]".format(name)
    title_col = "[tr]".format(name)
    dataframe = pd.read_pickle(pickle_file)
    for column in dataframe:
        title_col += "[th]{}[/th]".format(column)
    title_col += "[/tr]"

    row_strings = []
    for i in range(min(rows, len(dataframe))):
        row_strings.append("[tr]")
        for j in range(len(dataframe.columns)):

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
    return """[block display=none]Set up the buttons[/block]
[block=center][toggle group=initial block=overall label=Overall]
[toggle group=initial block=premier label=Premier Division]
[toggle group=initial block=lion label=Lion Conference]\
[toggle group=initial block=unicorn label=Unicorn Conference]
[toggle group=initial block=albany label=Albany Regional]\
[toggle group=initial block=greatalbion label=Great Albion Regional]\
[toggle=image src=/i/558171 group=initial block=morien][/block]"""


def section_toggles(section):
    return """[toggle group={} block=Bash{} label=Bashing]
[toggle group={} block=Score{} label=Scoring]
[toggle group={} block=Misc{} label=Misc.]""".format(section, section, section, section, section, section)


def generate_division(division, formal_division):
    initial_section = "[block=hidden group=initial id={}]".format(division) + section_toggles(division)
    for element in ["Bash", "Score", "Misc"]:
        initial_section += generate_section(division, element, formal_division)
    initial_section += "[/block]"
    return initial_section


def generate_section(division, section, formal_division):
    with open("utility/stat_names.yaml", "r") as stat_file:
        cats = yaml.safe_load(stat_file)
    elements = {}
    for element in cats:
        if cats[element]["Good"]["style"] == section:
            elements.update({element: cats[element]})
    initial_section = "[block=hidden group={} id={}][block=floatcontainer]".format(division, section+division)
    # elements = {"blocks/turns": {"Good": {"name": ["Swarmer"], "style": "Bash", "Team": True, "Individual": True},
    #                              "Bad": {"name": ["Pacifist"], "style": "Bash", "Team": False, "Individual": False}}}
    for element in elements:
        for up_down in ["Good", "Bad"]:
            initial_section += "[block=floatcontainer]"
            if elements[element][up_down]["Individual"]:
                initial_section += "[block=floatleft pad5]"
                initial_section += make_table("tables/" + formal_division + "/" + element.replace("/", "-") +
                                              up_down + ".pkl", 4, elements[element][up_down]["name"][0])
                initial_section += "[/block]"

            if elements[element][up_down]["Team"]:
                initial_section += "[block=floatright pad5]"
                initial_section += make_table("tables/" + formal_division + "/" + element.replace("/", "-") + "Team" +
                                              up_down + ".pkl", 4, elements[element][up_down]["name"][-1])
                initial_section += "[/block]"
            initial_section += "[/block]"
    initial_section += "[/block][/block]"
    return initial_section


# print(generate_section("overall", "Bash"))


def generate_full_tables():
    main_string = initial_toggles()
    for element in [["overall", "overall"], ["premier", "Premier Division"], ["lion", "Lion Conference"], ["unicorn", "Unicorn Conference"],
                    ["albany", "Albany Regional"], ["greatalbion", "Great Albion Regional"],
                    ["morien", "Morien Regional"]]:
        main_string += generate_division(element[0], element[1])
        # main_string += "[/block]"
    return main_string

print(generate_full_tables())
