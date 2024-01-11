# WARNING: This is a WIP tool for extracting the
# textures, patches and flats from freedoom 1 and 2
# It's an extreme work in progress so proceed at your own risk! :)

# TODO: Figure out how to separate skies from FD1 and FD2
# TODO: Assign them separately from the regular Doom and Doom 2's skies
# TODO: Clean this mess

import re
from pathlib import Path
from modules.texturetools import get_flats_for_iwad, get_textures_for_iwad, write_flats_to_file, write_texture_atlas_to_file
from modules.wadtools import DATA_DIR, RES_DIR, get_wad_filename

def get_textures_names(file):
    texture_base_atlas = []

    for texture in re.findall(r'Texture "(.*?)"', Path('%s/%s' % (RES_DIR, file)).read_text()):
        texture_base_atlas.append(texture)

    return texture_base_atlas

def main():
    common_txture = get_textures_names('textures.common')
    doom_txture = get_textures_names('textures.doom1') + common_txture
    doom2_txture = get_textures_names('textures.doom2') + common_txture
    
    common_flats = open(DATA_DIR+'flats_common', 'r').read().split('\n')
    doom2_flats = open(DATA_DIR+'flats_doom2', 'r').read().split('\n')
    
    reference_texture_atlas = []
    reference_flats_atlas = []
    
    # If freedoom1, freedoom2, doom and doom2 is found, 
    # get texture atlas for both games, and compare them to find duplicates
    # export those duplicated textures into a textures.fdcommon file
    # and merge doom_txture + doom2_txture + textures.fdcommon and process
    # both games after.

    if get_wad_filename('freedoom1') and get_wad_filename('freedoom2'):
        reference_texture_atlas = doom_txture + doom2_txture
        reference_flats_atlas = common_flats + doom2_txture
        
        fd2_txtures = []
        fd1_txtures = [] 
        fd2_flats = []
        fd1_flats = []


        for texture in get_textures_for_iwad('freedoom2'):
            fd2_txtures.append(texture)
        
        for texture in get_textures_for_iwad('freedoom1'):
            print(texture)
            fd1_txtures.append(texture)

        for flat in get_flats_for_iwad('freedoom2'):
            fd2_flats.append(flat)

        for flat in get_flats_for_iwad('freedoom1'):
            fd1_flats.append(flat)

        # Merge repeating textures into a common atlas
        common_txture = list(filter(lambda x: x[0] in [element[0] for element in fd2_txtures], fd1_txtures))
        common_flats = list(filter(lambda x: x[0] in [element[0] for element in fd2_flats], fd1_flats))

        # Remove any duplicates found in og Doom and Doom2 atlas
        write_texture_atlas_to_file(common_txture, 'freedoom', reference_texture_atlas)
        write_flats_to_file(common_flats, 'freedoom', reference_flats_atlas)
        
        # Process FD1 and FD2 atlas without repeating commons
        # write_texture_atlas_to_file(fd2_txtures, 'freedoom2', final_atlas)
        # write_texture_atlas_to_file(fd1_txtures, 'freedoom1', final_atlas)

        # TODO: Both wads uses the same unique new textures, so one textures.freedoom is necessary
        # at this point, all thats left to do is to make some work and progress
        # on the other variants below.
    
    # If freedoom1, doom and doom2 is found,
    # combine doom_txture + doom2_txture and process the fd1
    # textures normally

    # if get_wad_filename('freedoom1') and not get_wad_filename('freedoom2') and get_wad_filename('doom') and get_wad_filename('doom2'):
    #     reference_atlas = doom_txture + doom2_txture
    #     get_textures_for_iwad('freedoom1', reference_atlas)

    # # If freedoom2, doom and doom2 is found,
    # # combine doom_txture + doom2_txture and process fd2,
    # # textures normally

    # if get_wad_filename('freedoom2') and not get_wad_filename('freedoom1') and get_wad_filename('doom') and get_wad_filename('doom2'):
    #     reference_atlas = doom_txture + doom2_txture
    #     get_textures_for_iwad('freedoom2', reference_atlas)

    # # If freedoom 1 and doom 1 is found,
    # # use only doom_txture to filter and process
    # # fd1 textures

    # if get_wad_filename('freedoom1') and get_wad_filename('doom') and not get_wad_filename('freedoom2') and not get_wad_filename('doom2'):
    #     get_textures_for_iwad('freedoom1', doom_txture)

    # # If freedoom 2 and doom 2 is found,
    # # use only doom2_txture to filter and process
    # # fd2 textures 

    # if get_wad_filename('freedoom2') and get_wad_filename('doom2') and not get_wad_filename('freedoom1') and not get_wad_filename('doom'):
    #     get_textures_for_iwad('freedoom2', doom_txture)    

if __name__ == "__main__":
    main()