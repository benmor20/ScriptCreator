"""
Defines the internal representation of the script
"""
import string
import re
from typing import *
from abc import ABC, abstractmethod


class Section(ABC):
    """
    Defines a certain set of lines in the script
    """
    @abstractmethod
    def export_to_markdown(self) -> str:
        """
        :return: a str, this section in Markdown format
        """
        pass

    @abstractmethod
    def copy(self) -> 'Section':
        """
        :return: a copy of this section
        """
        pass


class RawSection(Section):
    """
    Creates a section of script that can contain any Markdown
    """
    def __init__(self, markdown: str):
        """
        Creates a RawSection

        :param markdown: a str, the lines in Markdown format
        """
        self.markdown = markdown

    def export_to_markdown(self) -> str:
        return self.markdown

    def copy(self) -> 'RawSection':
        return RawSection(self.markdown)


class CharacterLine(Section):
    """
    Represents a single line from a character
    """
    def __init__(self, character: str, line: str, stage_direction: Optional[str] = None):
        """
        Creates a new character line

        :param character: a str, the character that is speaking
        :param line: a str, the character's line in Markdown format
        :param stage_direction: a str, stage direction to include before the line, or None if no direction
        """
        self.character = character
        self.line = line
        self.stage_drctn = stage_direction

    def export_to_markdown(self):
        drctn_str = ''
        if self.stage_drctn is not None:
            drctn_str = f' *({self.stage_drctn})*'
        return f'**{self.character.upper()}**:{drctn_str}\n\n{self.line}'

    def copy(self) -> 'CharacterLine':
        return CharacterLine(self.character, self.line, self.stage_drctn)


class StageDirection(Section):
    """
    Represents a stage direction
    """
    def __init__(self, direction: str):
        """
        Creates a new stage direction

        :param direction: a str, the direction to perform in Markdown format
        """
        self.direction = direction

    def export_to_markdown(self) -> str:
        return '*(' + ')*\n\n*('.join(self.direction.split('\n\n')) + ')*'

    def copy(self) -> 'StageDirection':
        return StageDirection(self.direction)


class Scene(Section):
    """
    Represents a whole scene and everything within it

    Attributes:
        scene_num: an int, the scene number of this scene
    """
    def __init__(self, scene_num: int, *sections: Section):
        """
        Creates a Scene

        :param scene_num: an int, the number of this scene
        :param sections: a list of Sections, the sections to include, in order
        """
        self._scene_num = scene_num
        self._sections = list(sections)

    @property
    def scene_num(self) -> int:
        return self._scene_num

    @property
    def num_sections(self) -> int:
        """
        :return: an int, the number of sections in this scene
        """
        return len(self._sections)

    def add_section(self, section: Section):
        """
        Adds a section to this scene

        :param section: the Section to add
        """
        self._sections.append(section)

    def get_section(self, section_num: int) -> Section:
        return self._sections[section_num]

    def delete_section(self, section_num: int):
        """
        Deletes a given section

        :param section_num: an int, the index of the section to delete
        """
        del self._sections[section_num]

    def export_to_markdown(self) -> str:
        return f'## Scene {self._scene_num}\n' + '\n\n<br/>\n\n'.join(s.export_to_markdown() for s in self._sections)

    def copy(self) -> 'Scene':
        return Scene(self._scene_num, *[s.copy() for s in self._sections])


class Script(Section):
    """
    Represents the entire script

    Attributes:
        characters: a list of str, the characters in this Script, sorted alphabetically
        locations: a list of str, the locations in this Script, sorted alphabetically
        title: a str, the title of the script
        subtitle: a str, the subtitle for the script, or None for no subtitle
    """
    def __init__(self):
        """
        Creates a script
        """
        self._characters: Set[str] = set()
        self._locations: Set[str] = set()
        self.title: Optional[str] = None
        self.subtitle: Optional[str] = None
        self._scenes: List[Scene] = []

    @property
    def num_scenes(self) -> int:
        """
        :return: an int, the number of scenes this Script has
        """
        return len(self._scenes)

    @property
    def characters(self) -> List[str]:
        return sorted(self._characters)

    @property
    def locations(self) -> List[str]:
        return sorted(self._locations)

    def set_title(self, title: str):
        """
        Sets the title to the given name

        :param title: a str, what to set the title to
        """
        self.title = title

    def set_subtitle(self, subtitle: str):
        """
        Sets the subtitle to the given value

        :param subtitle: a str, what to set the subtitle to
        """
        self.subtitle = subtitle

    def add_character(self, character: str) -> bool:
        """
        Adds the given character to the list of characters

        :param character: a str, the name of the character to include
        :return: a bool, whether that character already exists in this script
        """
        if character in self._characters:
            return False
        self._characters.add(character)
        return True

    def add_location(self, location: str) -> bool:
        """
        Adds the given location to the list of locations

        :param location: a str, the name of the location to include
        :return: a bool, whether that location already exists in this script
        """
        if location in self._locations:
            return False
        self._locations.add(location)
        return True

    def add_scene(self, *sections: Section):
        """
        Adds a scene with the given sections

        :param sections: the Sections to add to the scene, if any
        """
        self._scenes.append(Scene(len(self._scenes) + 1, *sections))

    def add_section(self, scene_num: int, section: Section):
        """
        Adds a section to the given scene

        :param scene_num: an int, the scene to add the section to
        :param section: a Section, the section to add
        """
        if isinstance(section, StageDirection):
            section.direction = self._modify_stage_drctn(section.direction)
        elif isinstance(section, CharacterLine):
            section.stage_drctn = self._modify_stage_drctn(section.stage_drctn, False)
            section.line = self._modify_line(section.line)
        self._scenes[self._scene_num_to_idx(scene_num)].add_section(section)

    def get_scene(self, scene_num: int) -> Scene:
        """
        Gets a copy of the given scene

        :param scene_num: an int, the Scene to return
        :return: a Scene, a copy of the scene with the scene number
        """
        return self._scenes[self._scene_num_to_idx(scene_num)].copy()

    def get_scene_length(self, scene_num: int) -> int:
        """
        Find the number of sections a given scene has

        :param scene_num: an int, the scene to find the length of
        :return: an int, the number of sections in that scene
        """
        return self._scenes[self._scene_num_to_idx(scene_num)].num_sections

    def delete_section(self, scene_num: int, section_idx: int):
        """
        Deletes a section from the given scene

        :param scene_num: an int, the scene to delete the section from
        :param section_idx: an int, the section to delete
        """
        self._scenes[self._scene_num_to_idx(scene_num)].delete_section(section_idx)

    def export_to_markdown(self) -> str:
        if self.title is None:
            raise ValueError('Cannot export script to Markdown: title is not set.')
        subtitle = '' if self.subtitle is None else f'\n\n{self.subtitle}'
        title = f'# {self.title}{subtitle}'
        scenes = '\n\n<br/>\n\n<br/>\n\n'.join(s.export_to_markdown() for s in self._scenes)
        return f'{title}\n\n<br/>\n\n<br/>\n\n{scenes}'

    def copy(self) -> 'Script':
        res = Script()
        res.set_title(self._title)
        res.set_subtitle(self._subtitle)
        [res.add_character(c) for c in self._characters]
        [res.add_location(l) for l in self._locations]
        [res.add_scene(s.copy()) for s in self._scenes]
        return res

    def _scene_num_to_idx(self, scene_num: int) -> int:
        """
        Translates the scene number to the index of that scene

        :param scene_num: an int, the number of the scene
        :return: an int, the index of the scene in the scene list
        """
        if scene_num > self.num_scenes:
            raise IndexError(f'Tried to access scene {scene_num} but there are only {self.num_scenes} scenes.')
        if scene_num == 0:
            raise IndexError('There is no scene 0.')
        if scene_num < 0:
            return scene_num + self.num_scenes
        return scene_num - 1

    def _modify_stage_drctn(self, drctn: Optional[str], punct: bool = True) -> Optional[str]:
        """
        Formats a stage direction

        Ensures punctuation, puts the characters and locations in all caps

        :param drctn: a str, the raw stage direction
        :param punct: a bool, True to force punctuation at the end, False to remove it
        :return: a str, the formatted stage direction
        """
        if drctn is None:
            return None
        if punct:
            res = drctn + ('' if drctn[-1] in string.punctuation else '.')
        else:
            res = drctn[:-1] if drctn[-1] in string.punctuation else drctn
        to_capitalize = self._characters.union(self._locations)
        for noun in to_capitalize:
            for match in re.finditer(rf"\b{noun}'?s?\b", drctn, re.I):
                res = res[:match.start()] + match.group().upper() + res[match.end():]
        return res

    def _modify_line(self, line: str) -> str:
        """
        Formats a line.

        Ensures punctuation

        :param line: a str, the raw line
        :return: a str, the formatted line
        """
        if line[-1] not in string.punctuation:
            return line + '.'
        return line
