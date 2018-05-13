import yaml
import pandas as pd


def make_table(dataframe, rows):
    base_string = "[table width=100%]"
    title_col = "[tr]"
    for column in dataframe:
        title_col += "[th]{}[/th]".format(column)
    title_col += "[/tr]"
    row_strings = []
    for i in range(rows):
        row_strings.append("[tr]")
        for j in range(len(dataframe.columns)):
            row_strings[i] += "[td]" + str(dataframe.iloc[i][j]) + "[/td]"
        row_strings[i] += "[/tr]"
    base_string += title_col
    for i in range(len(row_strings)):
        base_string += row_strings[i]
    base_string += "[/table]"
    print(base_string)

#[tr][td]R1C1[/td] [td]R1C2[/td] [td]Debir Dullza [/td][td]R1C4[/td][/tr]
#[tr][td]R1C1[/td] [td]R1C2[/td] [td]R1C3 [/td][td]R1C4[/td][/tr]
#[tr][td]R1C1[/td] [td]R1C2[/td] [td]R1C3 [/td][td]R1C4[/td][/tr]