import logging
import re
import difflib

brd_logger = logging.getLogger('brd_log')

# turn a file into a comparable vector
# for whitespace, we remove every non-whitespace character and then do Ratcliff-Obershelp "gestalt pattern matching"
def file_to_vector(filepath):

    vector = []

    try:
        with open(filepath, "rb") as infile:

            raw_contents = infile.read().decode(errors="backslashreplace")

            substitution_regex = r'[^\s]+'

            whitespace_only = "".join(list(re.sub(substitution_regex,"",raw_contents)))

            # shorten sequences of > 2 newlines
            cut_vspace = r'\r?[\n]\r?[\n]\r?[\n]+'
            two_newlines = "\n\n"
            if "\r" in whitespace_only:
                two_newlines = "\r\n\r\n"
            
            whitespace_only_trimmed = re.sub(cut_vspace, two_newlines, whitespace_only)

            brd_logger.debug(f"{filepath}: {list(whitespace_only_trimmed)}")
            vector += list(whitespace_only_trimmed)

    except Exception as err:
        brd_logger.error(f"Error turning {filepath} to a comparable vector: {type(filepath)}: {err}")
        exit(76)

    return vector

S = difflib.SequenceMatcher(None, a="", b="")

# return a similarity score between 0-10
# 
def compare_vectors(a, b):

    S.set_seq1(a)
    S.set_seq2(b)
    similarity_score1 = S.ratio() * 10
    S.set_seq1(a)
    S.set_seq2(b)
    similarity_score2 = S.ratio() * 10
    similarity_score = (similarity_score1 + similarity_score2) / 2
    brd_logger.debug(f"Comparison yielded a score of: {similarity_score}")
    return similarity_score
