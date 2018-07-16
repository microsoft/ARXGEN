## by Asli Celikyilmaz
## Parse latex sections

## This scrip will segment the latex files into simple text documents segmented based on latex tags.

from os import listdir
import os
import re
import random
from simpleDelatex import *

read_dir = '/home/arxiv/latex' # input directory where the latex files reside.
write_dir = '/home/arxiv/latex_sec' # the directory to write the segmented latex as text format.

markers = set([])

alldirectories = listdir(read_dir)
random.shuffle(alldirectories)

count = 0
zero_count = 0

for dir in alldirectories:
    tempWriteDir = write_dir + dir
    try:
        in_files = listdir(read_dir+dir)

        if len(in_files):

            inputFile = read_dir+dir+"/"+in_files[0]

            outDir = write_dir+dir
            if not os.path.exists(outDir):
                os.makedirs(outDir)
            outFile = outDir +"/"+in_files[0] + ".sec"

            simpleLatexToText(inputFile, outFile, sectioned=True)

            count +=1

    except:
       print ("Can't process folder :" + str(tempWriteDir))

print ("Total : ", str(count))
