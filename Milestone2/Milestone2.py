import json
from bs4 import BeautifulSoup
import mysql.connector
import math
import time
import json

characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

data_Dict = {}
    
def store_words():
    with open('bookkeeping.json') as f:
        data = json.load(f)      #{0/106,"www.ics.uci.edu"}, {} , ...
        file_count = 0
        overall_data = data
        #change folder_document into doc_num
        for doc_num in data: #every file. eg. 0/116
            # ----
            if file_count%200==0:
                print file_count
            # ----
            file_total_word = 0
            file_dict = {}
            file_count +=1
            doc_num = doc_num.encode("ASCII")
            new_data = open(doc_num).read()     #Read html for 0/106
            soup = BeautifulSoup(new_data, 'html.parser')

            tags_to_look = ['body','title','h1','h2','h3','b','strong','cite']
            for tag in tags_to_look:
                substr = ""
                for i in soup.find_all(tag): #Find all text that after the tags
                    substr += i.text
                    tokenize(file_dict, substr, tag, data[doc_num])

            for each_file_word in file_dict.keys():
                file_dict[each_file_word]["position_weight"] = calculate_location_weight(file_dict[each_file_word]["position"])
                if each_file_word not in data_Dict:
                    data_Dict[each_file_word] = {}
                    data_Dict[each_file_word][doc_num] = file_dict[each_file_word]
                else: #word exists in data_Dict
                    data_Dict[each_file_word][doc_num] = file_dict[each_file_word]
    #done going over all files
    get_tfidf(file_count)
    #write_output("output1.txt",data_Dict)
    return

'''
@parameter: file_count: the total number of files
@function: this function loop over the data_Dict to get each word,
            and for each word, it loops over each file and uses
            information in each file to calculate the word's tf-idf
@return: None. The data_Dict will be modified, i.e. it's tf-idf spot will be filled.
'''
def get_tfidf(file_count):
    for each_word in data_Dict:
        #print "word: " + each_word
        for each_doc in data_Dict[each_word]:
            #print "doc: "+each_doc
            tf = data_Dict[each_word][each_doc]["tf"]
            #print "tf: "+str(tf)
            len_file = len(data_Dict[each_word])
            #print "# of files contains the word: " + str(len_file)
            data_Dict[each_word][each_doc]["tf_idf"] = tfidf_calculator(tf,len_file,file_count)


def calculate_location_weight(loc_list):
    #['body','title','h1','h2','h3','b','strong','cite']
    weight = 0
    for loc in loc_list:
        if loc == "body":
            weight += 2
        elif loc == "title":
            weight += 6
        elif loc == "h1":
            weight += 1
        elif loc == "h2":
            weight += 1
        elif loc == "h3":
            weight += 1
        elif loc == "b":
            weight += 6
        elif loc == "strong":
            weight += 6
        elif loc == "cite":
            weight += 6
    return weight



'''
@parameter: 1) tf: the term frequency of a word
            2) word_exists_file: the total number of files that the word exists in
            3) all_num_file: the total number of files
@function: calculate the weight of the tf-idf of a word
@return: return the weight of a word's tf-idf in a file
'''
def tfidf_calculator(tf, word_exists_files, all_num_file):
    weight = (1+ math.log10(float(tf))) * math.log10(float(all_num_file)/word_exists_files)
    return weight
    


'''
@function: write data I want to know  into a file, instead of waiting them to print out. Printing
    to the console is too slow.
@return: None
'''
def write_output(file_name, d):
    f = open(file_name,"w")
    for word in d:
        f.write(word + "\n")
        for each_doc in d[word].keys():
            f.write("doc_num: "+each_doc  +  "\n")
            f.write("url: " + d[word][each_doc]["url"] +"\n")
            f.write("tf_idf: " + str(d[word][each_doc]["tf_idf"]) +"\n")
            f.write("position: ")
            for pos in d[word][each_doc]["position"]:
                f.write(pos + " ")
            f.write("\n")
            f.write("position_weight:  " + str(d[word][each_doc]["position_weight"]) + "\n")
        f.write("\n")
    f.close()

'''
@parameter: an empty dictionary
@function: initialize the dictionary with keys:url(empty string), tf(float), tf(float), position(str)
@return: NONE. Because in the function the dictionary is modified and saved.
'''
def _init_eachDocDict(tar_dict):
    tar_dict["url"]  = ""
    tar_dict["tf"] = 0
    tar_dict["tf_idf"] = float(0.0)
    tar_dict["position"] = []



'''
@parameter: an empty dictionary, url(str), tf(float), tf_idf(float), position(str)
@function: put those information into it's corresponding value position in the empty dictionary
@return: NONE. Because in the function the dictionary is modified and saved.

def _fill_eachDocDict(doc_dict,  url, tf, tf_idf, position):
    doc_dict["url"] = url
    doc_dict["tf"] =  tf
    doc_dict["tf_idf"] = tf_idf
    doc_dict["position"].append(position)
'''

    
'''
@parameter: take a string and tokenize it according to the space
@return: a dictionary, the key is each word, the value is the occruence of each word in the string
'''
def tokenize(file_dict, text, position, url):
    tokenized_word = ""
    #Loop over every character in the file and find the character
    #that satisfies the standard
    for i in text:
        if i in characters:
            tokenized_word = tokenized_word + i
        else:
            #Add the satisfied words and their frequencies into
            #a directionary
            if tokenized_word != "":
                new_text = tokenized_word.lower()
                new_text = new_text.encode("ASCII")
                if new_text not in file_dict:
                    file_dict[new_text] = {}
                    _init_eachDocDict(file_dict[new_text])
                    file_dict[new_text]["url"] = url
                    file_dict[new_text]["position"].append(position)
                    file_dict[new_text]["tf"] = 1
 
                elif new_text in file_dict: #in the same tag  or new tag has the same  word
                    file_dict[new_text]["tf"] += 1
                    if position not in file_dict[new_text]["position"]:
                        file_dict[new_text]["position"].append(position)
                tokenized_word = ""
    return

def sortsecond(val):
    return val[1]

'''
'''

def write_json():
    with open("index.json","w") as f:
        json.dump(data_Dict,f)


if __name__ == "__main__":
    start_time = time.time()
    store_words()
    write_json()
    end_time = time.time()
    print "total time: " + str(end_time-start_time)







    

