"""
Defines the View and Controller for the Script Creator
"""
import dearpygui.dearpygui as dpg
from src.script import *


SCRIPT = Script()
STATIONARY_WINDOW = dict(no_resize=True, no_move=True, no_close=True, collapsed=False)
ALIGN_LEN = 10
CHARACTER_INPUTS = []


def title_callback(_, new_title):
    SCRIPT.set_title(new_title)


def subtitle_callback(_, new_subtitle):
    SCRIPT.set_subtitle(new_subtitle)


def char_loc_submit_callback(sender, app_data):
    is_char = sender[:4] == 'char'
    input_tag = 'char_input' if is_char else 'loc_input'
    list_tag = 'chars' if is_char else 'locs'
    if is_char:
        SCRIPT.add_character(dpg.get_value(input_tag))
        characters = SCRIPT.characters
        for char_inp in CHARACTER_INPUTS:
            dpg.configure_item(char_inp, items=characters)
    else:
        SCRIPT.add_location(dpg.get_value(input_tag))
    dpg.set_value(list_tag, f'{dpg.get_value(list_tag)}\n{dpg.get_value(input_tag)}')
    dpg.set_value(input_tag, '')


def left_label(add_func, label: str, **kwargs):
    with dpg.group(horizontal=True):
        dpg.add_text(label + ' ' * (ALIGN_LEN - len(label)))
        return add_func(**kwargs)


def add_section_callback_factory(scene_num: int, section_type: str):
    id_to_name = {'line': 'Character Line', 'drctn': 'Stage Direction', 'rawmd': 'Raw Markdown'}
    
    def btn_callback(sender, app_data):
        tag = f'scene_{scene_num}_{SCRIPT.get_scene(scene_num).num_sections}'
        with dpg.collapsing_header(label=id_to_name[section_type], tag=tag, parent=f'Scene {scene_num}',
                                   before=f'Scene {scene_num} Buttons', indent=20, user_data=scene_num):
            if section_type == 'line':
                SCRIPT.get_scene(scene_num).add_section(CharacterLine('', ''))
                with dpg.group(horizontal=True, horizontal_spacing=50):
                    char_name = left_label(dpg.add_combo, 'Character:', items=SCRIPT.characters, tag=tag+'_char_name', width=150)
                    CHARACTER_INPUTS.append(char_name)
                    left_label(dpg.add_input_text, 'Stage Direction:', tag=tag+'_char_drctn', width=400)
                left_label(dpg.add_input_text, 'Line:', tag=tag+'_char_line', width=600, height=200, multiline=True)
            elif section_type == 'drctn':
                SCRIPT.get_scene(scene_num).add_section(StageDirection(''))
                left_label(dpg.add_input_text, 'Stage Direction:', tag=tag+'_drctn', width=600, height=200, multiline=True)
            elif section_type == 'rawmd':
                SCRIPT.get_scene(scene_num).add_section(RawSection(''))
                left_label(dpg.add_input_text, 'Markdown:', tag=tag+'_rawmd', width=600, height=200, multiline=True)
    return btn_callback


def add_scene(sender, app_data):
    SCRIPT.add_scene()
    scene_num = SCRIPT.num_scenes
    name = f'Scene {scene_num}'
    with dpg.collapsing_header(label=name, tag=name, parent='Scenes', default_open=True, indent=20):
        with dpg.group(horizontal=True, horizontal_spacing=20, tag=name+' Buttons'):
            button_name = name.lower().replace(' ', '_')
            dpg.add_button(label='Add Character Line', tag=button_name+'_line',
                           callback=add_section_callback_factory(scene_num, 'line'))
            dpg.add_button(label='Add Stage Direction', tag=button_name+'_drctn',
                           callback=add_section_callback_factory(scene_num, 'drctn'))
            dpg.add_button(label='Add Raw Markdown', tag=button_name+'_rawmd',
                           callback=add_section_callback_factory(scene_num, 'rawmd'))


def generate_script(sender, app_data):
    for scene_idx in range(SCRIPT.num_scenes):
        scene_num = scene_idx + 1
        scene = SCRIPT.get_scene(scene_num)
        for section_idx in range(scene.num_sections):
            tag = f'scene_{scene_num}_{section_idx}'
            section = scene.get_section(section_idx)
            if isinstance(section, CharacterLine):
                # assert dpg.get_item_user_data(tag) == 'line'
                section.character = dpg.get_value(tag+'_char_name')
                drctn = dpg.get_value(tag+'_char_drctn')
                if drctn is not None and len(drctn) > 0:
                    section.stage_drctn = drctn
                section.line = dpg.get_value(tag+'_char_line')
            elif isinstance(section, StageDirection):
                # assert dpg.get_item_user_data(tag) == 'drctn'
                section.direction = dpg.get_value(tag+'_drctn')
            elif isinstance(section, RawSection):
                # assert dpg.get_item_user_data(tag) == 'rawmd'
                section.markdown = dpg.get_value(tag+'_rawmd')
            print(f'The section is now:\n{section.export_to_markdown()}\n\n')
    filepath = dpg.get_value('filepath_input')
    assert filepath[-3:] == '.md'
    with open(f'{__file__}/../{filepath}', 'w') as output:
        output.write(SCRIPT.export_to_markdown())


def run():
    dpg.create_context()
    with dpg.window(tag='Primary'):
        left_label(dpg.add_input_text, label='Title:', tag='title_input', callback=title_callback, width=200)
        left_label(dpg.add_input_text, label='Subtitle:', tag='subtitle_input', callback=subtitle_callback,
                              width=400, height=150, multiline=True)
        with dpg.collapsing_header(tag='Char-Locs', label='Characters and Locations', default_open=True):
            with dpg.group(horizontal=True, horizontal_spacing=100):
                left_label(dpg.add_input_text, 'New Character:', tag='char_input', width=100, callback=char_loc_submit_callback, on_enter=True)
                left_label(dpg.add_input_text, 'New Location:', tag='loc_input', width=100, callback=char_loc_submit_callback, on_enter=True)
            with dpg.group(horizontal=True, horizontal_spacing=250, indent=155):
                dpg.add_button(label='Submit', tag='char_submit', callback=char_loc_submit_callback)
                dpg.add_button(label='Submit', tag='loc_submit', callback=char_loc_submit_callback)
            with dpg.group(horizontal=True, horizontal_spacing=240, indent=50):
                dpg.add_text('Characters:', tag='chars')
                dpg.add_text('Locations:', tag='locs')
        with dpg.collapsing_header(tag='Scenes', label='Scenes', default_open=True):
            dpg.add_button(label='Add Scene', tag='add_scene', callback=add_scene)
        with dpg.group(horizontal=True, horizontal_spacing=20):
            left_label(dpg.add_input_text, 'Save To:', tag='filepath_input', width=200)
            dpg.add_button(label='Generate Script', callback=generate_script)

    dpg.create_viewport(title='Script Creator')
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.maximize_viewport()
    dpg.set_primary_window('Primary', True)
    dpg.start_dearpygui()
    dpg.destroy_context()
