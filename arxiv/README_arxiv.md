# ARXGEN
ARXGEN: Corpus of Arxiv Articles for Deep Generative Models

ARXGEN offers a list of article-id from arxiv.org and scripts to download and post-process into a text corpus to be used in text generation tasks. 

# CITATION

@inproceedings{arxgen2018,
    title={ARXGEN: Corpus of Arxiv Articles for Deep Generative Models},
    author={Celikyilmaz, Asli, and Bosselut, Antoine and Shen, Dinghan},
    booktitle={https://github.com/Microsoft/ARXGEN/edit/master/arxiv/},
    year={2018}
}

## Prerequisites

-- ArXiv provides bulk data access through Amazon S3. You need an account with Amazon AWS to be able to download the data. You also need,

-- python 2+

## Download arxiv articles and parse to segment sections

-- Follow the instructions in https://github.com/acohan/arxiv-tools to get the arxiv.dump. The download.py script will download a list of tar files from arxiv.

-- Run 'extract.py' script to extract the latex files from the tar files. Change the read/write directories in the file before running.

    python extract.py
    
-- Run 'parse.py' script to segment each article in latex format into sections and save as text file. All non-text components (e.g., tables, images, lists, etc.) are removed with this script. Change the read/write directories in the file before running.
    
    python parse.py
    
-- Run 'preprocess_latex.py' scrip to remove unnecessary latext tags and reformat the segmented article text file into tab delimited format. Create a new directory 'arxiv_latex' and change the read/write directories in the preprocess_latex.py' scropt before running.

    python preprocess_latex.py
    
-- Collect all the processed data into one big text file 

    cat arxiv_latex/* > all.txt
   
The above process will yield a large text file named 'all.txt', which is a tab delimeted text file with the following headers:

    article-id
    article-title
    abstract
    introduction
    conclusion
    
