#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'locasploit.update.cve'
        self.short_description = 'Updates CVE database.'
        self.references = [
            '',
        ]
        
        self.date = '2016-10-25'
        self.license = 'GNU GPLv2'
        self.version = '0.0'
        self.tags = [
            'locasploit',
            'update',
            'CVE',
            'CPE',
        ]
        self.description = """
This module checks https://nvd.nist.gov/download.cfm for modified CVE entries and alters local database accordingly.
This should be run frequently, as the list of modified entries is being held for up to 8 days.
"""
        
        self.dependencies = {
        }
        self.changelog = """
"""

        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'BACKGROUND' : Parameter(value='yes', mandatory=True, description='yes = run in background, no = wait for it...'),
            #'TIMEOUT' : Parameter(value='5', mandatory=True, description='Number of seconds to wait'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        result = CHECK_PROBABLY
        # check parameters
        silent = positive(self.parameters['SILENT'].value)
        if not positive(self.parameters['BACKGROUND'].value) and not negative(self.parameters['BACKGROUND'].value):
            if not silent:
                log.err('Bad %s value: %s.', 'BACKGROUND', self.parameters['BACKGROUND'].value)
            result = CHECK_FAILURE
        #if not self.parameters['TIMEOUT'].value.isdigit() or int(self.parameters['TIMEOUT'].value) < 0:
        #    if not silent:
        #        log.err('Bad timeout value: %d', int(self.parameters['TIMEOUT'].value))
        #    result = CHECK_FAILURE
        # can import urlib?
        try:
            from urllib.request import urlretrieve
        except:
            if not silent:
                log.err('Cannot import urllib.request library (urllib5).')
            # TODO other ways?
            result = CHECK_FAILURE

        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value) 
        # # # # # # # #
        #t = Thread(silent, int(self.parameters['TIMEOUT'].value))
        t = Thread(silent)
        t.start()
        if positive(self.parameters['BACKGROUND'].value):
            return t
        t.join()
        # # # # # # # #
        return None
    
        
class Thread(threading.Thread):
    def __init__(self, silent): #,timeout):
        threading.Thread.__init__(self)
        self.silent = silent
        #self.timeout = timeout
        self.terminate = False
            
    # starts the thread
    def run(self):
        from datetime import datetime
        # TODO check self.terminate somewhere!
        if self.terminate:
            pass
        from urllib.request import urlretrieve
        last = lib.db['vuln'].get_property('last_update')
        print(last)

        m = lib.modules['locasploit.update.cve-year']
        m.parameters['BACKGROUND'].value = 'no'
        last_update = lib.db['vuln'].get_property('last_update')
        if last_update != DB_ERROR and (datetime.now() - datetime.strptime(last_update, '%Y-%m-%d')).days < 8:
            log.info('Entries have been updated less than 8 days ago, checking Modified feed only...')
            m.parameters['YEARS'].value = 'Modified'
        else:
            log.info('Entries have been updated more than 8 days ago, checking all feeds for change...')
            m.parameters['YEARS'].value = ' '.join(map(str, range(2002, datetime.now().year+1)))
        m.run()
        # check last date in db (key-value table?)
        # if < 8 days: get modified
        #              update db
        #              set last_update
        #
        # else:        download everything
        #              update years where sha1 does not match
        #              get actual checksum of 'modified'
    # terminates the thread
    def stop(self):
        self.terminate = True
    

lib.module_objects.append(Module())
