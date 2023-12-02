from sklearn.feature_extraction.text import CountVectorizer

with open('Датасет.txt', 'r') as f:
    n = [i[:-2] for i in f]
f.close()


myVectorizer = CountVectorizer(analyzer="word", ngram_range=(1, 4))
data = myVectorizer.fit_transform(n)
myVectorizer.get_feature_names_out()

result = data.toarray()
