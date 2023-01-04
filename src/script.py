"""
Defines the internal representation of the script
"""
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
        self._markdown = markdown

    def export_to_markdown(self) -> str:
        return self._markdown

    def copy(self) -> 'RawSection':
        return RawSection(self._markdown)


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
        self._character = character
        self._line = line
        self._stage_drctn = stage_direction

    def export_to_markdown(self):
        drctn_str = ''
        if self._stage_drctn is not None:
            drctn_str = f'*({self._stage_drctn})*'
        return f'**{self._character.upper()}**:{drctn_str}\n\n{self._line}'

    def copy(self) -> 'CharacterLine':
        return CharacterLine(self._character, self._line, self._stage_drctn)


class StageDirection(Section):
    """
    Represents a stage direction
    """
    def __init__(self, direction: str):
        """
        Creates a new stage direction

        :param direction: a str, the direction to perform in Markdown format
        """
        self._direction = direction

    def export_to_markdown(self) -> str:
        return f'*({self._direction})*'

    def copy(self) -> 'StageDirection':
        return StageDirection(self._direction)


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

    def add_section(self, section: Section):
        """
        Adds a section to this scene

        :param section: the Section to add
        """
        self._sections.append(section)

    def export_to_markdown(self) -> str:
        return f'## Scene {self._scene_num}\n' + '\n\n<br/>\n\n'.join(s.export_to_markdown() for s in self._sections)

    def copy(self) -> 'Scene':
        return Scene(self._scene_num, *[s.copy() for s in self._sections])


class Script(Section):
    """
    Represents the entire script
    """
    def __init__(self):
        """
        Creates a script
        """
        self._characters: Set[str] = set()
        self._locations: Set[str] = set()
        self._title: Optional[str] = None
        self._subtitle: Optional[str] = None
        self._scenes: List[Scene] = []
        self._active_scene = -1

    def set_title(self, title: str):
        """
        Sets the title to the given name

        :param title: a str, what to set the title to
        """
        self._title = title

    def set_subtitle(self, subtitle: str):
        """
        Sets the subtitle to the given value

        :param subtitle: a str, what to set the subtitle to
        """
        self._subtitle = subtitle

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

    def update_scene(self, scene_num: int, new_scene: Scene):
        """
        Switches out the given scene number for the new scene

        :param scene_num: an int, the scene number to switch out
        :param new_scene: the Scene to set the scene number to
        """
        if scene_num != new_scene.scene_num:
            raise ValueError(f'Cannot set scene {scene_num} to be Scene {new_scene.scene_num}')
        if scene_num > len(self._scenes):
            raise ValueError(f'Tried to reset scene {scene_num}, but there are only {len(self._scenes)} scenes.')
        if scene_num <= 0:
            raise ValueError(f'The scene number must be positive (not {scene_num})')
        self._scenes[scene_num - 1] = new_scene

    def export_to_markdown(self) -> str:
        title = f'<div align="center"># {self._title}\n\n{self._subtitle}</div>'
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
