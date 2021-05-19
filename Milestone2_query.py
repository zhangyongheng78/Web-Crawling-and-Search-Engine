import json
import math
import time
import json

characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


def load_json_index(index):
    with open("index.json","r") as f:
        index = json.load(f)
    return index


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


def get_query():
    query = input('Enter query to search, or only type "exit" to exit: ')
    query_list = tokenize(query)
    return query_list


def tokenize(text):
    tokenized_word = ""
    d = []
    c = 0
    #Loop over every character in the file and find the character
    #that satisfies the standard
    for i in text:
        c += 1
        if i in characters:
            tokenized_word = tokenized_word + i
            if(c == len(text)):
                new_text = tokenized_word.lower()
                d.append(new_text)
        else:
            #Add the satisfied words and their frequencies into
            #a directionary
            if tokenized_word != "":
                new_text = tokenized_word.lower()
                d.append(new_text)
                tokenized_word = ""
    return d



'''
@parameter: tf_idf(float), pos_weight(int)
@function: calculate the score of product of tf_idf and position weight.
            tf_idf is 60% important, and position weight is 40% important
@return: return the score of tf_idf and position weight. It's a float.
'''
def _sum_tf_idf_pos(tf_idf, pos_weight):
    return 0.6*float(tf_idf)+0.4*float(pos_weight)
    
'''
@function: this function is the function that does the ranking.
@parameter: index: the whole inverted index database; query_list: the list that contains each query terms
@return: a dictionary that contains the intersect documents of those query terms, and their value is their overall rank
    e.g.{"12/100":3.54, "5/203": 4.2, "8/160":2.3231} ...
'''
def rank(index,query_list):
    #get all query word's intersection files first
    if len(query_list) >= 2:
        intersect = _find_intersect(index,query_list)
        for each_doc in intersect:
            intersect[each_doc] = _doc_overall_score(each_doc,query_list,index,intersect)
        return intersect
    elif len(query_list) == 1:
        result = {}
        for doc in index[query_list[0]]:
            result[doc] = _sum_tf_idf_pos(index[query_list[0]][doc]["tf_idf"],index[query_list[0]][doc]["position_weight"])
        return result

'''
@parameter: - index: the whole inverted index database;
            - query_list: a list that contains all query terms.
@function: this function finds the intersect files of those query terms
@return: it returns 2 things.
        1. intersect: a dictionary which key is each doc that all query terms appear in, the value is 0
        2. rank_term: a dictionary which key is each term, and the value is each term's number of total existing document
'''
#need to check if some query term is in the index. if it is not in index and I wanna index it,
#it will give me a keyerror.
def _find_intersect(index, query_list):
    intersect_docs= {}
    for i in range(len(query_list)-1):
        if i == 0:
            intersect_docs = _find_intersect_helper(index[query_list[i]],index[query_list[i+1]])
        else:
            intersect_docs = _find_intersect_helper(intersect_docs, index[query_list[i+1]])           
    return intersect_docs

'''
@parameter: dictionary a, b, both are dictionary that has all those files and affiliated file information
@function: find the intersect documents in both files, and put them into the result{}.
@return: result{}, which keys are the intersect docs, value are 0.
'''
def _find_intersect_helper(a,b):
    result = {}
    for each_doc in a:
        if each_doc in b:
            result[each_doc] = 0
    return result


'''
@parameter: doc: document number, e.g. 12/100;
            term_order_dict: a dictionary, key is all the query terms, value is each term's weight.
            index: the whole inverted_index database
@function: it calculates the document's overall score.
            e.g.
                term_order_dict: {"computer": 2, "science": 1}
                in doc 12/100:
                        the computr tf_idf is 1.6, pos_weight is 9
                        the science tf_idf is 0.9, pos_weight is 3
            doc 12/100 overall score:
                term_order_dict["computer"](the weight of computer) * _sum_tf_idf_pos(index["computer"]["12/100"]["tf_idf"], ...["position_weight"]) 
                    ->  2 * (0.6*1.6)+(0.4*9)
                    +
                    science's score.
@return: the overall score of the document
'''         
def _doc_overall_score(doc, query_list,index, intersect):
    score = 0
    for each_term in query_list:
        score += _sum_tf_idf_pos(index[each_term][doc]["tf_idf"],index[each_term][doc]["position_weight"])
    return score        

'''
@parameter: rank_term: a dict, key is query terms, value is # of total doc that each term exists
            e.g. {"computer": 10, "science": 4} -> computer is in 10 docs, science is in 4 docs
@function: sort those query terms from order: term that has less doc has more weight.
            e.g. science has more weight than computer science.
@return: a dict, key is each query terms, value is their weight.
            e.g. {"science": 2, "computer": 1}
'''
def _get_term_from_small_to_big(rank_term):
    term_ordered_dict = {}
    sorted_by_value = sorted(rank_term.items(), key=lambda kv: kv[1])
    for i in range(len(sorted_by_value)):#from important to less important
        term_ordered_dict[sorted_by_value[i][0]] = len(sorted_by_value)-i
    return term_ordered_dict

def _write_to_file(filename, sorted_by_rank_list, query_list, index):
    f = open(filename, "w")
    for info in sorted_by_rank_list:
        index[query_list[0]][info[0]]["url"]
        f.write("\n")
    f.close()

def _check_word_exists(index, query_list):
    valid_query_list = []
    for term in query_list:
        if term in index:
            valid_query_list.append(term)
    return valid_query_list

def _get_term_ranking(index, query_list):
    rank_term = {}
    for term in query_list:
        rank_term[term] = len(index[term])
    return rank_term

def _get_remain(index, remain_count, sorted_rank_term_list):
    url_list = []
    query_list = []
    count = 0
    for term_docNum in sorted_rank_term_list:
        query_list.append(term_docNum[0])
        count += int(term_docNum[1])
        if count >= remain_count:
            break
    rank_doc_dict = rank(index, query_list)
    sorted_by_rank_list = sorted(rank_doc_dict.items(),key=lambda kv: kv[1],reverse=True)
    for info in sorted_by_rank_list:
        url_list.append(index[query_list[0]][info[0]]["url"])
    return url_list



if __name__ == "__main__":
    index = {}
    index = load_json_index(index)
    exit_status = False
    while(exit_status == False):
        raw_query_list = get_query()
        if len(raw_query_list) == 1 and raw_query_list[0] == "exit":
            exit_status = True
        else:
            query_list = _check_word_exists(index, raw_query_list)
            if len(query_list) == 0:
                pass
            else:
                start = time.time()
                url_list = []
                rank_doc_dict = rank(index, query_list)
                sorted_by_rank_list = sorted(rank_doc_dict.items(),key=lambda kv: kv[1],reverse=True)
                if len(sorted_by_rank_list) < 20:
                    for info in sorted_by_rank_list[:len(sorted_by_rank_list)]:
                        url_list.append(index[query_list[0]][info[0]]["url"])
                    rank_term = _get_term_ranking(index, query_list)
                    sorted_rank_term_list = sorted(rank_term.items(),key=lambda kv: kv[1])
                    remain_count = 20-len(sorted_by_rank_list) 
                    extra_url_list = _get_remain(index, remain_count, sorted_rank_term_list)
                    url_list = url_list+extra_url_list
                else:
                    for info in sorted_by_rank_list[:20]:
                        url_list.append(index[query_list[0]][info[0]]["url"])

    
    print("Done.")





'''
            

if __name__ == "__main__":
    index = {}
    index = load_json_index(index)
    exit_status = False
    while(exit_status == False):
        raw_query_list = get_query()
        if len(raw_query_list) == 1 and raw_query_list[0] == "exit":
            exit_status = True
        else:
            query_list = _check_word_exists(index, raw_query_list)
            if len(query_list) == 0:
                pass
            else:
                start = time.time()
                rank_doc_dict = rank(index, query_list)
                sorted_by_rank_list = sorted(rank_doc_dict.items(),key=lambda kv: kv[1])
                for info in sorted_by_rank_list[:20]:
                    print(index[query_list[0]][info[0]]["url"])
                print(time.time()-start)
    print("Done.")
'''
    
    






    
