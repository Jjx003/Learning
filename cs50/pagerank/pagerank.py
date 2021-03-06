import math
import time
import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000

DEFAULT_FMT = '[{elapsed:0.8f}s] {name}({args}) -> {result}'

def clock(fmt=DEFAULT_FMT):
    def decorate(func):
        def clocked(*_args):
            t0 = time.time()
            _result = func(*_args)
            elapsed = time.time() - t0
            name = func.__name__
            args = ', '.join(repr(arg) for arg in _args)
            result = repr(_result)
            print(fmt.format(**locals()))
            return _result
        return clocked
    return decorate

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
    move_on = 0
    outgoing_degree = len(outgoing)
    if outgoing_degree > 0:
        move_on = damping_factor / outgoing_degree

    for link in outgoing:
        prob = probability_matrix[link] + move_on
        if prob > 0:
            probability_matrix[link] = prob

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
    total_weight = int(sum(prob_matrix.values()))
    r = random.randint(1, total_weight)
    for page, weight in prob_matrix.items():
        r -= weight
        if r <= 0.001:
            return page

@clock()
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
    inc = 1/n
    for i in range(n):
        prob_dict = all_prob[current_page]
        ranking_dict[current_page] += inc
        current_page = weighted_choose(prob_dict)
    return ranking_dict


@clock()
def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """


    epsilon = 0.00001
    num_pages = len(corpus)
    hop_chance = (1 - damping_factor) / num_pages

    starting_rank = 1 / num_pages
    # rank_dict_c -> [previous rank, current rank]
    rank_dict_c = {k:[starting_rank, starting_rank] for k in corpus.keys()}
    iterations = 0

    while True:
        iterations += 1
        for page in corpus.keys():
            prev_rank = rank_dict_c[page][1]
            traveled_chance = [
                rank_dict_c[x][0] / len(corpus[x]) for x in corpus.keys()
                if page in corpus[x]
            ]
            traveled_chance = sum(traveled_chance)
            rank_dict_c[page][1] = hop_chance + damping_factor * traveled_chance
            rank_dict_c[page][0] = prev_rank

        total_error = sum([abs(x[1]-x[0]) for x in rank_dict_c.values()]) / num_pages
        if total_error <= epsilon:
            break

    #print(iterations, math.log(num_pages))

    return {k:v[1] for k,v in rank_dict_c.items()}





if __name__ == "__main__":
    main()
