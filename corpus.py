import numpy as np
from math import log

class Document:
	def __init__(self, key, uniques, bow):
		self.id = key
		self.uniques = uniques
		self.tfvec = self.tf(self.counts_vec(bow, uniques))
		self.tfidfvec = {}
		self.cluster = -1

	def counts_vec(self, bow, keys):
		cvec = dict.fromkeys(self.uniques, 0)
		for word in bow:
			cvec[word] += 1
		return(cvec)
	
	def tf(self, counts_vec):
		# expects as input vector from counts_vec
		num_words = sum(counts_vec.values())
		tfvec = {}
		for word, count in counts_vec.items():
			tfvec[word] = count / num_words
		
		return(tfvec)
	
	def calc_tfidf(self, idfvec):
		for word, val in self.tfvec.items():
			self.tfidfvec[word] = idfvec[word] * val
			
	def get_vals(self):
		if self.tfidfvec is {}:
			return None
		else:
			return(list(self.tfidfvec.values()))
	
	def set_cluster(self, newclust):
		self.cluster = newclust

class Corpus:
	def __init__(self, bowdict):
		self.uniquekeys = self.get_unique_values(bowdict)
		self.documents = self.tfidf(bowdict)
		self.gen_np_dataset()
		
						
	def idf(self, documents):
		# expects a list of dictionaries, each dict is output of counts_vec
		N = len(documents)
		
		idfDict = dict.fromkeys(documents[0].uniques, 0)
		for document in documents:
			for word, val in document.tfvec.items():
				if val > 0:
					idfDict[word] += 1
	
		for word, val in idfDict.items():
			idfDict[word] = log(N / float(val))
		return(idfDict)
	
	def get_unique_values(self, corpus):
		vals = list(corpus.values())
		unique = { i for l in vals for i in l }
		return(list(unique))
			
	
	def tfidf(self, corpus):
		unique_keys = self.uniquekeys
		documents = []
		for key, value in corpus.items():
			documents.append(Document(key, unique_keys, value))
		
		idfdict = self.idf(documents)
		for doc in documents:
			doc.calc_tfidf(idfdict)
		
		return(documents)
	
	def gen_np_dataset(self):
		self.dataset = np.array([document.get_vals() for document in self.documents])
			
if __name__ == '__main__':
	from citation_network import abstract_network
	toolname = 'ahl27litreview'
	email = 'a@gmail.com'
	init_pmids = ['24349035']
	terms = [['coevolution', 'coevolutionary', 'cooccurence'],
								['phylogenetic', 'profile', 'phylogeny', 'mirrortree', 'contexttree']]
		
	abstracts = abstract_network(init_pmids, toolname, email, search_terms=terms)
	documents = Corpus(abstracts)
