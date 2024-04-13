import re 
import json
from nltk.util import ngrams
from collections import defaultdict
from tkinter import *
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import re 
import csv
import webbrowser
""" 
    Install dependencies:
    pip install nltk
    pip install tk
    pip install -U scikit-learn
"""

# get data from crawled data - DangHuuTan.json
def readDocs():
    with open("DangHuuTan.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    docs = []
    map = {}

    for doc_id, article in enumerate(data):
        content = re.sub("\n", " ", article["content"].lower())
        url = article["originalLink"]
        map[doc_id] = url
        docs.append(content)
    
    return docs, map

# preprocess data
def preprocess(text):
    text = re.sub(r"…", " ", text)
    text = re.sub(r"[.;,|\"'“”‘’()]", "", text)

    return text

# tokenize data - for building inverted index
def tokenize(text):
    return [token for token in text.split(" ") if token != ""]

# build inverted index including unigram and bigram
def build_inverted_index(docs):
    inverted_index = defaultdict(set)
    for doc_id, doc in enumerate(docs):
        tokens = tokenize(preprocess(doc))
        unigrams = tokens
        bigrams = list(ngrams(tokens, 2))
        for unigram in unigrams:
            inverted_index[unigram].add(doc_id)
        for bigram in bigrams:
            inverted_index[bigram[0] + " " + bigram[1]].add(doc_id)

    #sort doc_ids
    for term, doc_ids in inverted_index.items():
        inverted_index[term] = sorted(doc_ids)

    return dict(sorted(inverted_index.items()))

# save inverted index to inverted_index.json file
def saveInvertedIndexToJson(inverted_index):
    inverted_index_json = {term: list(doc_ids) for term, doc_ids in inverted_index.items()}
    with open("inverted_index.json", "w", encoding="utf-8") as file:
        json.dump(inverted_index_json, file, ensure_ascii=False)

# read inverted index from inverted_index.json file
def readInvertedIndex():
    with open("inverted_index.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    
    inverted_index = defaultdict(set)
    for term, doc_ids in data.items():
        inverted_index[term] = set(doc_ids)
    
    return inverted_index

# search And operation, for example: tom AND good jerry
def searchAnd(inverted_index, query):
    query = query.split(" and ")
    query = [token.strip() for token in query if token != ""]
    if len(query) == 0:
        return set()
    result = inverted_index[query[0]]
    for term in query[1:]:
        result = result.intersection(inverted_index[term])
    # sort doc_ids
    result = sorted(result)
    return result

# search Or operation, for example: tom OR good jerry
def searchOr(inverted_index, query):
    query = query.split(" or ")
    query = [token.strip() for token in query if token != ""]
    result = set()
    for term in query:
        result = result.union(inverted_index[term])
    # sort doc_ids
    result = sorted(result)
    return result
   
def search(inverted_index, query):
    query = query.lower()
    query = preprocess(query)
    if " and " in query:
        return searchAnd(inverted_index, query)
    elif " or " in query:
        return searchOr(inverted_index, query)
    else:
        return "Wrong query for Boolean search!"

def rankedSearch(query, docs):
    searchQuery = query

    n = len(docs)
    # preprocess data
    docs = [preprocess(doc) for doc in docs]

    tfidf = TfidfVectorizer(vocabulary=searchQuery.split(" "))

    tfidf_result_docs = tfidf.fit_transform(docs)
    print(tfidf_result_docs.toarray())

    print("-----------------")

    tfidf_result_query = tfidf.fit_transform([searchQuery])
    print(tfidf_result_query.toarray())

    print("-----------------")

    result = []
    for i, _ in enumerate(docs):
        result.append({i: cosine_similarity(tfidf_result_docs[i], tfidf_result_query)[0][0]})

    # sort result by similarity
    result = sorted(result, key=lambda x: list(x.values())[0], reverse=True)
    print(result)
    # get top 5 most similar documents with similarity score more than 0.5
    result = [list(r.keys())[0] for r in result if list(r.values())[0] > 0.5][:5]
    print(result)

    return result

# create GUI for input query by Tkinter
def createGUI():
    root = Tk()
    root.title("Gu Gồ Sớt")
    root.geometry("730x300")

    frame_interact = Frame(root)
    frame_interact.pack(side=TOP, fill=X, expand=True)

    docs, map_url = readDocs()
    inverted_index = {}

    label = Label(frame_interact, text="Enter your query:")
    label.pack(side=LEFT)

    query = StringVar()
    entry = Entry(frame_interact, textvariable=query, width=35)
    entry.pack(side=LEFT)

    button_search = Button(frame_interact, text="Boolean search", command=lambda: text.insert(
        END, "Query: " + str(query.get()) + "\n  ->Result: " + str(search(inverted_index, query.get())) + "\n") if inverted_index 
        else text.insert(END, "Inverted index not loaded!\n", "error")
    )
    button_search.pack(side=LEFT)

    def handle_ranked_search():
        text.insert(
            END, "Query: " + str(query.get()) + "\n  ->Top 5 result:[\n"
        )
        for doc_id in rankedSearch(query.get(), docs):
            text.insert(END, "\tDocID: " + str(doc_id) + " - ")
            text.insert(END, "Link\n", "url")
        text.insert(END, "]\n")
    button_ranked_search = Button(frame_interact, text="Ranked search", command=handle_ranked_search)
    button_ranked_search.pack(side=LEFT)

    def handle_read_inverted_index():
        try:
            inverted_index.update(readInvertedIndex())
            text.insert(
                END, "Inverted index loaded!\n  Support opperation: AND, OR\n  For example: cũng như AND cũng phải\n               cũng như OR cũng phải\n", "loaded"
            )
        except FileNotFoundError:
            text.insert(END, "Error: Inverted index file not found!\nPlease build inverted index first!\n", "error")
    button_load = Button(frame_interact, text="Load inverted index", 
        command=handle_read_inverted_index
    )
    button_load.pack(side=LEFT)

    def handle_build_inverted_index():
        try:
            inverted_index = build_inverted_index(docs)
            saveInvertedIndexToJson(inverted_index)
            text.insert(
                END, "Inverted index built!\nThen you can load from it\n", "loaded"
            )
        except Exception as e:
            print(e)
            text.insert(END, "Failed to build inverted index\n", "error")
    button_build_inverted_index = Button(frame_interact, text="Build inverted index",
        command=handle_build_inverted_index
    )
    button_build_inverted_index.pack(side=LEFT)

    text = Text(root)
    text.pack(side=BOTTOM, fill=BOTH, expand=True)
    text.tag_config("error", foreground="red")
    text.tag_config("loaded", foreground="green")
    text.tag_config("url", foreground="blue", underline=1)

    def handle_url_click(event, text):
        line_context = text.get("current linestart", "current lineend")
        tokens = line_context.split(" ")
        # print(tokens)
        url = map_url[int(tokens[1])]
        webbrowser.open(url)
    text.tag_bind("url", "<Button-1>", lambda e: handle_url_click(e, text))
    text.insert(END, "Welcome to Gu Gồ Sớt!\nTry to search something. Ex: \"lễ hội\"\n", "loaded")

    root.mainloop()

if  __name__ == "__main__":
    createGUI()