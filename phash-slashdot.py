#!/usr/bin/python

#The MIT License (MIT)
#
#Copyright (c) <year> <copyright holders>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#

import sys
import os
import re
import shutil
import time
 
from PIL import Image,ImageStat,ImageOps
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--directory", dest="directory",help="directory to hash")
parser.add_option("-t", "--threshold", dest="threshold",default=5,help="threshold")
parser.add_option("-v","--verbose", action="store_true",dest="verbose",default=False,help="Output More Things")

(options, args) = parser.parse_args()

EXTS = 'jpg', 'jpeg','gif', 'png','bmp'

def hamming(h1, h2):
    diffs = 0
    for ch1,ch2 in zip(h1,h2):
        if ch1!=ch2:
            diffs+=1
    return diffs
    

def avhash(im):
    #im = Image.open(im)
    im = im.resize((8, 8), Image.ANTIALIAS).convert('L')
    avg = reduce(lambda x, y: x + y, im.getdata()) / 64.
    data = reduce(lambda x, (y, z): x | (z << y),enumerate(map(lambda i: 0 if i < avg else 1, im.getdata())),0)
    newdata = str(bin(data))[2:].zfill(64)
    return newdata

phash = {}
sizes = {}
for path, dirs, files in os.walk(options.directory):
    for file in files:
        filename = os.path.normpath(path + "/" + file)
        extension = os.path.splitext(filename)[1][1:]
        if extension.lower() in EXTS:
            try:
                im = Image.open(filename)
            except:
                print "Image filename doesn't exist"
            (width,height) = im.size
            sizes[filename] = (width,height)            
            h = avhash(im)
            if options.verbose:
              print "PHASH:",h,filename
            if h not in phash.keys():
                phash[h] = []
            phash[h].append(filename)

hashes = phash.keys()
hashcount = len(hashes)
final_output={}
for lcv in phash:
  if len(phash[lcv]) > 1:
    if not final_output.has_key(0):
      final_output[0] = []
    final_output[0].append(phash[lcv])

for lcv in xrange(hashcount):
    for sublcv in xrange(lcv+1,hashcount):
        hd = hamming(hashes[lcv],hashes[sublcv])
        output = []
        for file in phash[hashes[lcv]]:
            output.append(file)
        for file in phash[hashes[sublcv]]:
            output.append(file)
        if not final_output.has_key(hd):
            final_output[hd] = []
        final_output[hd].append(output)

if options.verbose:
  print ""

counter = 0
for hamming_distance in range(0,65):
    if not final_output.has_key(hamming_distance):
        continue
    if hamming_distance > options.threshold:
        continue
    for files in final_output[hamming_distance]:
        counter += 1
        for file in files:
            (x,y) = sizes[file]
            print "Group: %2d\tPhash Hamming Distance: %2d\tSize: %4d x %4d\t%s" % (counter,hamming_distance,x,y,file)
        print ""
