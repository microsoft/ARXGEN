## by Asli Celikyilmaz
## Extract tar files
## use the download.py under here to get the big dump from arxiv


import tarfile
from os import listdir
from os.path import isfile, join
import os
from shutil import copy, rmtree

read_dir =  '/home/arxiv/tars/' # directory that contains downloaded arxiv tar files
write_dir = '/home/dummy/' # temp directory to untar
latex_folder = '/home/arxiv/latex' # /media/aslicel/DATADRIVE2/arxiv/local-directory/arXivTex/

onlyfiles = [f for f in listdir(read_dir) if isfile(join(read_dir, f))]

num_corrupt = 0
num_noncorupt = 0

for f in onlyfiles:

    ## open the tar file
    if f.endswith("tar"):
        print (f)
        folder = f.split("_")[2]
        tar = tarfile.open(read_dir + f)
        tar.extractall(write_dir)
        tar.close()

        ## open the gzip files under the tar directory
        mypath = write_dir + folder + "/"
        onlyfiles_gz = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        try:
            for f_gz in onlyfiles_gz:
                if f_gz.endswith(".gz"):
                    try:
                        tar = tarfile.open(mypath + f_gz)
                        new_dir = mypath + f_gz.replace(".gz", "")
                        if not os.path.exists(new_dir):
                            os.makedirs(new_dir)
                        tar.extractall(new_dir)
                        tar.close()

                        ## now copy the latex file under here
                        mypath_inner = new_dir + "/"
                        onlytexfiles = [fi for fi in listdir(mypath_inner) if isfile(join(mypath_inner, fi))]
                        latex_folder_sub = latex_folder + "/" + f_gz.replace(".gz", "")
                        if not os.path.exists(latex_folder_sub):
                            os.makedirs(latex_folder_sub)

                        for f_tex in onlytexfiles:
                            if f_tex.endswith(".tex"):
                                copy(mypath_inner+f_tex, latex_folder_sub)

                        num_noncorupt += 1

                    except:
                        num_corrupt += 1
                        pass

            rmtree(mypath)
        except:
            pass


print ("Total : ", str(num_corrupt+num_noncorupt))
print ("Number of corrupted articles : " + str(num_corrupt))
print ("Number of non-corrupted articles : " + str(num_noncorupt))
