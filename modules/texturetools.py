import re
import omg
from omg.txdef import Textures
from modules.logg import logg

from modules.wadtools import RES_DIR, get_wad_filename
from pathlib import Path

def get_textures_for_iwad(wad_name, texture_atlas):
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
     
def write_texture_atlas_to_file(atlas, filename, atlas_reference = []):
     texture_file_name = RES_DIR + 'textures.%s' % (filename)
     output_file = open(texture_file_name, 'w')
     total_exported_textures = 0

     for name, data in atlas:
                    if name in atlas_reference:
                         print('Texture %s found in base texture atlas' % (name))
                         continue;
                    
                    output_file.write('Texture "%s", %s, %s' % (name, data.width, data.height) + '\n')
                    output_file.write('{' + '\n')
                    for patch in data.patches:
                         output_file.write('      Patch "%s", %s, %s' % (patch.name, patch.x, patch.y) + '\n')
                    output_file.write('}' + '\n')
                    output_file.write('\n')
                    print('Texture %s exported' % (name))
                    total_exported_textures += 1
               
     message = 'Exported %s textures' % (total_exported_textures)
     
     logg(message)
     print('-' * len(message) + '\n')