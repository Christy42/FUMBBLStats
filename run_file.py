import yaml

from DataGrab import kill_list_grab, race_check, cycle_divisions, set_player_icons, set_player_numbers
from utility_func import reset_file
from StatCheck import generate_stats, sort_regions, total
from generateBBCode import generate_kill_list, generate_full_tables


class GenerateStats:
    def __init__(self, folder_locations):
        with open(folder_locations) as master_folder:
            self._file_loc = yaml.safe_load(master_folder)
        self._player_folder = self._file_loc["player_folder"]
        self._player_file = self._player_folder + "/" + self._file_loc["player_file"]
        self._kill_file = self._player_folder + "/" + self._file_loc["kill_file"]
        self._team_file = self._player_folder + "/" + self._file_loc["team_file"]
        self._league_file = self._player_folder + "/" + self._file_loc["league_file"]
        self._utility_folder = self._file_loc["utility_folder"]
        self._icon_file = self._utility_folder + "/" + self._file_loc["icon_file"]
        self._stat_name_file = self._utility_folder + "/" + self._file_loc["stat_name_file"]
        self._total_stat_file = self._utility_folder + "/" + self._file_loc["total_stat_file"]
        self._match_folder = self._file_loc["match_folder"]
        self._division_file = self._match_folder + "/" + self._file_loc["division_file"]
        self._run_file = self._match_folder + "/" + self._file_loc["run_file"]
        self._tables_folder = self._file_loc["tables_folder"]

    def set_files(self):
        self._player_file = self._player_folder + "/" + self._file_loc["player_file"]
        self._kill_file = self._player_folder + "/" + self._file_loc["kill_file"]
        self._team_file = self._player_folder + "/" + self._file_loc["team_file"]
        self._league_file = self._player_folder + "/" + self._file_loc["league_file"]
        self._division_file = self._match_folder + "/" + self._file_loc["division_file"]
        self._run_file = self._match_folder + "/" + self._file_loc["run_file"]

    def base_stats(self):
        season = input("Enter in season number")
        round_no = input("Enter in round number")
        self.alter_master_file(season)
        cycle_divisions(self._division_file, self._player_file, self._team_file, round_no, self._run_file)
        race_check(self._team_file)
        set_player_numbers(self._league_file, self._player_file)
        set_player_icons(self._player_file, self._icon_file)

        generate_stats(self._player_file, self._total_stat_file)
        generate_stats(self._team_file, self._total_stat_file, team=True)
        total(self._team_file, self._league_file, self._total_stat_file)
        sort_regions(self._total_stat_file, self._player_file, self._league_file, self._team_file,
                     self._tables_folder, self._division_file)
        with open(self._division_file, "r") as file:
            divisions = yaml.safe_load(file)
        generate_full_tables(round_no, season, divisions)

    def reset_files(self):
        reset_file(self._player_file)
        reset_file(self._team_file)
        reset_file(self._kill_file)
        reset_file(self._league_file)
        reset_file(self._run_file)

    def kill_lists(self):
        kill_list_grab(self._division_file, self._kill_file,  self._team_file, self._player_file)
        season = input("Enter in season number")
        round_no = input("Enter in round number")
        with open(self._division_file, "r") as file:
            divisions = yaml.safe_load(file)
        generate_kill_list(self._kill_file, self._team_file, self._player_file, season, round_no, divisions)

    def master_func(self):
        action = input("Choose to reset (r), get info for the stat page (b) or generate the kill list (k)")
        if action == "r":
            self.reset_files()
        elif action == "b":
            self.base_stats()
        elif action == "k":
            self.kill_lists()

    def alter_master_file(self, season):
        self._player_folder = self._player_folder.split("/")[0] + "/Season" + season
        self._match_folder = self._match_folder.split("/")[0] + "/Season" + season
        self.set_files()


master_cont = GenerateStats("utility/master_loc.yaml")
master_cont.master_func()
