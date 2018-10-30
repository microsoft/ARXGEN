## by Asli Celikyilmaz

## Preprocess the segmented latex articles and convert into tab delimeted text file with the following columns:
## -- Article-ID
## -- Title
## -- Abstract
## -- Introduction
## -- Conclusion


from os import listdir
import re
import random
import datetime

def clean_starting(input):
    if str.startswith(input.lower().strip().replace(' ', '').replace('*',''), '{introduction}'):
        return None
    if str.startswith(input.lower().strip().replace(' ', '').replace('*',''), '{conclusion}'):
        return None
    if str.startswith(input.lower().strip().replace(' ', '').replace('*',''), '{acknowledgments}'):
        return None
    if str.startswith(input.lower().strip().replace(' ', '').replace('*',''), '{appendix}'):
        return None
    if len(input.strip().split(' ')) <= 1:
        return None
    return input
#
def clean_processed_latex(input):
    sweep_these = {' ~()', ' ~( )', '"', '``', '\'\'','(see figure)',
                   '---', '--', '...', '{ etc}', '{etc}', '{et. al.}', '{viz.}', 'Ref.~[ ]', '{}', '{ }', '{  }', '[]', '[ ]', '[  ]','[...]',
                   '()', '( )', '(  )', '{', '}'}
    out_str = input
    for dl in sweep_these:
        out_str = out_str.replace(dl, '', re.IGNORECASE)

    possible_urls = re.findall(r'\S+:\S+', out_str)

    for dl in possible_urls:
        out_str = out_str.replace(dl, '')

    return out_str

def clean_citings(input):
    out_str = input

    regexpSTR1 = r'^(.*)?(~{.*?};?)(.*)?'
    regexpSTR2 = r'^(.*)?(\([ ]?~{.*?};?[ ]?\)?)(.*)?'
    regexpSTR3 = r'^(.*)?(~{.*?};?)(.*)?'


    regs = [regexpSTR2, regexpSTR3, regexpSTR1]

    for reg in regs:
        regexp = re.match(reg, out_str, re.I)

        while regexp:
            left = regexp.group(1)
            start = regexp.group(2)
            block = regexp.group(3)

            out_str = left.strip() + " " + block

            regexp = re.match(reg, out_str, re.I)

        out_str = out_str.replace("(Fig. )", "")

    return out_str

def start_section_match(input):
    ###start section title###
    reg = r'.*##.*start section title.*##.*'
    str = input.lower()
    regexp = re.match(reg, str,  re.I)

    if regexp:
        return 't'

    reg = r'.*##.*start section abstract.*##.*'
    regexp = re.match(reg, str, re.I)
    if regexp:
        return 'a'

    reg = r'.*##.*start section introduction.*'
    regexp = re.match(reg, str, re.I)
    if regexp:
        return 'i'

    reg = r'.*##.*start section conclusion.*##.*'
    regexp = re.match(reg, str, re.I)
    if regexp:
        return 'c'

    reg = r'.*##.*start section.*'
    regexp = re.match(reg, str, re.I)
    if regexp:
        return 'o'

    reg = r'.*##start dummy section.*##.*'
    regexp = re.match(reg, str, re.I)
    if regexp:
        return 'o'

    return None

read_dir = "/home/aslicel/data/arxiv/outParseSection/outParseSection"
write_dir = "/home/aslicel/data/arxiv/sil" #"/home/aslicel/data/arxiv/arxiv_all"

file_count = 1
writeme = open(write_dir + "/f" + str(file_count), "w")

alldirectories = listdir(read_dir)

print("len files:" + str(len(alldirectories)))

count = 1
all_count = 0
fmt = '%Y-%m-%d %H:%M:%S'
d1 = datetime.datetime.now().replace(microsecond=0)
line_to_write = ''

alldirectories.sort()

for i in range(len(alldirectories)):
    dir = alldirectories[i]

    tempWriteDir = write_dir + "/" + dir

    try:
        in_files = listdir(read_dir+ "/" + dir)

        r=random.random()
        if len(in_files):

            ## if you want to add the article categories in the text file as an additional column,
            ## uncomment the following and append the category_term to the line_to_write in #line 237!
            ## WARNING: If you uncomment the following to get the categories, it slows down the process drastically.!!!! We used a farm of parallel machines to add the category_term in a reasonable time!

            # url = baseurl + 'search_query=id:' + dir + '&start=0&max_results=1'
            # response = urllib.request.urlopen(url).read()
            # feed = feedparser.parse(response)
            # if len(feed.entries):
            #     category_term = feed.entries[0].arxiv_primary_category['term']
            # else:
            #     continue

            all_count += 1
            inputFile = read_dir+ "/" + dir+"/"+in_files[0]

            fin = open(inputFile)
            lines = fin.readlines()
            fin.close()

            current = None
            introduction = []
            abstract = []
            conclusion = []
            title = []

            for line in lines:
                res = start_section_match(line)
                if res == 't':
                    current = 't'

                elif res == 'a':
                    current = 'a'

                elif res == 'i':
                    current = 'i'

                elif res == 'c':
                    current = 'c'

                elif res == 'o':
                    current = 'o'

                elif res == None:
                    if current == 't':
                        l = clean_starting(line)
                        if l:
                            l = clean_citings(l)
                            l = clean_processed_latex(l)
                            title.append(l)
                    if current == 'a':
                        l = clean_starting(line)
                        if l:
                            l = clean_citings(l)
                            l = clean_processed_latex(l)
                            abstract.append(l)
                    if current == 'i':
                        l = clean_starting(line)
                        if l:
                            l = clean_citings(l)
                            l = clean_processed_latex(l)
                            introduction.append(l)
                    if current == 'c':
                        l = clean_starting(line)
                        if l:
                            l = clean_citings(l)
                            l = clean_processed_latex(l)
                            conclusion.append(l)

            # if len(abstract) == 0 or len(introduction) == 0 or len(conclusion) == 0 or len(title) == 0:
            #     continue


            if len(abstract) > 0:
                abstract = [t.replace('.\n', ' <p>').replace('!\n', ' <p>').replace('?\n', ' <p>').replace('. \n',' <p>').replace('! \n', ' <p>').replace('? \n', ' <p>') for t in abstract]
                abstract = [t.replace('\n', ' ') for t in abstract]
                abstract = ' '.join(abstract).replace('  ', ' ')
            else:
                abstract = ''

            if len(title) > 0:
                title = [t.replace('.\n', ' <p>').replace('!\n', ' <p>').replace('?\n', ' <p>').replace('. \n', ' <p>').replace('! \n', ' <p>').replace('? \n', ' <p>') for t in title]
                title = [t.replace('\n', ' ') for t in title]
                title = ' '.join(title).replace('  ', ' ')
            else:
                title = ''

            if len(introduction) > 0:
                introduction = [t.replace('.\n', ' <p>').replace('!\n', ' <p>').replace('?\n', ' <p>').replace('. \n', ' <p>').replace('! \n', ' <p>').replace('? \n', ' <p>') for t in introduction]
                introduction = [t.replace('\n', ' ') for t in introduction]
                introduction = ' '.join(introduction).replace('  ', ' ')
            else:
                introduction = ''

            if len(conclusion) > 0:
                conclusion = [t.replace('.\n', ' <p>').replace('!\n', ' <p>').replace('?\n', ' <p>').replace('. \n', ' <p>').replace('! \n', ' <p>').replace('? \n', ' <p>') for t in conclusion]
                conclusion = [t.replace('\n', ' ') for t in conclusion]
                conclusion = ' '.join(conclusion).replace('  ', ' ')
            else:
                conclusion = ''

            count +=1

            # line_to_write += dir + "\t" + category_term + "\t" + title + "\t" + abstract + "\t" + introduction + "\t" + conclusion + "\n"
            line_to_write += dir + "\t" + title + "\t" + abstract + "\t" + introduction + "\t" + conclusion + "\n"

            if count % 1000 == 0:
                print('f-', str(file_count))
                writeme.write(line_to_write)
                writeme.close()

                file_count += 1
                writeme = open(write_dir + "/f" + str(file_count), "w")
                line_to_write = ''

    except Exception as ex:
       print("exception : " + str(ex))
       print ("Can't process folder :" + str(dir))

writeme.write(line_to_write)
writeme.close()
print("finiished count-" + str(count) + " file-" + str(file_count))

print ("Total read " , str(all_count))
print ("Total written into files : ", str(count))
