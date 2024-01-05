NUM_ERRORS = 0
LOG_FILE = None
LOG_FILENAME = 'wadsmoosh.log'

def logg(line, error=False):
    global LOG_FILE, NUM_ERRORS
    if not LOG_FILE:
        LOG_FILE = open(LOG_FILENAME, 'w')
    print(line)
    LOG_FILE.write(line + '\n')
    if error:
        NUM_ERRORS += 1

def terminateLogg():
    LOG_FILE.close()