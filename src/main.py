"""
Run from here
"""
import json
import sys
import view_controller as vc
from script import *


def main(data):
    if data is not None:
        vc.SCRIPT.set_title(data['title'])
        vc.SCRIPT.set_subtitle(data['subtitle'])
        for char in data['characters']:
            vc.SCRIPT.add_character(char)
        for loc in data['locations']:
            vc.SCRIPT.add_location(loc)
        for idx, scene_data in enumerate(data['scenes']):
            vc.SCRIPT.add_scene()
            scene = vc.SCRIPT.get_scene(idx + 1)
            for section in scene_data:
                if section['type'] == 'line':
                    scene.add_section(CharacterLine(section['name'], section['line'], section['drctn']))
                elif section['type'] == 'drctn':
                    scene.add_section(StageDirection(section['drctn']))
                elif section['type'] == 'rawmd':
                    scene.add_section(RawSection(section['rawmd']))
    vc.run()


if __name__ == '__main__':
    data = None
    if len(sys.argv) > 1:
        filepath = f'{__file__}/../{sys.argv[1]}'
        with open(filepath, 'r') as file:
            data = json.load(file)
    main(data)
