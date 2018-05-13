import yaml


def reset_file(file_address):
    with open(file_address, "w") as file:
        yaml.safe_dump({}, file)
