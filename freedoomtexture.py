# TODO: Make this function reusable so it can be taken as a function for both freedoom and maybe sigil? - Done!
# TODO: Get texture names from Doom / Doom 2 and use them as references for which texture to process - Done!
# TODO: If wad is freedoom1, extract it in full (except for regular doom textures)
# TODO: If wad is freedoom2 without freedoom1, extract it in full (except for regular doom textures)
# TODO: If wad is freedoom2 with freedoom1, do a comparison and extract only unique textures
# TODO: Print result to textures.freedoom1 and textures.freedoom2
# TODO: Print unmatched patches to patches_freedoom1 and patches_freedoom2

import re
from pathlib import Path
from modules.logg import logg
from modules.texturetools import get_textures_for_iwad, write_texture_atlas_to_file
from modules.wadtools import RES_DIR, get_wad_filename

def get_textures_names(file):
    texture_base_atlas = []

    for texture in re.findall(r'Texture "(.*?)"', Path('%s/%s' % (RES_DIR, file)).read_text()):
        texture_base_atlas.append(texture)

    return texture_base_atlas

def main():
    common_txture = get_textures_names('textures.common')
    doom_txture = get_textures_names('textures.doom1') + common_txture
    doom2_txture = get_textures_names('textures.doom2') + common_txture
    reference_atlas = []
    wad_name = 'freedoom1'
    
    # If freedoom1, freedoom2, doom and doom2 is found, 
    # get texture atlas for both games, and compare them to find duplicates
    # export those duplicated textures into a textures.fdcommon file
    # and merge doom_txture + doom2_txture + textures.fdcommon and process
    # both games after.

    if get_wad_filename('freedoom1') and get_wad_filename('freedoom2') and get_wad_filename('doom') and get_wad_filename('doom2'):
        reference_atlas = doom_txture + doom2_txture
        
        fd2_txtures = []
        fd1_txtures = [] 

        for texture in get_textures_for_iwad('freedoom2', reference_atlas):
            fd2_txtures.append(texture)
        
        for texture in get_textures_for_iwad('freedoom1', reference_atlas):
            fd1_txtures.append(texture)

        print(len(fd2_txtures))
        print(len(fd1_txtures))

        # Merge repeating textures into a common atlas
        common_txture = list(filter(lambda x: x[0] in [element[0] for element in fd2_txtures], fd1_txtures))
        print(len(common_txture))

        # Remove any duplicates found in og Doom and Doom2 atlas
        write_texture_atlas_to_file(common_txture, 'commonfd', reference_atlas)

        final_atlas = get_textures_names('textures.commonfd') + reference_atlas
        print(len(final_atlas))
        
        # Process FD1 and FD2 atlas without repeating commons
        write_texture_atlas_to_file(fd2_txtures, 'freedoom2', final_atlas)
        write_texture_atlas_to_file(fd1_txtures, 'freedoom1', final_atlas)

        # TODO: Both wads uses the same unique new textures, so one textures.freedoom is necessary
        # at this point, all thats left to do is to make some work and progress
        # on the other variants below.
    
    # If freedoom1, doom and doom2 is found,
    # combine doom_txture + doom2_txture and process the fd1
    # textures normally

    if get_wad_filename('freedoom1') and not get_wad_filename('freedoom2') and get_wad_filename('doom') and get_wad_filename('doom2'):
        reference_atlas = doom_txture + doom2_txture
        get_textures_for_iwad('freedoom1', reference_atlas)

    # If freedoom2, doom and doom2 is found,
    # combine doom_txture + doom2_txture and process fd2,
    # textures normally

    if get_wad_filename('freedoom2') and not get_wad_filename('freedoom1') and get_wad_filename('doom') and get_wad_filename('doom2'):
        reference_atlas = doom_txture + doom2_txture
        get_textures_for_iwad('freedoom2', reference_atlas)

    # If freedoom 1 and doom 1 is found,
    # use only doom_txture to filter and process
    # fd1 textures

    if get_wad_filename('freedoom1') and get_wad_filename('doom') and not get_wad_filename('freedoom2') and not get_wad_filename('doom2'):
        get_textures_for_iwad('freedoom1', doom_txture)

    # If freedoom 2 and doom 2 is found,
    # use only doom2_txture to filter and process
    # fd2 textures 

    if get_wad_filename('freedoom2') and get_wad_filename('doom2') and not get_wad_filename('freedoom1') and not get_wad_filename('doom'):
        get_textures_for_iwad('freedoom2', doom_txture)

    
    

if __name__ == "__main__":
    main()