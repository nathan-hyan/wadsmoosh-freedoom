import os
import sys
from modules.logg import logg
from modules.wadtools import DEST_DIR, extract_map, get_wad_filename
import omg
from wadsmoosh_data import MASTER_LEVELS_AUTHOR_PREFIX, MASTER_LEVELS_AUTHORS, MASTER_LEVELS_CLUSTER_DEF, MASTER_LEVELS_MAP07_SPECIAL, MASTER_LEVELS_MAPINFO_HEADER, MASTER_LEVELS_MUSIC, MASTER_LEVELS_PATCHES, MASTER_LEVELS_SECRET_DEF, MASTER_LEVELS_SKIES, WAD_MAP_PREFIXES

MASTER_LEVELS_MAP_PREFIX = WAD_MAP_PREFIXES.get('masterlevels', '')
ML_ORDER_FILENAME = 'masterlevels_order_xaser.txt'
ML_MAPINFO_FILENAME = DEST_DIR + 'mapinfo/masterlevels.txt'


def get_master_levels_map_order():
    order = []
    if len(sys.argv) > 1:
        order_file = ' '.join(sys.argv[1:])
        if not os.path.exists(order_file):
            order_file = ML_ORDER_FILENAME
    else:
        order_file = ML_ORDER_FILENAME
    if not os.path.exists(order_file):
        return order_file, []
    logg('Using Master Levels ordering from %s' % order_file)
    for line in open(order_file).readlines():
        line = line.strip().lower()
        if line.startswith('//') or line == '':
            continue
        if not line in MASTER_LEVELS_MUSIC:
            logg('ERROR: Unrecognized Master Level %s' % line, error=True)
            continue
        order.append(line)
    return order_file, order

def get_ml_mapinfo(wad_name, map_number):
    lines = []
    prefix = MASTER_LEVELS_MAP_PREFIX.upper()
    mapnum = str(map_number).rjust(2, '0')
    nextnum = str(map_number + 1).rjust(2, '0')
    
    lines.append('map %sMAP%s lookup "%s%s"' % (prefix, mapnum, prefix, wad_name.upper()))
    lines.append('{')
    
    next_map = '%sMAP%s' % (prefix, nextnum) if map_number < 20 else 'EndGameC'
    sky = MASTER_LEVELS_SKIES.get(wad_name, None) or 'RSKY1'
    music = MASTER_LEVELS_MUSIC[wad_name]
    author_lc = '%s_%s' % (MASTER_LEVELS_AUTHOR_PREFIX, MASTER_LEVELS_AUTHORS[wad_name])
    
    lines.append('    next = "%s"' % next_map)
    
    if wad_name == 'teeth':
        lines.append('    secretnext = "ML_MAP21"')

    lines.append('    sky1 = "%s"' % sky)
    lines.append('    music = "$MUSIC_%s"' % music)

    # (cluster # is defined in MASTER_LEVELS_MAPINFO_HEADER)
    lines.append('    Author = "$%s"' % author_lc)
    if wad_name in MASTER_LEVELS_MAP07_SPECIAL:
        lines.append('    map07special')
    
    # don't reset player for secret level
    if map_number != 21:
        lines.append('    ResetHealth')
        lines.append('    ResetInventory')

    lines.append('}')
    return lines

def extract_master_levels():
    # check if present first
    order_file, ml_map_order = get_master_levels_map_order()
    if len(ml_map_order) == 0:
        return
    first_ml_wad = get_wad_filename(ml_map_order[0])
    if not first_ml_wad:
        logg('ERROR: Master Levels not found.', error=True)
        return
    logg('Processing Master Levels...')
    mapinfo = open(ML_MAPINFO_FILENAME, 'w')
    mapinfo.write(MASTER_LEVELS_MAPINFO_HEADER % order_file)
    for i,wad_name in enumerate(ml_map_order):
        in_wad = omg.WAD()
        wad_filename = get_wad_filename(wad_name)
        if not wad_filename:
            logg("ERROR: Couldn't find %s" % wad_name, error=True)
            continue
        in_wad.from_file(wad_filename)
        out_wad_filename = DEST_DIR + 'maps/' + MASTER_LEVELS_MAP_PREFIX + 'map'
        # extra zero for <10 map numbers, eg map01
        out_wad_filename += str(i + 1).rjust(2, '0') + '.wad'
        logg('  Extracting %s to %s' % (wad_filename, out_wad_filename))
        # grab first map we find in each wad
        map_name = in_wad.maps.find('*')[0]
        extract_map(in_wad, map_name, out_wad_filename)
        # write data to mapinfo based on ordering
        mapinfo.writelines('\n'.join(get_ml_mapinfo(wad_name, i+1)))
        mapinfo.write('\n\n')
    # save teeth map32 to map21
    wad_filename = get_wad_filename('teeth')
    out_wad_filename = DEST_DIR + 'maps/' + MASTER_LEVELS_MAP_PREFIX + 'map21' + '.wad'
    logg('  Extracting %s map32 to %s' % (wad_filename, out_wad_filename))
    in_wad = omg.WAD()
    in_wad.from_file(wad_filename)
    extract_map(in_wad, in_wad.maps.find('*')[1], out_wad_filename)
    # write map21 mapinfo
    if ml_map_order.index('teeth') == 19:
        next_map = 'EndGameC'
    else:
        next_map = '%sMAP%s' % (MASTER_LEVELS_MAP_PREFIX.upper(),
                                ml_map_order.index('teeth') + 2)
    mapinfo.write(MASTER_LEVELS_SECRET_DEF % (next_map, MASTER_LEVELS_MUSIC['teeth2'],
                                              MASTER_LEVELS_AUTHOR_PREFIX, MASTER_LEVELS_AUTHORS['teeth2']))
    # finish mapinfo
    mapinfo.writelines([MASTER_LEVELS_CLUSTER_DEF])
    mapinfo.close()
    # extract sky lumps
    for wad_name,patch_replace in MASTER_LEVELS_PATCHES.items():
        wad = omg.WAD()
        wad_filename = get_wad_filename(wad_name)
        wad.from_file(wad_filename)
        # manor stores sky in patches namespace, combine and virgil don't
        if patch_replace[0] in wad.data:
            lump = wad.data[patch_replace[0]]
        else:
            lump = wad.patches[patch_replace[0]]
        out_filename = DEST_DIR + 'patches/' + patch_replace[1] + '.lmp'
        logg('  Extracting %s lump from %s as %s' % (patch_replace[0],
                                                   wad_filename,
                                                   patch_replace[1]))
        lump.to_file(out_filename)