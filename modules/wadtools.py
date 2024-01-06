import os
import omg
from shutil import copyfile
from modules.logg import logg
from wadsmoosh_data import RES_FILES, WAD_LUMP_LISTS

SRC_WAD_DIR = 'source_wads/'
DATA_DIR = 'data/'
DEST_DIR = 'pk3/'
DEST_FILENAME = 'doom_complete.pk3'
RES_DIR = 'res/'
BFG_ONLY_LUMP = ''

# track # of maps extracted
NUM_MAPS = 0


def get_wad_filename(wad_name):
    # return filename of first case-insensitive match
    wad_name += '.wad'
    for filename in os.listdir(SRC_WAD_DIR):
        if wad_name.lower() == filename.lower():
            return SRC_WAD_DIR + filename
    return None

def extract_map(in_wad, map_name, out_filename):
    global NUM_MAPS
    out_wad = omg.WAD()
    out_wad.maps[map_name] = in_wad.maps[map_name]
    out_wad.to_file(out_filename)
    NUM_MAPS += 1

def extract_iwad_maps(wad_name, map_prefix):
    in_wad = omg.WAD()
    wad_filename = get_wad_filename(wad_name)
    in_wad.from_file(wad_filename)
    for map_name in in_wad.maps.find('*'):
        logg('  Extracting map %s...' % map_name)
        out_wad_filename = DEST_DIR + 'maps/' + map_prefix + map_name + '.wad'
        extract_map(in_wad, map_name, out_wad_filename)
        #logg('  Saved map %s' % out_wad_filename)

def extract_lumps(wad_name):
    if not wad_name in WAD_LUMP_LISTS:
        return
    
    wad = omg.WAD()
    wad_filename = get_wad_filename(wad_name)
    wad.from_file(wad_filename)
    
    for lump_list in WAD_LUMP_LISTS[wad_name]:
    
        # derive subdir from name of lump list
        try:
            lump_type = lump_list[:lump_list.index('_')]
        except ValueError:
            logg("ERROR: Couldn't identify type of lump list %s" % lump_list, error=True)
            continue
        # sigil sky lump isn't in patch namespace
        if lump_list == 'patches_sigil':
            lump_type = 'data'
        lump_table = getattr(wad, lump_type, None)
        if not lump_table:
            logg('  ERROR: Lump type %s not found' % lump_type, error=True)
            continue
        logg('  extracting %s...' % lump_list)
        # sigil sky is in data namespace but we want it in patches dir
        if wad_name == 'sigil' and lump_list == 'patches_sigil':
            lump_subdir = DEST_DIR + 'patches/'
        # sigil 1&2 screens aren't in graphics namespace but belong in that dir
        elif wad_name == 'sigil' and lump_type == 'data':
            lump_subdir = DEST_DIR + 'graphics/'
        elif wad_name == 'sigil2' and lump_type == 'data':
            lump_subdir = DEST_DIR + 'graphics/'
        # write PLAYPAL, TEXTURE1 etc to pk3 root
        elif lump_type in ['data', 'txdefs']:
            lump_subdir = DEST_DIR
        else:
            lump_subdir = DEST_DIR + lump_type + '/'
        # process each item in lump list
        for line in open(DATA_DIR + lump_list).readlines():
            line = line.strip()
            # ignore comments
            if line.startswith('//'):
                continue
            # no colon: extracted lump uses name from list
            if line.find(':') == -1:
                out_filename = line
                lump_name = line
            # colon: use filename to right of colon
            else:
                # split then strip
                lump_name, out_filename = line.split(':')
                lump_name = lump_name.strip()
                out_filename = out_filename.strip()
            if not lump_name in lump_table:
                logg("  ERROR: Couldn't find lump with name %s" % lump_name, error=True)
                continue
            lump = lump_table[lump_name]
            out_filename += '.lmp' if lump_type != 'music' else '.mus'
            logg('    Extracting %s' % lump_subdir + out_filename)
            lump.to_file(lump_subdir + out_filename)

def copy_resources():
    # wadsmoosh_data/RES_FILES contains all pre-made files
    # that are needed for the gzdoom engine to understand what's going on

    for src_file in RES_FILES:
        # don't copy texture lumps for files that aren't present
        if src_file.startswith('textures.doom1') and not get_wad_filename('doom'):
            continue
        elif src_file == 'textures.doom2' and not get_wad_filename('doom2'):
            # DO copy if final doom exists and doom2 doesn't
            if not get_wad_filename('tnt'):
                continue
        elif src_file == 'textures.tnt' and not get_wad_filename('tnt'):
            continue
        elif src_file == 'textures.plut' and not get_wad_filename('plutonia'):
            continue
        
        # TODO: Read both freedoom's TEXTURE1/PNAMES files and extract only the files that doesnt exist in regular doom2 / tnt TEXTURE1/PNAMES 
        # TODO: Probably we can use textures from one game in the other


        elif src_file == 'textures.freedoom1' and not get_wad_filename('freedoom1'):
            continue
        elif src_file == 'textures.freedoom2' and not get_wad_filename('freedoom2'):
            continue

        logg('Copying %s' % src_file)
        copyfile(RES_DIR + src_file, DEST_DIR + src_file)
    
    # doom2 vs doom2bfg map31/32 names differ, different mapinfos with same name
    d2wad = omg.WAD()
    d2_wad_filename = get_wad_filename('doom2')
    
    # neither doom2: mapinfo still wants a file for the secret levels
    if not d2_wad_filename:
        copyfile(RES_DIR + 'mapinfo/doom2_nonbfg_levels.txt',
                 DEST_DIR + 'mapinfo/doom2_secret_levels.txt')
        return
    
    d2wad.from_file(d2_wad_filename)
    
    # bfg version?
    if d2wad.graphics.get(BFG_ONLY_LUMP, None):
        copyfile(RES_DIR + 'mapinfo/doom2_bfg_levels.txt',
                 DEST_DIR + 'mapinfo/doom2_secret_levels.txt')
    else:
        copyfile(RES_DIR + 'mapinfo/doom2_nonbfg_levels.txt',
                 DEST_DIR + 'mapinfo/doom2_secret_levels.txt')
