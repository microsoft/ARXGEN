# ARXGEN: Corpus of Arxiv Articles for Deep Generative Models

ARXGEN offers a list of article-id from arxiv.org, scripts to download and post-process into a text corpus, to be used in text generation tasks.

# CITATION
<pre><code>@inproceedings{arxgen2018,
    title={ARXGEN: Corpus of Arxiv Articles for Deep Generative Models},
    author={Celikyilmaz, Asli, and Bosselut, Antoine and Shen, Dinghan},
    booktitle={https://github.com/Microsoft/ARXGEN},
    year={2018}
}</code></pre>

## Prerequisites

- ArXiv provides bulk data access through Amazon S3. You need an account with Amazon AWS to be able to download the data.
- python =2.7

## Download arxiv articles and parse to segment sections

#### Download arXiv Dump

1. Follow the instructions in https://github.com/acohan/arxiv-tools to get the arxiv dump. The `download.py` script will download a list of tar files from arXiv.

#### Extract Latex File from arXiv dump

1. Open `extract.py` and Change the values of read_dir/write_dir/latex_folder directories. 

2. Run ` python extract.py `. This will extract the latex files from the tar files.

#### Latex to Text

1. Open `parse.py` and Change the read/write directories. 

2. Run ` python parse.py` script to segment each article in latex format into sections and save as text files. All non-text components ( tables, images, lists, etc.) are removed with this script. 

#### Convert to tab delimited format

1. Create a new directory named `arxiv_latex`. Open `preprocess_latex.py` and change read_dir/write_dir directories values. 

2. Run `python preprocess_latex.py` script to remove unnecessary latex tags and reformat the segmented article text file into the tab delimited format.

#### Marge into single file

1. Collect all the processed data into one big text file 

    ```   
    cat arxiv_latex/* > all.txt
    ```

2. The above process will yield a large tab delimited text file named `all.txt` with the following headers:

    ```
    article-id
    article-title
    abstract
    introduction
    conclusion
    ```

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
