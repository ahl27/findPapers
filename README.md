## Running the Script

Run this script with `python3 main.py`.
This script is implemented almost entirely in base Python3.
Only dependencies should be numpy and Python >= 3.7.

See definition of user parameters below.

NCBI enforces an API access limit of 3 requests/second, which is the main speed bottleneck. 
This script queries at a rate of approximately 7,000 calls per hour. I might go back and make it more 
efficient later, but this is pretty close to the ideal limit of 10,800 calls per hour.

You can generate an API key from your account on NCBI, and use this in the `api_key` argument. 
This is supposed to increase the limit to 10 requests/second, which should improve processing time.
Even with this, though, my rate is still roughly 2 abstracts processed per second.

Tested and working on Pythonista 3 for iPad. 

## User Parameters

Parameters are defined within `main.py`.

##### Example usage:
```
toolname = 'ahl27litreview'

email = 'example@example.com'

init_pmids = ['24349035']

api_key = None

outfile_name = 'filesfound.txt'

verbose = True

depth = 1

nclust = 2

terms = [['coevolution', 'coevolutionary', 'cooccurence'], ['phylogenetic', 'profile', 'phylogeny', 'mirrortree', 'contexttree']]
```

##### Explanations:

Required params to use NCBI API:

* toolname: name of tool, set it to some string corresponding with your project. 
  * ex. `'alakshmantool’`
* email: email address for contacting if there's a problem.
  * ex. `'a@gmail.com'`
* init_pmids: PubMed IDs to build a network from, as a comma separated list of numbers. 
  * Should be fine as strings or integers. 
  * If only using a single ID, still put it into a list (like `['1']`)
  * ex. `['001', '002', '003']`

Note that if you do not provide an email and toolname your requests may be blocked. Supplying an
invalid email address will mean NCBI cannot contact you if there's a problem, and can result in
your IP address being blacklisted from using any NCBI API commands.

Additional parameters:

* verbose: `True` to print out progress, `False` to suppress most output 
  * default: `True`
* api_key: Input your API key as a string, or use `None` if you don't have one.
  * ex. `None` or `'123456789abcdef'`
* outfile_name: file to save results to. Set to `None` to print out output instead of saving.
  * ex. `fileout.txt` or `None`
* depth: How far into the network to go. 
  * ex. `3`
  * Depth=n means that all papers returned will be within n distance from at least one paper in init_pmids. A paper that cites or is cited by a given paper are distance 1 away from each other.
  * CAUTION: The number of papers returned grows incredibly rapidly with depth. The example returns 35 papers at depth 1, and \~32,000 at depth 2.
* nclust: Number of clusters to cluster into.
  * ex. `3` 
* terms: Search terms, organized as a list of lists. 
  * Within each nested list, the abstract must contain at least one word from it.
  * The format is essentially: `[ [1, 2], [3, 4] ]` => (1 OR 2) AND (3 OR 4)
  * Leave empty ( `[]` ) to just grab everything.
  * only use lowercase letters--abstract is lowercased before it's filtered. Additionally, hyphens are removed. 
    * "Co-Evolution" becomes "coevolution"
  * ex. `[['streptomyces', 'pseudomonas'], ['antibiotics']]`
    * This returns abstracts that include both 'antibiotics' and at least one term from (streptomyces, pseudomonas)

## Example Output:

```
Finding papers from initial paper(s)...

Search depth of 1
1 element(s) to search.
[=========================] (1/1)
35 papers found.

Finding abstracts...
[=========================] (35/35)

8 total abstracts matched search criteria.

Clustering with k-means (k=2)...
****************************************

Clusters found:

Cluster 1 (4 items): [18930732, 18199838, 16139301, 24349035]

Cluster 2 (4 items): [23458856, 18818697, 20363731, 32043173]
```
