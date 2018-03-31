#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Program entry point"""

from __future__ import print_function

import argparse
import sys, os
import json
import wunderpy2

from wunderwarrior import metadata
from taskw import TaskWarrior

from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose

BANNER = """
Wunderwarrior v%s
wunderlist <==> taskwarrior sync
""" % metadata.version

class SyncController(CementBaseController):
    syncdb = {}
    access_token = 'foo'
    client_id = ''
    wunderlist = None
    taskw = None
    class Meta:
        label = 'base'
        arguments = [
            (['-V', '--version'], dict(action='version', version=BANNER)),
            (['-t', '--token-file'], dict(help='token file'))
        ]

    @expose(hide=True)
    def default(self):
        self.app.log.info('Run wunderwarrior --help for more info.')

    @expose(help="syncs ")
    def sync(self):
        self.app.log.info("Inside MyBaseController.command1()")
        self.connectWunderlist()

    def connectWunderlist(self):
        if self.app.pargs.token_file and os.path.exists(self.app.pargs.token_file):
            with open(self.app.pargs.token_file) as token_file:
                tokens = json.loads(token_file.read())
                self.access_token = tokens['accessToken']
                self.client_id = tokens['clientId']
                api = wunderpy2.WunderApi()
                self.wunderlist = api.get_client(self.access_token, self.client_id)
                lists = self.wunderlist.get_lists()
                wunderlist_tasks = []
                tasks = []
                for list in lists:
                    wunderlist_tasks += self.wunderlist.get_tasks(list['id'])
                print(wunderlist_tasks)
                self.taskw = TaskWarrior()
                tasks = self.taskw.load_tasks()
                print(tasks)
                
class Wunderwarrior(CementApp):
    class Meta:
        label = 'wunderwarrior'
        base_controller = 'base'
        handlers = [SyncController]

def main(argv):
    if(argv):
        sys.argv = argv
    with Wunderwarrior() as app:
        app.run()

def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
