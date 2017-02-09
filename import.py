#!/usr/bin/python
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
