#!/usr/bin/python

"""
Shifter, Copyright (c) 2015, The Regents of the University of California,
through Lawrence Berkeley National Laboratory (subject to receipt of any
required approvals from the U.S. Dept. of Energy).  All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
 1. Redistributions of source code must retain the above copyright notice,
    this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.
 3. Neither the name of the University of California, Lawrence Berkeley
    National Laboratory, U.S. Dept. of Energy nor the names of its
    contributors may be used to endorse or promote products derived from this
    software without specific prior written permission.`

See LICENSE for full text.
"""

# This is the mongo side of the importer.
# This basically constructs the mongo record and adds it
# in.

import time
import sys
from pymongo import MongoClient

sysname = sys.argv[1]
format = sys.argv[2]
fh = sys.argv[3]
tag = sys.argv[4]

image = {'status': 'READY',
         'format': format,
         'ostcount': '0',
         'replication': '1',
         'itype': 'custom',
         'system': sysname,
         'remotetype': 'custom',
         'last_pull': time.time(),
         'id': fh,
         'tag': [tag],
         'arch': 'amd64',
         'groupAcl': [],
         'userAcl': [],
         'location': '',
         'os': 'linux',
         'expiration': time.time() + 3600 * 24 * 60,
         }

client = MongoClient('mongo')
images = client.Shifter.images

# Look for duplicate
i = images.find_one({'system': sysname, 'itype': 'custom', 'id': fh})
if i is not None:
    print "This id already exist"
    sys.exit(1)

# Remove old tags
images.update({'system': sysname, 'tag': {'$in': [tag]}},
              {'$pull': {'tag': tag}}, multi=True)

# Add new image
images.insert(image)

print images.find_one({'system': sysname, 'tag': {'$in': [tag]}})
