# by Chenhao Tan

import os
import re
import tarfile
import string
import logging
logger = logging.getLogger('delatex')

class FinalContent:
    def __init__(self):
        self.result = []
    def appendString(self, text):
        self.result.append(text)
    #if tokenize then will add space between words
    def appendContent(self, content, pos, tokenize=False):
        if not tokenize:
            self.result.append(content[pos])
            return
        if content[pos] not in string.letters and content[pos] not in string.digits and content[pos] != '-':
            self.result.append(' %s' % content[pos])
            if pos < len(content) - 1 and content[pos + 1] != ' ':
                self.result.append(' ')
        else:
            self.result.append(content[pos])
    def getResult(self):
        return ''.join(self.result)

def getFileContent(filename, filecontent, fout):
    validExtension = set(['.tex', '.st'])
    for line in filecontent[filename]:
        line = line.strip()
        if len(line) == 0:
            continue
        pos = max(line.find('\\include '), line.find('\\input '), line.find('\\input{'), line.find('\\include{'), line.find('\\subfile{'), line.find('\\subfile '))
        bibpos = line.find('\\bibliography{')
        if pos != -1:
            #input file
            startpos = 0
            endpos = 0
            if pos > 0:
                fout.write('%s\n' % line[0:pos])
            interval = 0
            if line[pos:pos+8] == '\\include' or line[pos:pos+8] == '\\subfile':
                interval = 8
            else:
                interval = 6
            if line[pos+interval] == '{':
                startpos = line.find('{', pos) + 1
                endpos = line.find('}', startpos + 1)
                inputfile = line[startpos:endpos]
            else:
                startpos = line.find(' ', pos)
                while line[startpos] == ' ':
                    startpos += 1
                endpos = line.find(' ', startpos)
                if endpos == -1:
                    endpos = len(line)
                inputfile = line[startpos: endpos]
            logger.info('line %s', line)
            logger.info('input file %s', inputfile)
            
            if len(inputfile) == 0:
                logger.warn('no input file %s', line)
                fout.write('%s\n' % line[endpos+1:])
                continue
            
            inputfile = inputfile.lower()
            (inputfile, inputext) = os.path.splitext(inputfile)
            if inputfile.startswith('./'):
                inputfile = inputfile[2:]
            matched = 0
            for filename in filecontent:
                #print filename
                (cmpfilename, cmpext) = os.path.splitext(filename.lower())
                if inputext == '':
                    if cmpfilename == inputfile and cmpext in validExtension:
                        logger.info('matching file %s' % filename)
                        getFileContent(filename, filecontent, fout)
                        matched = 1
                        break
                else:
                    if cmpfilename == inputfile and cmpext == inputext:
                        logger.info('matching file %s' % filename)
                        getFileContent(filename, filecontent, fout)
                        matched = 2
                        break
            if matched == 0:
                logger.warn('no matching file %s', line)
                
            if endpos < len(line):
                fout.write('%s\n' % line[endpos+1:])
        elif bibpos != -1:
            inputbib = line[bibpos+1:line.find('}', bibpos)]
            inputbib = os.path.splitext(inputbib)[0]
            if inputbib.startswith('./'):
                inputbib = inputbib[2:]
            bblfilecandidate = []
            bblfile = None
            for filename in filecontent:
                (cmpfilename, cmpext) = os.path.splitext(filename.lower())
                if cmpext == '.bbl':
                    bblfilecandidate.append(filename)
                    if inputbib == cmpfilename:
                        bblfile = filename
            if bblfile is None:
                if len(bblfilecandidate) != 0:
                    bblfile = bblfilecandidate[0]
            if bblfile is not None:
                logger.info('matching bbl %s', bblfile)
                for l in filecontent[bblfile]:
                    fout.write('%s\n' % l)
            else:
                logger.warn('no matching bbl %s', inputbib)
        else:
            fout.write('%s\n' % line)
    
def extractTexFromTar(srcfile, dstfile):
    tarfin = tarfile.open(srcfile, 'r')
    filenames = tarfin.getnames()
    filecontent = {}
    mainfile = ''
    mainfilelist = {}
    validExtension = set(['.tex', '.bbl', '.st'])
    for filename in filenames:
        filetype = os.path.splitext(filename)[1].lower()
        if filetype in validExtension:
            fin = tarfin.extractfile(filename)
            content = []
            for line in fin:
                linesegs = line.splitlines()
                for ls in linesegs:
                    lreturn = ls.split('\r')
                    for l in lreturn:
                        pos = l.find('%')
                        if pos != -1 and l[pos-1] != '\\':
                            l = l[0:pos]
                        content.append(l)
            filecontent[filename] = content
            for line in content:
                if line.find('\\begin{document}') != -1 and filetype == '.tex':
                    mainfilelist[filename] = len(content)
    if len(mainfilelist) == 0:
        logger.warn('not finding main file %s', srcfile)
        return
    maxLen = 0
    for filename in mainfilelist:
        if mainfilelist[filename] > maxLen:
            maxLen = mainfilelist[filename]
            mainfile = filename
    fout = open(dstfile, 'w')
    getFileContent(mainfile, filecontent, fout)
    fout.close()


def removeBadMath(content):
    result = []
    pos = 0
    while pos < len(content) - 1:
        if content[pos:pos+2] == '\\(':
            if not (pos > 0 and content[pos-1] == '\\'):
                result.append(' $ ')
                pos += 2
                continue
        
        if content[pos:pos+2] == '\\)':
            if not (pos > 0 and content[pos-1] == '\\'):
                result.append(' $ ')
                pos += 2
                continue

        if content[pos:pos+2] == '\\[':
            if not (pos > 0 and content[pos-1] == '\\'):
                result.append(' $$ ')
                pos += 2
                continue
        
        if content[pos:pos+2] == '\\]':
            if not (pos > 0 and content[pos-1] == '\\'):
                result.append(' $$ ')
                pos += 2
                continue
        result.append(content[pos])
        pos += 1
    if pos < len(content):
        result.append(content[pos])
    return ''.join(result)

def getDebt(text):
    debt = 0
    for c in text:
        if c == '{':
            debt -= 1
        elif c == '}':
            debt += 1
    return debt

def removeDefinition(lines, content):
    debt = 0
    ignoreset = set(['def', 'newcommand', 'renewcommand', 'newtheorem', 'setsymbol', 'footmath', 'thanks', 'footnote'])
    for i in range(len(lines)):
        line = lines[i]

        pos = line.find('%')
        if pos != -1 and not (pos - 1 >= 0 and line[pos-1] == '\\'):
            line = line[0:pos]
        if len(line) == 0:
            continue
        pos = 0
        if line[pos] == '\\':
            pos += 1
            while pos < len(line) and (line[pos] in string.letters or line[pos] in string.digits):
                pos += 1
            latexcommand = line[1:pos]
            if latexcommand in ignoreset:
                debt = getDebt(line)
                continue
        if debt < 0:
            debt += getDebt(line)
            if debt <= 0:
                continue
        content.append('%s\n' % line.strip())

def simpleClean(lines):
    newlines = []
    for i in range(len(lines)):
        lines[i] = lines[i].replace("}}", "}\n}")
        tag = '\\thanks'
        a = lines[i].replace(tag, '\n' + tag).split('\n')
        tag = '\\footnote'
        for ai in a:
            if len(ai) == 0:
                continue
            aii = ai.replace(tag, '\n' + tag).split('\n')
            for aiii in aii:
                newlines.append(aiii)

    return newlines

# a very simple version of latex to text, put the text between document together
# remove all the enviroment settings and formulas
def simpleLatexToText(inputfile, outputfile, sectioned=False):
    fin = open(inputfile)
    lines = fin.readlines()

    lines = simpleClean(lines)

    fin.close()
    content = []
    count = 0
    removeDefinition(lines, content)
    content = ''.join(content)
    content = removeBadMath(content)
    startpos = content.find('\\begin{document}')
    if startpos == -1:
        logger.warn('no start document %s', inputfile)
        return
    #sometimes title appear before document
    titlepos = content.find('\\title') 
    if titlepos > 0 and titlepos < startpos:
        startpos = titlepos
    pos = startpos
    label = 'document'
    ignoringmode = set(['equation', 'eqnarray', 'array', 'figure', 'align', 'table', 'tabular', 'math', 'displaymath', 'thebibliography'])
    wordpattern = re.compile('\w+')
    sectionmode = set(['section', 'section*', 'title'])
    finalcontent = FinalContent()
    titleEnd = -2
    while pos < len(content):
        if content[pos] == '\\':
            if content[pos+1:pos+5] == 'verb':
                tempInterval = 5
                if content[pos+6] == '*':
                    tempInterval = 6
                tempPos = pos + tempInterval
                while content[tempPos] == ' ':
                    tempPos += 1
                delim = content[tempPos]
                verbEnd = content.find(delim, tempPos + 1)
                for ti in range(tempPos + 1, verbEnd):
                    finalcontent.appendContent(content, ti)
                pos = verbEnd + 1
                
            elif content[pos+1] not in string.letters and content[pos+1] not in string.digits:
                if content[pos+1] == ' ':
                    pos += 1
                else:
                    pos += 2
            else:
                temppos = pos + 1
                while content[temppos] in string.letters or content[temppos] in string.digits:
                    temppos += 1
                latexcommand = content[pos+1:temppos]
                if latexcommand == 'begin':
                    #ignoring mode: equation, eqnarray, array, figure, align, table, tabular
                    modestart = content.find('{', pos)
                    modeend = content.find('}', pos)
                    mode = content[modestart+1:modeend]
                    modeword = re.findall(wordpattern, mode)
                    if len(modeword) > 0:
                        tomatchmode = modeword[0]
                    else:
                        tomatchmode = mode
                    if sectioned and tomatchmode == 'abstract':
                        finalcontent.appendString('\n###start section abstract###\n') 
                    #print tomatchmode
                    if tomatchmode in ignoringmode or tomatchmode.find('bibliography') != -1:
                        if content.find('\\end{%s}' % mode, pos + 1) != -1:
                            pos = content.find('\\end{%s}' % mode, pos+1) + 6 + len(mode)
                        elif content.find('{%s}' % mode, pos + 1) != -1:
                            pos = content.find('{%s}' % mode, pos+1) + 2 + len(mode)
                        else:
                            pos = modeend + 1
                    else:
                        pos = modeend + 1
                elif latexcommand == 'end':
                    modestart = content.find('{', pos)
                    if modestart != -1:
                        modeend = content.find('}', pos)
                        pos = modeend + 1
                        if sectioned:
                            mode = content[modestart+1:modeend].lower()
                            if mode.strip() == 'abstract':
                                finalcontent.appendString('\n###start dummy section###\n')
                    else:
                        pos += 1
                elif sectioned and latexcommand in sectionmode:
                    modestart = 0
                    if content[temppos] == '[':
                        temp = content.find(']', pos)
                        modestart = content.find('{', temp)
                    else:
                        modestart = content.find('{', pos)
                    pastparenthsis = 0
                    modeend = modestart
                    #find matching parathesis
                    while True:
                        modeend += 1
                        if content[modeend] == '}':
                            pastparenthsis -= 1
                            if pastparenthsis < 0:
                                break
                        elif content[modeend] == '{':
                            pastparenthsis += 1
                    mode = ''.join(['%s ' % a.strip() for a in content[modestart+1:modeend].splitlines()])
                    if latexcommand == 'title':
                        finalcontent.appendString('\n###start section title###\n') 
                        titleEnd = modeend
                    else:
                        finalcontent.appendString('\n###start section %s###\n' % mode) 
                    pos = temppos
                else:
                    pos = temppos
        elif content[pos] == '$':
            if content[pos+1] == '$':
                endpos = pos
                while True:
                    endpos = content.find('$$', endpos+2)
                    if content[endpos - 1] != '\\' or (content[endpos-1] == '\\' and content[endpos-2] == '\\'):
                        break
                    else:
                        endpos -= 1
                pos = endpos + 2
            else:
                endpos = pos
                while True:
                    endpos = content.find('$', endpos+1)
                    if content[endpos - 1] != '\\' or (content[endpos-1] == '\\' and content[endpos-2] == '\\'):
                        break
                pos = endpos + 1
        else:
            finalcontent.appendContent(content, pos)
            if sectioned and pos == titleEnd + 1:
                logger.info('title found %s %d %s', inputfile, titleEnd, content[titleEnd + 1])
                finalcontent.appendString('\n###start section dummy###\n')
            pos += 1
        if pos < count:
            logger.error('find error %s %s %d %d %d', inputfile, content[(count-100):count], count, len(content), pos)
            break
        else:
            count = pos

    fout = open(outputfile, 'w')
    lines = finalcontent.getResult().split('\n')
    logger.info('line number %d', len(lines))
    linenum = 0
    percent = 0.8
    for line in lines:
        linenum += 1
        if line.find('References') != -1 and linenum > percent * len(lines):
            break
        line = line.strip()
        words = line.split()
        for word in words:
            fout.write('%s ' % word.decode('ascii', 'ignore'))
        if len(line) > 0:
            fout.write('\n')
    fout.close()
