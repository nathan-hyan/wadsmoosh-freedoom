from omg.util import *
from struct import unpack
import time
from modules.wadtools import SRC_WAD_DIR
import omg;
from omg.txdef import Textures

def main():
    # TODO: Get texture names from Doom / Doom 2 and use them as references for which texture to process and what not
    # TODO: Print result to textures.freedoom1 and textures.freedoom2
    # TODO: Print unmatched patches to patches_freedoom1 and patches_freedoom2

    wad_filename =  SRC_WAD_DIR + '/freedoom1.wad'
    wad = omg.WAD(from_file=wad_filename)

    texture_lump = wad.txdefs['TEXTURE1']
    patches_lump = wad.txdefs['PNAMES']
    textures_editor = Textures(texture_lump, patches_lump).items()

    for x, y in textures_editor:
            print('Texture "%s", %s, %s' % (x, y.width, y.height))
            print('{')
            for patch in y.patches:
                 print('    Patch "%s", %s, %s' % (patch.name, patch.x, patch.y))
            print('}')
            print('\n\n')

    
    # current_time=time.time();
    # saveFile = 'test_%s' % current_time
    # print(texture_lump)

    # def unpack_texture(texture1, pnames):
    #     # Unpack PNAMES
    #     numdefs = unpack16(pnames.data[0:2])
    #     pnames = [zstrip(pnames.data[ptr:ptr+8]) \
    #         for ptr in range(4, 8*numdefs+4, 8)]

    #     # Unpack TEXTURE1
    #     data = texture1.data
    #     numtextures = unpack('<i', data[0:4])[0]
    #     pointers = unpack('<%ii'%numtextures, data[4:4+numtextures*4])
    #     for ptr in pointers:
    #         texture = TextureDef(bytes=data[ptr:ptr+22])
    #         for pptr in range(ptr+22, ptr+22+10*texture.npatches, 10):
    #             x, y, idn = unpack('<hhh', data[pptr:pptr+6])
    #             texture.patches.append(PatchDef(x, y, name=pnames[idn]))
    #         print(texture.name)
    #         for x in texture.patches:
    #             print(x.x, x.y, x.id, x.name)

    # unpack_texture(texture_lump, patches_lump)
    
    # for x in textures_editor:
    #     print(x)

    

if __name__ == "__main__":
    main()