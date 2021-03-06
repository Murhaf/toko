# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from subprocess import Popen, PIPE
from subtoken import Subtoken
import inspect

toko_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/"


def toko_file(file_name, wapiti_path, wp_model, delimiter):
    '''
    takes a `raw' file as an input (one sentence per line) and outputs
    a file (.tokens) with one token per line and empty lines between
    sentences
    '''
    wp_file = label_subtokenize_file(file_name)
    result = call_wapiti(wp_file, wapiti_path, wp_model)
    write_output(file_name+".tks", result, delimiter)
    os.remove(wp_file)

def label_subtokenize_file(file_name):
    '''
    This method produces subtokens for the 'tokenize' mode (for labeling)
    it assumes an input file with one sentence per line, however it can
    handle sentence-ID \tab sentence per line.
    If there is no sentence-ID the function will assign one for
    each.
    '''

    wp_file_name = toko_path + "tmp.subtks"

    subtk_file = open(wp_file_name, "w")
    raw_lines = [line for line in open(file_name)]
    
    if len( raw_lines[0].split('\t') ) == 1:
        sentence_id = 0
        for line in raw_lines:
            if len(line) > 1:
                line_splits = line.split("\t") 
                t = Subtoken(line_splits[0][0:-1]) # [0:-1] to remove the `\n'
                subtokens, categories, spaces = t.subtokenize()
            
                for i in range(len(subtokens)):
                    subtk_line = str(sentence_id) + '\t' + \
                        subtokens[i] + '\t' + str(spaces[i]) + \
                        '\t'+ categories[i] + '\t' + str(len(subtokens[i])) +\
                        '\t'
                    subtk_file.write(subtk_line)
                    subtk_file.write('\n')
                sentence_id += 1
                subtk_file.write('\n')

    elif len( raw_lines[0].split('\t') ) == 2:
        for line in raw_lines:
            if len(line) > 1:
                line_splits = line.split("\t") 
                t = Subtoken(line_splits[1][0:-1]) # [0:-1] to remove the `\n'
                subtokens, categories, spaces = t.subtokenize()

                for i in range(len(subtokens)):
                    subtk_line = line_splits[0] + '\t' + subtokens[i] +\
                        '\t' + str(spaces[i]) +\
                        '\t'+ categories[i] + '\t' + str(len(subtokens[i])) +\
                        '\t'
                    subtk_file.write(subtk_line)
                    subtk_file.write('\n')
                subtk_file.write('\n')

    else:
        print "toko is expecting one sentence per line or one sentence-ID and sentence per line (separated by a tab). Please double-check the input file."
        exit(1)

    subtk_file.close()
    return wp_file_name



def call_wapiti(wp_file_name, wapiti_path, wp_model):
    '''
    calls wapiti to classify the subtokens.
    - wp_file_name -- the file containing subtokens
    - wapiti_path -- path to wapiti toolkit, if passed then it will be
    used even if the wapiti path has been previously set through
    'config'.
    - wp_model -- the tokenization model to be used, if None is passed
    then the PTB model will be used.
    '''
    input_path = wp_file_name

    if wp_model is None:
        wp_model = toko_path + '/../models/ptb.model'
    
    if wapiti_path is None:
        try:
            wapiti_path = open(toko_path + 'tokoconfig').read()            
        except IOError:
            print "Please use the 'config' mode to permanently set the absolute path to Wapiti or use the argument --wapiti with the 'tokenize' mode.\n python toko config --wapiti /full/path/to/wapiti \n python toko tokenize file-to-tokenize --wapiti /full/path/to/wapiti"
            exit(1)

    args = ['./wapiti', 'label', '-m', wp_model, input_path]
    wapiti_proc = subprocess.Popen(args, cwd=wapiti_path, stdout=PIPE)
    
    return wapiti_proc.stdout.readlines()




def write_output(out_file_name, wapiti_output, delimiter):
    '''
    reads the output of wapiti and writes a new file with each token
    on one line. 
    '''
    if delimiter is None:
        delimiter = '\n'

    out_file = open(out_file_name, "w")
    word = ""

    for l in wapiti_output:
        columns = l.split("\t")        
        
        if len(columns) < 2:
            out_file.write('\n')

        else:
            word += columns[1]
            if columns[2] == "1": #if the word is followed by a whitespace
                word += " "
            
            if columns[-1][0:-1] == "SPLIT":                
                out_file.write(word)
                out_file.write(delimiter)
                word = ""
                
    out_file.close()        



#############
### tokenizing one setence at a time
#############

def toko_sentence(sentence, wapiti_path, wp_model):
    '''
    tokenizes one sentence at a time. the method returns a list
    of tokens
    '''
    wp_file = label_subtokenize_sentence(sentence)
    result = call_wapiti(wp_file, wapiti_path, wp_model)
    list_of_tokens = write_output_sentence(result)
    os.remove(wp_file)
    return list_of_tokens


def label_subtokenize_sentence(sentence):

    wp_file_name = toko_path + "tmp.subtks"

    subtk_file = open(wp_file_name, "w")
    t = Subtoken(sentence)
    subtokens, categories, spaces = t.subtokenize()
            
    for i in range(len(subtokens)):
        subtk_line = "1" + '\t' + \
            subtokens[i] + '\t' + str(spaces[i]) + \
            '\t'+ categories[i] + '\t' + str(len(subtokens[i])) +\
            '\t'
        subtk_file.write(subtk_line)        
        subtk_file.write('\n')
        
    subtk_file.write('\n')
    
    subtk_file.close()
    return wp_file_name


def write_output_sentence(wapiti_output):
    '''
    reads the output of wapiti and returns a list of tokens.    
    '''

    output = list()
    word = ""

    for l in wapiti_output:
        columns = l.split("\t")               
        
        if len(columns) > 2:
            word += columns[1]
            if columns[2] == "1": #if the word is followed by a whitespace
                word += " "
            
            if columns[-1][0:-1] == "SPLIT":                
                output.append(word)                
                word = ""
    
    return output
