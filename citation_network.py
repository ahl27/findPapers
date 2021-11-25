import requests
import xmltodict
import re
from time import sleep
from stopwords import stopwords

def find_citing_articles(pmid, toolname, email, apikey, return_pmids=True, use_pmcid=False):
	# By default returns a list of PMIDs that cite the given article in PubMed
	params = {'id': pmid, 'tool': toolname, 'email': email,
						'linkname': 'pubmed_pmc_refs', 'dbfrom': 'pubmed'}
	if apikey is not None:
		params['api_key'] = apikey
	if (return_pmids):
		params['linkname'] = 'pubmed_pubmed_citedin'
	elif (use_pmcid):
		params['linkname'] = 'pmc_pmc_citedby'
	
	return(make_request(params))


def find_cited_articles(pmid, toolname, email, apikey, pmc_refs_only=False, id_by_pmid=True):
	# Returns a list of all articles cited by the article
	params = {'id': pmid, 'tool': toolname, 'email': email,
						'linkname': 'pmc_refs_pubmed', 'dbfrom': 'pmc'}
	if apikey is not None:
		params['api_key'] = apikey
	if (pmc_refs_only):
		params['linkname'] = 'pmc_pmc_cites'
	elif (id_by_pmid):
		params['linkname'] = 'pubmed_pubmed_refs'
		params['dbfrom'] = 'pubmed'
	
	return(make_request(params))
	
	
def make_request(params):
	request = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi'
	r = requests.get(request, params=params)
	
	# Only 3 requests are allowed per second, delay if we're sending too many
	# Using an API key supposedly increases the limit to 10/sec
	while r.status_code != 200:
		sleep(0.33)
		r = requests.get(request, params=params)
	ids = []
	parsed = xmltodict.parse(r.text)
	
	if ('LinkSetDb' not in parsed['eLinkResult']['LinkSet'].keys()):
		return(ids)
		
	cites = parsed['eLinkResult']['LinkSet']['LinkSetDb']['Link']
	for elem in cites:
		if len(elem) > 1:
			pass
		else:
			ids.append(elem['Id'])
		
	return(ids)
	

def get_abstract(id, toolname, email, apikey):
	request = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
	params = {'db': 'pubmed', 'id': id, 'tool': toolname, 'email': email,
						'retmode': 'JSON', 'rettype': 'abstract'}
	if apikey is not None:
		params['api_key'] = apikey
	r = requests.get(request, params=params)
	while r.status_code != 200:
		sleep(0.33)
		r = requests.get(request, params=params)
	r = r.text
	r = r.split('\n\n')[4]
	r = r.replace('\n', ' ')

	return(tokenize_abstract(r))

def tokenize_abstract(abstract):
	alph_abs = abstract.replace('-', '')
	alph_abs = re.sub("[^0-9a-zA-Z]+", " ", alph_abs).lower().strip()
	tokens = alph_abs.split(' ')
	tokens = [word for word in tokens if word not in stopwords]

	return(tokens)

def print_progress_bar(k, maxk, barwidth=25, forcesame=False, time_per_k = 0.45):
	# 0.5 is about how fast it can compute based on my machine
	# at the end of the day it's really just an estimate
	if k == 0 and not forcesame:
			print('[' + (' '*barwidth) + '] (0/' + str(maxk) + ')', end='')
	else:
		num_bars = int((k/maxk) * barwidth)
		prog = '=' * num_bars
		spacer = ' ' * (barwidth - num_bars)
		remaining_sec = int((maxk - k) * time_per_k + 0.5)
		remaining_hr = remaining_sec // 3600
		remaining_min = (remaining_sec % 3600) // 60
		remaining_sec = remaining_sec % 60
		timestring = "{hr}:{min:02d}:{sec:02d}".format(hr=remaining_hr, min=remaining_min, sec=remaining_sec)
		print('\r' + '[' + prog + spacer + '] (' + str(k) + '/' + str(maxk) + ', ' + timestring + ')', end='')
	
	if k == maxk:
		print()
		
	
def gen_paper_network(pmids, toolname, email, apikey, depth, verbose=True):
	network = {}
	temp = pmids
	all_pmids = set(pmids)
	
	for j in range(1,(depth+1)):
		print("\nSearch depth of " + str(j))
		num_elements = len(temp)
		print(str(num_elements) + " element(s) to search.")
		cur = set(temp)
		temp = []
		if verbose:
			k = 0
			print_progress_bar(0, num_elements)
		for item in cur: 
			temp = temp + find_citing_articles(item, toolname, email, apikey) + find_cited_articles(item, toolname, email, apikey)
			all_pmids.update(temp)
			if verbose:
				k += 1 
				print_progress_bar(k, num_elements)
				
	return(list(all_pmids))
	
def abstracts_from_network(network, toolname, email, apikey, terms, verbose=True):
	abstracts = {}
	maxlen = len(network)
	if verbose:
		print_progress_bar(0, maxlen)
		k = 0
	for item in network:
		abstract = get_abstract(item, toolname, email, apikey)
		flag = True
		if terms is not []:
			flag = find_search_terms(abstract, terms)
		if flag:
			abstracts[item] = abstract
		if verbose:
			k += 1
			print_progress_bar(k, maxlen, forcesame=True)
		
	return(abstracts)
	
def find_search_terms(corpus, terms):
	state = True
	for term_list in terms:
		state = state and any([term in corpus for term in term_list])
	return(state)

def abstract_network(init_pmids, toolname=None, email=None, apikey=None, depth=1, search_terms=[], verbose=True):
	if any(i is None for i in [toolname, email]):
		raise Exception("Tool and Email name must be specified")
	if verbose:
		print("Finding papers from initial paper(s)...")
	network = gen_paper_network(init_pmids, toolname, email, apikey, depth, verbose)
	if verbose:
		print(str(len(network)) + " papers found.\n")
		print("Finding abstracts...")
	abstracts = abstracts_from_network(network, toolname, email, apikey, search_terms, verbose)
	
	return(abstracts)
		
			
if __name__ == '__main__':
	toolname = 'ahl27litreview'
	email = 'pmcsearch@ahl27.com'
	apikey = None
	init_pmids = ['24349035']
	search_terms = [['coevolution', 'coevolutionary', 'cooccurence'],
								['phylogenetic', 'profile', 'phylogeny', 'mirrortree', 'contexttree']]
		
	print(abstract_network(init_pmids, toolname, email, apikey, search_terms=search_terms))
