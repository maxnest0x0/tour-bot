from sklearn.feature_extraction.text import CountVectorizer
import sys
import numpy
numpy.set_printoptions(threshold=sys.maxsize)

with open('Датасет.txt', 'r') as f:
    n = [i[:-2] for i in f]
f.close()

vectorizer = CountVectorizer(analyzer="word", ngram_range=(1, 4))
X = vectorizer.fit_transform(n)
vectorizer.get_feature_names_out()
print(sum(list(arr).count(1) for arr in X.toarray()))