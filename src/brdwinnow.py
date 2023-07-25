import logging

brd_logger = logging.getLogger('brd_log')

# turn a file into a comparable vector
# for winnowing, we need to read the paper
def file_to_vector(filepath):

    vector = {}

    try:
        with open(filepath) as infile:
            raw_contents = infile.read()

    except Exception as err:
        brd_logger.error(f"Error turning {filepath} to a comparable vector: {type(filepath)}: {err}")

    return vector

# return a similarity score between 1-10
def compare_vectors(a, b):
    return len(a)