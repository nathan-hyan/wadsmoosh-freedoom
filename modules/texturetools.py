import re
import omg
from omg.txdef import Textures
from modules.logg import logg

from modules.wadtools import DATA_DIR, RES_DIR, get_wad_filename
from pathlib import Path

def get_textures_for_iwad(wad_name):
     wad_filename = get_wad_filename(wad_name)

     logg('Processing textures for wad: %s' % (wad_filename), error=False)

     if wad_filename:
          in_wad = omg.WAD();
          in_wad.from_file(wad_filename)

          texture_lump = in_wad.txdefs['TEXTURE1']
          patches_lump = in_wad.txdefs['PNAMES']
          return Textures(texture_lump, patches_lump).items()

     else:
          logg('Invalid wad %s, skipping...' % (wad_name), error=True)
          return
     
def get_flats_for_iwad(wad_name):
     wad_filename = get_wad_filename(wad_name)
     logg('Processing flats for wad: %s' % (wad_filename), error=False)

     flats = []

     if wad_filename:
          in_wad = omg.WAD();
          in_wad.from_file(wad_filename)

          for flat in in_wad.flats:
               flats.append(flat)

          return flats
     else:
          logg('Invalid wad %s, skipping...' % (wad_name), error=True)
          return


def write_flats_to_file(atlas, filename, atlas_reference = []):
     flats_file_name = DATA_DIR + 'flats_%s' % (filename)

     parsed_flats = []

     for flat in atlas:
          if flat in atlas_reference:
               logg('!> %s already exist' % (flat), error=False)
          else:
               parsed_flats.append(flat)

     flats_file_output = open(flats_file_name, 'w');

     for flat in parsed_flats:
          flats_file_output.write(flat + '\n')

     flats_file_output.close()

def write_texture_atlas_to_file(atlas, filename, atlas_reference = []):
     texture_file_name = RES_DIR + 'textures.%s' % (filename)
     patches_file_name = DATA_DIR + 'patches_%s' % (filename)


     doom_patches = open(DATA_DIR + 'patches_doom1', 'r').read().split('\n')
     doom2_patches = open(DATA_DIR + 'patches_doom2', 'r').read().split('\n')
     common_patches = open(DATA_DIR + 'patches_common', 'r').read().split('\n')

     texture_output_file = open(texture_file_name, 'w')
     patches_output_file = open(patches_file_name, 'w')

     patches_reference_atlas = doom_patches + doom2_patches + common_patches

     parsed_patches = []

     total_exported_textures = 0

     print('\n')
     for name, data in atlas:
                    if name in atlas_reference:
                         print('!> Texture %s found in base texture atlas... skipping' % (name))
                         continue;
                    
                    texture_output_file.write('Texture "%s", %s, %s' % (name, data.width, data.height) + '\n')
                    texture_output_file.write('{' + '\n')
                    for patch in data.patches:
                         if patch.name not in parsed_patches and patch.name not in patches_reference_atlas:
                              parsed_patches.append(patch.name)

                         texture_output_file.write('      Patch "%s", %s, %s' % (patch.name, patch.x, patch.y) + '\n')
                    texture_output_file.write('}' + '\n')
                    texture_output_file.write('\n')
                    total_exported_textures += 1
               
     message = 'Exported %s textures' % (total_exported_textures)

     for patch in parsed_patches:
           patches_output_file.write(patch+'\n')

     texture_output_file.close()
     patches_output_file.close()
     
     print('\n')
     print('-' * len(message))
     logg(message)
     print('-' * len(message) + '\n')