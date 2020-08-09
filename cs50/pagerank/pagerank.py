import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    hop_chance = 1 - damping_factor
    probability_matrix = {k:hop_chance for k in corpus.keys()}
    outgoing = corpus[page]
    move_on = damping_factor / len(outgoing)
    for link in outgoing:
        probability_matrix[link] = probability_matrix[link] + move_on

    return probability_matrix


def weighted_choose(prob_matrix):
    """
    Given a probability matrix (dictionary k:v where k is page and
    v is the corresponding weight), choose a page at random such that
    the probability that a page is chosen is that of
    (weight / total_weight)%

    The idea of this is similar to creating an interval of the total
    weights and assigning allotments of this interval based on the
    specified weights. Yet instead of creating the memory for these
    allotments, we pretend these allotments are passed over by each
    iteration by subtracting the allocated weight.
    """

    #items = list(prob_matrix.keys())
    #weights = [prob_matrix[x] for x in items]
    #return random.choices(items, weights=weights,k=1)[0]

    normal_factor = 1000
    prob_matrix = {k:v*normal_factor for k,v in prob_matrix.items()}
    total_weight = sum(prob_matrix.values())
    r = random.randint(1, total_weight)
    for page, weight in prob_matrix.items():
        r -= weight
        if r <= 0.001:
            return page


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    current_page = list(corpus.keys())[0]
    starting_rank = 0
    ranking_dict = {k:starting_rank for k in corpus.keys()}
    all_prob = {k:transition_model(corpus, k, damping_factor) for k in corpus.keys()}
    print(all_prob)
    inc = 1/n
    for i in range(n):
        prob_dict = all_prob[current_page]
        ranking_dict[current_page] += inc
        current_page = weighted_choose(prob_dict)
    return ranking_dict



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
