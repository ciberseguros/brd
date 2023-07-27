import logging
import difflib
import re

brd_logger = logging.getLogger('brd_log')

# turn a file into a comparable vector
# for tokenized_ngrams, we need to read the paper
def file_to_vector(filepath):

    vector = []

    try:
        with open(filepath, "rb") as infile:
            raw_contents = infile.read().decode(errors="backslashreplace")

            # shorten sequences of > 2 newlines
            cut_vspace = r'\r?[\n]\r?[\n]\r?[\n]+'
            two_newlines = "\n\n"
            if "\r" in raw_contents:
                two_newlines = "\r\n\r\n"
            
            raw_contents_trimmed = re.sub(cut_vspace, two_newlines, raw_contents)

            vector = raw_contents_trimmed

    except Exception as err:
        brd_logger.error(f"Error turning {filepath} to a comparable vector: {type(filepath)}: {err}")
        exit(55)

    return vector

S = difflib.SequenceMatcher(lambda x: x in "\r\n", a="", b="")

# return a similarity score between 0-10
# 
def compare_vectors(a, b):
    S.set_seq1(a)
    S.set_seq2(b)
    similarity_score1 = S.ratio() * 10
    S.set_seq1(b)
    S.set_seq2(a)
    similarity_score2 = S.ratio() * 10
    similarity_score = (similarity_score1 + similarity_score2) / 2
    brd_logger.debug(f"Comparison yielded a score of: {similarity_score}")
    return similarity_score