# TODO: Rip skies from Freedoom 1 and 2
# TODO: Rip intermission graphics
# TODO: Use FD assets when neither doom 1 nor doom 2 are present
# TODO: Ask user if wants to use Doom's or FD's assets

import os, time
from shutil import copyfile
from zipfile import ZipFile, ZIP_DEFLATED
from modules.logg import LOG_FILENAME, NUM_ERRORS, logg, terminateLogg
from modules.masterlevels import extract_master_levels
from modules.wadtools import DEST_DIR, DEST_FILENAME, NUM_MAPS, RES_DIR, SRC_WAD_DIR, copy_resources, extract_iwad_maps, extract_lumps, get_wad_filename

import omg
from wadsmoosh_data import TIDY_DIR_EXTENSIONS

VERSION_FILENAME = 'version'

# if False, do a dry run with no actual file writing
should_extract = True

DATA_TABLES_FILE = 'wadsmoosh_data.py'

# forward-declare all the stuff in DATA_TABLES_FILE for clarity
RES_FILES = []
WADS = []
REPORT_WADS = []
COMMON_LUMPS = []
DOOM1_LUMPS = []
DOOM2_LUMPS = []
WAD_LUMP_LISTS = {}
WAD_MAP_PREFIXES = {}
MAP_NAME_GRAPHICS_DIRS = []
MASTER_LEVELS_PATCHES = {}
MASTER_LEVELS_SKIES = {}
MASTER_LEVELS_MUSIC = {}
MASTER_LEVELS_MAP07_SPECIAL = []
MASTER_LEVELS_AUTHOR_PREFIX = ''
MASTER_LEVELS_AUTHORS = {}
MASTER_LEVELS_MAPINFO_HEADER = []
SIGIL_ALT_FILENAMES = []
SIGIL2_ALT_FILENAMES = []

exec(open(DATA_TABLES_FILE).read())

def add_secret_exit(map_name, line_id):
    # sets given line # in given map as a secret exit switch
    wad = omg.WAD()
    wad_filename = DEST_DIR + 'maps/%s.wad' % map_name
    wad.from_file(wad_filename)
    ed = omg.MapEditor(wad.maps[map_name])
    ed.linedefs[line_id].__dict__['action'] = 51
    wad.maps[map_name] = ed.to_lumps()
    wad.to_file(wad_filename)

def add_secret_level(map_src_filename, map_src_name, map_dest_name):
    global NUM_MAPS
    # copies given map file into dest dir and sets its map lump name
    src_filename = get_wad_filename(map_src_filename)
    dest_filename = DEST_DIR + 'maps/%s.wad' % map_dest_name
    copyfile(src_filename, dest_filename)
    wad = omg.WAD()
    wad.from_file(dest_filename)
    wad.maps.rename(map_src_name, map_dest_name)
    wad.to_file(dest_filename)
    NUM_MAPS += 1

def add_xbox_levels():
    # :P
    logg('Adding Xbox bonus levels...')
    if get_wad_filename('doom'):
        logg('  Adding secret exit to E1M1')
        add_secret_exit('E1M1', 268)
        logg('  Adding SEWERS.WAD as E1M10')
        add_secret_level('sewers', 'E3M1', 'E1M10')
    if get_wad_filename('doom2'):
        logg('  Adding secret exit to MAP02')
        add_secret_exit('MAP02', 283)
        logg('  Adding BETRAY.WAD as MAP33')
        add_secret_level('betray', 'MAP01', 'MAP33')

def get_report_found():
    found = []
    
    # Checks if any of the supported wads are present
    # first loops REPORT_WADS (which comes from wadsmoosh_data.py)
    # and check if the file exist, if it does... save
    # it to the 'found' array above

    for wadname in REPORT_WADS: 
        if get_wad_filename(wadname):
            found.append(wadname)
    
    # Some games needs special treatment because they have
    # multiple filenames or depends on a game (example Sigil
    # depends on Doom I)
            
    # SIGIL_ALT_FILENAMES comes from wadsmoosh_data.py
    
    # look for sigil by other names
    if 'doom' in found and not 'sigil' in found:
        for alt_name in SIGIL_ALT_FILENAMES:
            sigil_alt = get_wad_filename(alt_name)
            
            # rather than handle variable filename for it, just create
            # a copy in source_wads/ with the expected name
            if sigil_alt:
                copyfile(sigil_alt, SRC_WAD_DIR + 'sigil.wad')
                found.insert(1, 'sigil')
                break

    # same with sigil2
    # (TODO maybe some way to generalize this for future releases?)
    if 'doom' in found and not 'sigil2' in found:
        for alt_name in SIGIL2_ALT_FILENAMES:
            sigil2_alt = get_wad_filename(alt_name)
            if sigil2_alt:
                copyfile(sigil2_alt, SRC_WAD_DIR + 'sigil2.wad')
                found.insert(2, 'sigil2')
                break

    # Once we have everything, return the array and move on!
    return found

def get_eps(wads_found):
    eps = []

    for wadname in wads_found:
        if wadname == 'doom':
            eps += ['Knee Deep in the Dead', 'The Shores of Hell', 'Inferno', 'Thy Flesh Consumed']
        elif wadname == 'doom2':
            eps += ['Hell on Earth']
        elif wadname == 'nerve' and 'doom2' in wads_found: # Check if Doom 1 / 2 is present in wads_found before presenting it to the user
            eps += ['No Rest for the Living']
        elif wadname == 'attack' and 'doom2' in wads_found:
            eps += ['The Master Levels']
        elif wadname == 'tnt':
            eps += ['TNT: Evilution']
        elif wadname == 'plutonia':
            eps += ['The Plutonia Experiment']
        elif wadname == 'sigil' and 'doom' in wads_found:
            eps += ['Sigil']
        elif wadname == 'sigil2' and 'doom' in wads_found:
            eps += ['Sigil II']
        elif wadname == 'freedoom1' and 'doom' in wads_found:
            eps += ['Freedoom: Phase I']
        elif wadname == 'freedoom2' and 'doom2' in wads_found:
            eps += ['Freedoom: Phase II']

    return eps

# Main app
def main():
    # Start tracking time
    start_time = time.time()
    
    # Read 'version' file and print app name, version and the underline
    version = open(VERSION_FILENAME).readlines()[0].strip()
    title_line = 'WadSmoosh v%s' % version
    logg(title_line + '\n' + '-' * len(title_line)) 
    
    # Populate found with all wads present in source_wads folder
    found = get_report_found()

    input_func = input
    
    # bail if no wads in SRC_WAD_DIR
    if len(found) == 0:
        logg('No source WADs found!\nPlease place your WAD files into %s.' % os.path.realpath(SRC_WAD_DIR))
        terminateLogg()
        input_func('Press Enter to exit.\n')
        return
    
    # clear out pk3 dir from previous runs
    files_tidied = 0

    # TIDY_DIR_EXTENSIONS comes from wadsmoosh_data.py and it contains
    # all the folders and extensions to be deleted in tuples (directory, array of extensions)

    for dirname,extensions in TIDY_DIR_EXTENSIONS.items():
        if not os.path.exists(DEST_DIR + dirname): # If the folder does not exist, move on
            continue

        for filename in os.listdir(DEST_DIR + dirname):
            for ext in extensions:
                if filename.endswith(ext):
                    filename = DEST_DIR + dirname + filename
                    if os.path.exists(filename):
                        os.remove(filename)
                        files_tidied += 1

    # clear out files in pk3 base dir too
    for filename in RES_FILES:
        
        # don't touch subdirs
        if filename != os.path.basename(filename):
            continue
        
        filename = DEST_DIR + filename
        
        if os.path.exists(filename):
            os.remove(filename)
            files_tidied += 1
    
    if files_tidied > 0:
        logg('Removed %s files from a previous run.' % files_tidied)
    
    # Report all wads found in source_dir
    logg('Found in %s:\n  ' % SRC_WAD_DIR + ', '.join(found))
    
    print('\n\nA new PK3 format IWAD will be generated with the following episodes:')
    
    # Print all episodes that are going to be available and
    # store the number of episodes in num_eps for later
    for num_eps,ep_name in enumerate(get_eps(found)):
        print('- %s' % ep_name)
    
    num_eps += 1
    
    # Ask user for input
    i = input_func('\n\nPress Y and then Enter to proceed, anything else to cancel: ')
    
    # User inputted other than 'y'? Stop logging and close app
    if i.lower() != 'y':
        logg('Canceled.')
        terminateLogg()
        return
    
    # make dirs if they don't exist
    if not os.path.exists(DEST_DIR):
        os.mkdir(DEST_DIR)
    for dirname in ['flats', 'graphics', 'music', 'maps', 'mapinfo',
                    'patches', 'sounds', 'sprites']:
        if not os.path.exists(DEST_DIR + dirname):
            os.mkdir(DEST_DIR + dirname)
    
    # copy pre-authored lumps eg mapinfo
    if should_extract:
        copy_resources()

    # if final doom present but not doom1/2, extract doom2 resources from it
    if get_wad_filename('tnt') and not get_wad_filename('doom2'):
        WAD_LUMP_LISTS['tnt'] += DOOM2_LUMPS # Append lumps that were to be extracted from Doom2 to be extracted from TNT

    # if doom 1 also isn't present (weird) extract all common resources
    if not get_wad_filename('doom'):
        WAD_LUMP_LISTS['tnt'] += COMMON_LUMPS # Append lumps that were to be extracted from Doom1 to also be extracted from TNT
    
    # extract lumps and maps from wads
    for iwad_name in WADS:
        wad_filename = get_wad_filename(iwad_name)

        # First, check if theres any error or missing file?
        if not wad_filename:
            logg('WAD %s not found' % iwad_name)
            continue
        if iwad_name == 'nerve' and not get_wad_filename('doom2'):
            logg('Skipping nerve.wad as doom2.wad is not present', error=True)
            continue
        if iwad_name == 'sigil' and not get_wad_filename('doom'):
            logg('Skipping SIGIL.wad as doom.wad is not present', error=True)
            continue
        if iwad_name == 'sigil_shreds' and not get_wad_filename('sigil'):
            logg('Skipping SIGIL_SHREDS.wad as SIGIL.wad is not present', error=True)
            continue
        if iwad_name == 'sigil2' and not get_wad_filename('doom'):
            logg('Skipping sigil2.wad as doom.wad is not present', error=True)
            continue
        
        logg('Processing WAD %s...' % iwad_name)

        if should_extract:
            extract_lumps(iwad_name)
            
            prefix = WAD_MAP_PREFIXES.get(iwad_name, None) # None is assigned as an initial value
            # check None, not empty string! [nathan-hyan says: This is necessary since there are map prefixes that are empty strings (sigil and sigil II)]
            if prefix is not None:
                extract_iwad_maps(iwad_name, prefix)
    
    if get_wad_filename('doom2'):
        if should_extract:
            extract_master_levels()
    else:
        logg('Skipping Master Levels as doom2.wad is not present', error=True)
    
    # only supported versions of these @ http://classicdoom.com/xboxspec.htm
    # TODO: Ask and download these files automatically

    if get_wad_filename('sewers') and get_wad_filename('betray') and should_extract:
        add_xbox_levels()

    # copy custom GENMIDI, if user hasn't deleted it
    genmidi_filename = 'GENMIDI.lmp'
    if os.path.exists(RES_DIR + genmidi_filename):
        logg('Copying %s' % genmidi_filename)
        copyfile(RES_DIR + genmidi_filename, DEST_DIR + genmidi_filename)
    
    # create pk3
    logg('Compressing %s...' % DEST_FILENAME)
    
    pk3 = ZipFile(DEST_FILENAME, 'w', ZIP_DEFLATED)
    for dir_name, x, filenames in os.walk(DEST_DIR):
        for filename in filenames:
            src_name = dir_name + '/' + filename
            # exclude pk3/ top dir from name within archive
            dest_name = src_name[len(DEST_DIR):]
            pk3.write(src_name, dest_name)
    pk3.close()
    logg('Done!')

    # Stop tracking elapsed time
    elapsed_time = time.time() - start_time

    # Get full size
    ipk3_size =  os.path.getsize(DEST_FILENAME) / 1000000
    
    # Display results to the user
    logg('Generated %s (%.1f MB) with %s maps in %s episodes in %.2f seconds.' % (DEST_FILENAME, ipk3_size, NUM_MAPS, num_eps, elapsed_time))
    
    # Report errors
    if NUM_ERRORS > 0:
        logg('%s errors found, see %s for details.' % (NUM_ERRORS, LOG_FILENAME))
    input_func('Press Enter to exit.\n')
    
    # Stop logging
    terminateLogg()

if __name__ == "__main__":
    main()
