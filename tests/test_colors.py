from color_me.colors import Color

MINECRAFT_COLOR_NAMES = {
    'black',
    'dark_blue',
    'dark_green',
    'dark_aqua',
    'dark_red',
    'dark_purple',
    'gold',
    'gray',
    'dark_gray',
    'blue',
    'green',
    'aqua',
    'red',
    'light_purple',
    'yellow',
    'white',
}


def test_exposes_all_minecraft_colors():
    assert {color.name for color in Color} == MINECRAFT_COLOR_NAMES


def test_team_name_suffix_matches_color_name():
    for color in Color:
        assert color.value == f'__{color.name}'


def test_team_names_are_unique_and_vanilla_safe():
    team_names = [color.value for color in Color]
    assert len(set(team_names)) == len(team_names)
    for team_name in team_names:
        assert len(team_name) <= 16
