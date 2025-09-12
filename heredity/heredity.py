from collections import defaultdict
import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )

        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)
    print(probabilities)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def calculate_gene(one_gene, two_genes, person):
    if person in one_gene:
        return 1
    elif person in two_genes:
        return 2
    else:
        return 0

def calculate_no_parents_prob(gene_nums, has_trait, person):
    return PROBS["gene"][gene_nums]

def calculate_parents_prob(person, mother_gene, father_gene, gene_nums, has_trait):
    gene_passing_prob = {
        0: PROBS['mutation'],
        1: 0.5,
        2: 1 - PROBS['mutation']
    }

    p_m = gene_passing_prob[mother_gene]
    p_f = gene_passing_prob[father_gene]

    if gene_nums == 0:
        return (1 - p_m) * (1 - p_f)
    elif gene_nums == 1:
        return (p_m * (1 - p_f)) + (p_f * (1 - p_m))
    else:
        return p_m * p_f


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probability = 1.0

    for person, person_data in people.items():
        gene_nums = calculate_gene(one_gene, two_genes, person)
        has_trait = True if person in have_trait else False

        mother = person_data['mother']
        father = person_data['father']

        mother_gene = calculate_gene(one_gene, two_genes, mother)
        father_gene = calculate_gene(one_gene, two_genes, father)

        gene_prob = 0
        if mother is None:
            gene_prob = calculate_no_parents_prob(gene_nums, has_trait, person)
        else:
            gene_prob = calculate_parents_prob(person, mother_gene, father_gene, gene_nums, has_trait)

        probability *= PROBS['trait'][gene_nums][has_trait] * gene_prob

    return probability






def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities.keys():
        nums_gene = calculate_gene(one_gene, two_genes, person)
        has_trait = True if person in have_trait else False
        probabilities[person]["gene"][nums_gene] += p
        probabilities[person]["trait"][has_trait] += p




def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person, person_prob_data in probabilities.items():
        s_gene = sum([x for x in person_prob_data['gene'].values()])
        s_trait = sum([x for x in person_prob_data['trait'].values()])

        probabilities[person]['gene'][0] /=  s_gene
        probabilities[person]['gene'][1] /=  s_gene
        probabilities[person]['gene'][2] /=  s_gene

        probabilities[person]['trait'][True] /= s_trait
        probabilities[person]['trait'][False] /= s_trait





if __name__ == "__main__":
    main()
