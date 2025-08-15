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
    result = {}
    if len(corpus[page]) == 0:
        pr = 1 / len(corpus)
        for p in corpus:
            result[p] = pr
        return result

    prob_from_link = damping_factor/len(corpus[page])

    for p in corpus[page]:
        result[p] = prob_from_link

    prob_from_random_jump = (1-damping_factor) / len(corpus)

    for p in corpus:
        result[p] = result.get(p, 0) + prob_from_random_jump

    return result



def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    counter = {p: 0 for p in corpus}

    corpus_keys = [k for k in corpus.keys()]
    curr_page = random.choice(corpus_keys)

    counter[curr_page] = counter.get(curr_page, 0) + 1

    for _ in range(n-1):
        probability_distribution = transition_model(corpus, curr_page, damping_factor)
        choices = [k for k in probability_distribution.keys()]
        weights = [v for v in probability_distribution.values()]
        curr_page = random.choices(choices, weights=weights)[0]
        counter[curr_page] = counter.get(curr_page, 0) + 1

    for k, _ in counter.items():
        counter[k] = counter.get(k, 0) / n

    return counter



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    n = len(corpus)
    curr_page_rank = {k: 1/n for k in corpus.keys()}

    page_links = {k: [] for k in corpus.keys()}

    for page in corpus.keys():
        for link_page in corpus[page]:
            page_links[link_page].append(page)

    while True:
        new_page_rank = {}
        for page in corpus:
            random_jump_probability = (1-damping_factor) / n
            endorsement_probability = 0
            for link_page in page_links[page]:
                if len(corpus[link_page]) != 0:
                    endorsement_probability += curr_page_rank[link_page] / len(corpus[link_page])
                else:
                    endorsement_probability += curr_page_rank[link_page] / n
            new_page_rank[page] = random_jump_probability + damping_factor * endorsement_probability

        similar = {k: False for k in corpus.keys()}

        for page in corpus:
            if abs(new_page_rank[page] - curr_page_rank[page]) <= 0.001:
                similar[page] = True

        if all(similar.values()):
            return new_page_rank

        curr_page_rank = new_page_rank


if __name__ == "__main__":
    main()
