#!/usr/bin/env python


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

#
# This is used to import images directly from the file system.
# This is the user side of the script.  It calls the importer.py which
# should have access to the mongo databse.  The ssh could be skipped if both
# are running on the same system.

# This script hashes the file, copies the data, generates a metafile and
# then calls the importer to create the mongo record.
#
import json
import os
import sys
import hashlib
import subprocess


images = None
config = None

command = ['./import.py']
#If the database part needs to run remotely
#command = ["ssh","user@host","-p","2222"]


def init(configfile):
    global images
    global config

    with open(configfile) as cf:
        config = json.load(cf)


def fasthash(file):
    m = hashlib.sha256()
    with open(file, 'rb', 1024 * 1024) as f:
        l = f.read(1024 * 1024)
        while (len(l) > 0):
            m.update(l)
            f.seek(1024 * 1024 * (512 - 1), 1)
            l = f.read(1024 * 1024)

    return m.hexdigest()


def copy(source, imageFilename, system):
    local = system['local']
    targetFilename = os.path.join(local['imageDir'], imageFilename)
    cpCmd = ['cp']
    if 'cpCmdOptions' in system:
        cpCmd.extend(system['cpCmdOptions'])
    # TODO: Add command to pre-create the file with the right striping
    cpCmd.extend([source, targetFilename])
    #print "DEBUG: %s"%(scpCmd.join(' '))
    if os.path.exists(targetFilename):
        print "Warning: target file exist.  Skipping Copy."
        return -1
    ret = subprocess.call(cpCmd)  # , stdout=fdnull, stderr=fdnull)
    return ret == 0


def write_meta(id, system, format):
    print "Writing meta file"
    local = system['local']
    filename = os.path.join(local['imageDir'], '%s.meta' % id)
    with open(filename, 'w') as f:
        f.write("FORMAT: %s\n" % (format))

def main():
    if len(sys.argv) != 5:
        print "Usage: importer <sysname> <image file> <squashfs|ext4> <tag>"
        sys.exit(1)
    sysname = sys.argv[1]
    image = sys.argv[2]
    format = sys.argv[3]
    tag = sys.argv[4]

    print "System: " + sysname
    configfile = '/etc/imagemanager.json'
    if 'CONFIG' in os.environ:
            configfile = os.environ['CONFIG']
    init(configfile)
    #mgr=imagemngr.imagemngr(config)
    system = config['Platforms'][sysname]
    #for i in images.find():
    #   print i
    fh = fasthash(image)
    print "hash: %s" % (fh)
    #to test check
    #fh='2bc6cdd62ffb5472d95fa74ce960fec49a5877e8ea7d2dd453d5ae90e773ecf3'
    #

    # Copy image to locationS
    copy(image, "%s.%s" % (fh, format), system)

    write_meta(fh, system, format)

    command.extend([sysname, format, str(fh), tag])
    print 'Running: ' + ' '.join(command)
    subprocess.call(command)


if __name__ == '__main__':
    main()
