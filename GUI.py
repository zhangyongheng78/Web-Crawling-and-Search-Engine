from flask import Flask, url_for, render_template, request, redirect
import Milestone2_query

app = Flask(__name__)
navigation = [
    {'message':'', 'length': 3},[
    {
        'author': 'Frank zhang',
        'title' : 'Blog Post 1',
        'content' : 'First post conetent',
        'date_posted' : 'April 20, 2018'
    },
    {
        'author': 'Sam',
        'title' : 'Blog post 2',
        'content' : 'Second post conetent',
        'date_posted' : 'April 20, 2018'
    }]
    ]
navigation[1].append({
        'author': 'Qiren xiaodi',
        'title' : 'Blog post 3',
        'content' : 'Third post conetent',
        'date_posted' : 'April 20, 2018'
    })

output = [{'message':'', 'length': 0},[]]
index = {}
index = Milestone2_query.load_json_index(index)


@app.route('/', methods=['POST', 'GET'])
def cool():

    if request.method == "GET":
        return render_template('index.html', message = output)
    else:
        text = request.form['search']
        if text != '':
            message = ''
            count = 0
            output[1] = []
            
            raw_query_list = Milestone2_query.tokenize(text)
            query_list = Milestone2_query._check_word_exists(index, raw_query_list)
            if len(query_list) == 0:
                output[0]['message'] = "there is no key word " + text.upper() +" in any websit"
                return redirect('/search')
            url_list = []
            rank_doc_dict = Milestone2_query.rank(index, query_list)
            sorted_by_rank_list = sorted(rank_doc_dict.items(),key=lambda kv: kv[1])
            if len(sorted_by_rank_list) < 20:
                for info in sorted_by_rank_list[:len(sorted_by_rank_list)]:
                    url = index[query_list[0]][info[0]]["url"]
                    url_list.append(url)
                rank_term = Milestone2_query._get_term_ranking(index, query_list)
                sorted_rank_term_list = sorted(rank_term.items(),key=lambda kv: kv[1])
                remain_count = 20-len(sorted_by_rank_list) 
                extra_url_list = Milestone2_query._get_remain(index, remain_count, sorted_rank_term_list)
                url_list = url_list + extra_url_list
            else:
                for info in sorted_by_rank_list[:len(sorted_by_rank_list)]:
                    url = index[query_list[0]][info[0]]["url"]
                    url_list.append(url)
            for url in url_list:
                if count >= 20:
                    break
                output[1].append({"url": url})
                count += 1
    
            output[0]['message'] = text.upper()
            output[0]['length'] = count
            return redirect('/search')
        output[0]['message']  = "please input something"
        return redirect('/')

@app.route('/search', methods=['GET'])
def login():
    return render_template('search.html', navigation = output)




