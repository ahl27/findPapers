## Running the Script

Run this script with `python3 main.py`.

See definition of user parameters below.

## User Parameters

Parameters are defined within `main.py`.

##### Example usage:
```
toolname = 'ahl27litreview'

email = 'example@example.com'

init_pmids = ['24349035']

verbose = True

depth = 1

nclust = 2

terms = [['coevolution', 'coevolutionary', 'cooccurence'], ['phylogenetic', 'profile', 'phylogeny', 'mirrortree', 'contexttree']]
```

##### Explanations:

Required params to use NCBI API:

* toolname: name of tool, set it to some random string. 
  * ex. 'alakshmantool’
* email: email address for contacting if there's a problem.
  * ex. 'a@gmail.com'
* init_pmids: PubMed IDs to build a network from, as a comma separated list of numbers. 
  * Should be fine as strings or integers. 
  * If only using a single ID, still put it into a list (like `['1']`)
  * ex. `['001', '002', '003']`

Additional parameters:

*  verbose: `True` to print out progress, `False` to suppress most output 
  * default: `True`
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
