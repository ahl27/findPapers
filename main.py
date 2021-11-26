from kmeans import KMeans
from citation_network import abstract_network
from corpus import Corpus

# Run this script with `python3 main.py`
# See definition of user parameters below

###### USER PARAMETERS #####
toolname = 'ahl27litreview'
email = 'pmcsearch@ahl27.com'
init_pmids = ['24349035']
verbose = True
outfile_name = None #'papersfound.txt'
api_key = None
depth = 1
nclust = 2
terms = [['coevolution', 'coevolutionary', 'cooccurence'],
					['phylogenetic', 'profile', 'phylogeny', 'mirrortree', 'contexttree']]

#### EXPLANATIONS ####
# Required params to use NCBI API:
#
# * toolname: 	name of tool, set it to some random string. 
#									- ex. 'alakshmantool'
# * email: 			email address for contacting if there's a problem.
# 								- ex. 'a@gmail.com'
# * init_pmids:	PubMed IDs to build a network from, as a comma separated list
#								of numbers. Should be fine as strings or integers. If only using
#								a single ID, still put it into a list (like ['1'])
#									- ex. ['001', '002', '003']
#
# Additional parameters:
#
# * verbose:		True to print out progress, False to suppress most output 
#									- (default True)
#
# * depth:			How far into the network to go. Depth=n means that all papers returned 
#								will be within n distance from at least one paper in init_pmids. A paper 
#								that cites or is cited by a given paper are distance 1 away from each other.
#									- ex. 3
# 								-	CAUTION: The number of papers returned grows incredibly rapidly with depth. 
# 				 								The example returns 35 papers at depth 1, and ~32,000 at depth 2.
#
# * apikey:			Generated from your NCBI account. Using an apikey supposedly increases limit to 10 requests/sec.
#				- ex. `None` if you don't have a key, else `'abcde123456'`
#
# * nclust:			Number of clusters to cluster into.
#									- ex. 3 
#
# * terms:			Search terms, organized as a list of lists. Within each nested list, the 
#								abstract must contain at least one word from it.
# 							The format is essentially: [ [1, 2], [3, 4] ] => (1 OR 2) AND (3 OR 4)
# 							Leave empty ( [] ) to just grab everything.
#									- ex. [['streptomyces', 'pseudomonas'], ['antibiotics']]
#									- This returns abstracts that include both 'antibiotics' and at least
#										one term from (streptomyces, pseudomonas)

def interpret_cluster(corp):
	clusters = {}
	for document in corp.documents:
			if document.cluster in clusters.keys():
				clusters[document.cluster].append(document.id)
			else:
				clusters[document.cluster] = [document.id]
	
	return(clusters)

if __name__ == '__main__':
	print('*'*40)
	print("Finding papers and clustering by abstract similarity.\n")
	print("User parameters:")
	print('\t- toolname: ' + toolname)
	print("\t- email: " + email)
	print('\t- init_pmids: ' + str([int(i) for i in init_pmids]))
	print('\t- depth: ' + str(depth))
	print('\t- nclust: ' + str(nclust))
	if outfile_name is not None:
		print('\t- outfile: ' + outfile_name)
	if terms != []:
		search_str = [' OR '.join(i) for i in terms]
		search_str = '(' + ') AND ('.join(search_str) + ')'
		print('\t- terms: ' + search_str)
	print('\nThanks for using my tool!')
	print('*'*40)
	print()			
	abstracts = gen_paper_network(init_pmids, toolname, email, apikey=api_key, depth=depth, terms=terms, verbose=verbose)
	documents = Corpus(abstracts)
	print('\n' + str(len(documents.documents)) + ' total abstracts matched search criteria.\n')
	print('Clustering with k-means (k=' + str(nclust) + ')...')
	model = KMeans(k=nclust)
	model.fit(documents.dataset)
	for i in range(len(documents.documents)):
		documents.documents[i].set_cluster(model.predict(documents.dataset[i]))
	print('*'*40)
	clust = interpret_cluster(documents)
	if outfile_name is not None:
		with open(outfile_name, 'w') as f:
			for key, value in clust.items():
				str_data = "Cluster " + str(key+1) + ' (' + str(len(value)) + ' items): ' + str([int(i) for i in value]) + '\n\n'
				f.write(str_data)
			print('Wrote data to file: ' + outfile_name)
	else:
		print('\nClusters found:\n')
		for key, value in clust.items():
			str_data = "Cluster " + str(key+1) + ' (' + str(len(value)) + ' items): ' + str([int(i) for i in value])
			print(str_data)
			print()
