#!/usr/bin/python3
# Copyright (c) 2021 Kernighan
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

# Tool to convert songs made in 3MLE or imported
# into 3MLE from a MIDI file for use in Archeage.

import sys
import re
import os

cgi_mode = False

__version__ = "1.0.2"
__version_info__ = tuple([ int(num) for num in __version__.split('.')])

if bool(re.search(r'\.cgi$',sys.argv[0])) is True:
    cgi_mode = True

if cgi_mode:
    import cgi,cgitb
else:
    import argparse

octaves = {"o1": "o2",
           "o2": "o3",
           "o3": "o4",
           "o4": "o5",
           "o5": "o6",
           "o6": "o7",
           "o7": "o8"}


def strstr(strng, replace):
    buf, i = [], 0
    while i < len(strng):
        for s, r in replace.items():
            if strng[i:len(s)+i] == s:
                buf.append(r)
                i += len(s)
                break
        else:
            buf.append(strng[i])
            i += 1
    return ''.join(buf)

def fix_n_notes(strng):
    notes = ["c","c+","d","d+","e","f","f+","g","g+","a","a+","b"]
    buf, curoctave, i = [], 4, 0
    while i < len(strng):
        if strng[i] == "<":
            curoctave -= 1
        if strng[i] == ">":
            curoctave += 1
        if strng[i] == ",":
            curoctave = 4
        if strng[i] == "o":
            curoctave = int(strng[i+1])
        if strng[i] == "n":
            nbuf = []
            inc=1
            if strng[i+2].isdigit():
                if strng[i+3].isdigit():
                    nbuf.extend((strng[i+1],strng[i+2],strng[i+3]))
                    inc+=2
                else:
                    nbuf.extend((strng[i+1],strng[i+2]))
                    inc+=1
            else:
                nbuf.append(strng[i+1])
            nbuf = ''.join(nbuf)
            nbuf = int(nbuf)
            text_note = notes[nbuf %12]
            note_octave = nbuf//12
            note_shift = abs(note_octave - curoctave)
            upshift = ">" * note_shift
            downshift = "<" * note_shift
            if curoctave > note_octave:
                buf.append(downshift)
                buf.append(text_note)
                buf.append(upshift)
            else:
                buf.append(upshift)
                buf.append(text_note)
                buf.append(downshift)
            i+=inc
        else:
            buf.append(strng[i])
        i+=1
    return ''.join(buf)

def fix_length(strng):
    buf, i = [], 0
    curlen = 4
    new_track = 0
    while i < len(strng):
        if strng[i] == ",":
            new_track = 1
        if strng[i] == "l":
            lbuf = []
            if new_track == 1:
                new_track = 0
            if strng[i+2].isdigit():
                lbuf.extend((strng[i+1],strng[i+2]))
            else:
                lbuf.append(strng[i+1])
            lbuf = ''.join(lbuf)
            curlen = int(lbuf)
        if new_track == 1:
            if bool(re.search(r'[a-gr]',strng[i])) is True:
                if bool(re.search(r'[-\+]',strng[i+1])):
                    if not strng[i+2].isdigit():
                        if curlen != 4:
                            buf.append("l4")
                            curlen = 4
                        buf.append(strng[i])
                        new_track = 0
                    else:
                        buf.append(strng[i])
                elif not strng[i+1].isdigit():
                    if curlen != 4:
                        buf.append("l4")
                        curlen = 4
                    buf.append(strng[i])
                    new_track = 0
                else:
                    buf.append(strng[i])
            else:
                buf.append(strng[i])
        else:
            buf.append(strng[i])
        i += 1
    return ''.join(buf)

def fix_volume(strng):
    buf, i = [], 0
    while i < len(strng):
        if strng[i] == 'v':
            inc = 1
            vbuf = []
            if strng[i+2].isdigit():
                if strng[i+3].isdigit():
                    vbuf.extend((strng[i],strng[i+1],strng[i+2],strng[i+3]))
                    vbuf = ''.join(vbuf)
                    buf.append(vbuf)
                    i+=4
                    continue
                else:
                    vbuf.extend((strng[i+1],strng[i+2]))
                    inc+=1
            else:
                vbuf.append(strng[i+1])
            vbuf = ''.join(vbuf)
            volume = int (vbuf)
            if volume == 15:
                buf.append("v127")
            elif volume == 14:
                buf.append("v118")
            elif volume == 13:
                buf.append("v110")
            elif volume == 12:
                buf.append("v101")
            elif volume == 11:
                buf.append("v93")
            elif volume == 10:
                buf.append("v85")
            elif volume == 9:
                buf.append("v76")
            elif volume == 8:
                buf.append("v68")
            elif volume == 7:
                buf.append("v60")
            elif volume == 6:
                buf.append("v51")
            elif volume == 5:
                buf.append("v43")
            elif volume == 4:
                buf.append("v35")
            elif volume == 3:
                buf.append("v26")
            elif volume == 2:
                buf.append("v18")
            elif volume == 1:
                buf.append("v9")
            elif volume == 0:
                buf.append("v0")
            else:
                buf.append(strng[i])
                buf.append(vbuf)
            i+=inc
        else:
            buf.append(strng[i])
        i += 1
    return ''.join(buf)

content = ''
if cgi_mode:
    form = cgi.FieldStorage()

    if form.getvalue('nooctave'):
        nooctave = True
    if form.getvalue('novolume'):
        novolume = True
    if form.getvalue('mle'):
        content = form.getvalue('mle')
    else:
        content = False
else:
    parser = argparse.ArgumentParser()

    parser.add_argument('-v','--version', action='version',
                    version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('--nooctave', action="store_true", help="Skip octave fix")
    parser.add_argument('--novolume', action="store_true", help="Skip volume fix")
    parser.add_argument('-f','--infile', type=str, help='MML file to\
                        read in')

    args = parser.parse_args()
    if not args.infile:
        content = str(input("Enter MML code:\n"))

    else:
        mle = args.infile
        if not os.path.exists(mle):
            print("Error: File " + mle + " does not exist")
            sys.exit()

        with open(mle) as myfile:
            content = myfile.read()

if content is not False:
    content = content.strip("MML@") # Remove MML header

    # Use a transform to fix the volumes
    if content.find("v") > -1 and not args.novolume:
        #content = strstr(content, volumes)
        content = fix_volume(content)

    # N notes must be fixed before the octave transform is done
    if content.find("n") > -1:
        content = fix_n_notes(content)

    # Use a transform to fix the octaves
    if content.find("o") > -1 and not args.nooctave:
        content = strstr(content, octaves)

    # Fix default length in new tracks if it was altered in previous track
    if content.find("l") > -1:
        content = fix_length(content)

if cgi_mode:
    print("Content-type:text\r\n\r\n")
    print("<html>")
    print("<head>")
    print("<title>Converted MML code</title>")
    print("</head>")
    print("<body>")
    if content is not False:
        print("<code>")
        print("%s" % content)
        print("/<code>")
    else:
        print("<p>No MML provided</p>")
    print("</body>")
    print("</html>")
else:
    print(content)
