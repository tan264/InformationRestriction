import re 
import json
from nltk.util import ngrams
from collections import defaultdict
from tkinter import *
"""
    Install dependencies:
    pip install nltk
    pip install tk
"""


# preprocess data
def preprocess(text):
    text = re.sub(r"…", " ", text)
    text = re.sub(r"[.;,|\"'“”‘’()]", "", text)
    return text

# tokenize data
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

def saveToJson(inverted_index):
    inverted_index_json = {term: list(doc_ids) for term, doc_ids in inverted_index.items()}
    with open("DangHuuTan.json", "w", encoding="utf-8") as file:
        json.dump(inverted_index_json, file, ensure_ascii=False)

def readDocs():
    with open("DangHuuTan_docs.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    docs = []
    for article in data:
        content = re.sub("\n", " ", article["content"].lower())
        docs.append(content)
    
    return docs

# read inverted index from json file
def readInvertedIndex():
    with open("DangHuuTan.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    
    inverted_index = defaultdict(set)
    for term, doc_ids in data.items():
        inverted_index[term] = set(doc_ids)
    
    return inverted_index

# search And operation, for example: tom AND good jerry
def searchAnd(inverted_index, query):
    query = query.split(" and ")
    query = [token for token in query if token != ""]
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
    query = [token for token in query if token != ""]
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
        return "Wrong query"

# create GUI for input query by Tkinter
def createGUI():
    root = Tk()
    root.title("Gu Gồ Sớt")
    root.geometry("700x300")

    inverted_index = {}

    label = Label(root, text="Enter your query:")
    label.pack(side=LEFT)

    query = StringVar()
    entry = Entry(root, textvariable=query, width=35)
    entry.pack(side=LEFT)

    button = Button(root, text="Search", command=lambda: text.insert(
        END, "Query: " + str(query.get()) + "\n  ->Result: " + str(search(inverted_index, query.get())) + "\n") if inverted_index 
        else text.insert(END, "Inverted index not loaded!\n", "error")
    )
    button.pack(side=LEFT)

    def handle_read_inverted_index():
        try:
            inverted_index.update(readInvertedIndex())
            text.insert(
                END, "Inverted index loaded!\n  Support opperation: AND, OR\n  For example: cũng như AND cũng phải\n               cũng như OR cũng phải\n", "loaded"
            )
        except FileNotFoundError:
            text.insert(END, "Error: Inverted index file not found!\n", "error")
    button_load = Button(root, text="Load inverted index", 
        command=handle_read_inverted_index
    )
    button_load.pack(side=LEFT)

    text = Text(root)
    text.pack(side=BOTTOM, fill=BOTH, expand=True)
    text.tag_config("error", foreground="red")
    text.tag_config("loaded", foreground="green")
    text.insert(END, "Inverted index not loaded!\n", "error")

    root.mainloop()

if  __name__ == "__main__":
    createGUI()