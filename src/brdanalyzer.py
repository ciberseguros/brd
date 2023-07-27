import logging
import threading
from multiprocessing import cpu_count
import brdtokenngram, brdwhitespace, brdwinnow
from datetime import datetime

brd_logger = logging.getLogger('brd_log')
md_escaped_backslash = "\\_"

WINNOWNING_DEFAULT_THRESHOLD = 5
TOKENIZED_NGRAMS_TEST_DEFAULT_THRESHOLD = 5
WHITESPACE_GESTALT_DEFAULT_THRESHOLD = 5

class brdanalyzer:

    def __init__(self, filelist, outfile, thresholds):
        try:
            with open(outfile, "w") as of:
                timestamp = datetime.now()
                of.write(f"# BRD Plagiarism Analysis Engine Automated Report \nGenerated at {timestamp}\n\n")
        except Exception as err:
            brd_logger.error(f"Error initializing outfile: {type(err)}: {err}")
            brd_logger.error(f"Given filepath: {outfile}")
            exit(42)
        brd_logger.debug(f"Outfile successfully initialized at {outfile}.")
        
        self.threadcount = cpu_count()
        self.filelist = filelist
        self.outfile = outfile
        self.thresholds = thresholds
        self.default_thresholds = {
            "Whitespace Gestalt Test"       : WHITESPACE_GESTALT_DEFAULT_THRESHOLD,
            "Tokenized Ngrams Test" : TOKENIZED_NGRAMS_TEST_DEFAULT_THRESHOLD,
            "Winnowing Hash Test"   : WINNOWNING_DEFAULT_THRESHOLD
        }
        return None
    
    def do_whitespace_ngrams(self):
        self.whitespace_results = []
        self.whitespace_vectors = []

        #TODO parallelize
        for file in self.filelist:
            self.whitespace_vectors.append(brdwhitespace.file_to_vector(file))
        
        for i, a in enumerate(self.filelist):
            for j, b in enumerate(self.filelist):
                if a <= b:
                    continue #Skip self-comparisions, and duplicates
                brd_logger.debug(f"Comparing {i}:{a} to {j}:{b}")

                similarity_score = brdwhitespace.compare_vectors(self.whitespace_vectors[i],self.whitespace_vectors[j])

                assert type(similarity_score) in [int, float], f"Similarity Score was not a number, but rather a {type(similarity_score)}"

                self.whitespace_results.append([a, b, similarity_score])

        pass

    def do_tokenized_ngrams(self):
        self.tokenized_ngrams_result = []
        self.tokenized_ngrams_vectors = []

        brd_logger.warn("Tokenized ngrams not yet implemented correctly. It is currently a gestalt match")
        for file in self.filelist:
            self.tokenized_ngrams_vectors.append(brdtokenngram.file_to_vector(file))

        for i, a in enumerate(self.filelist):
            for j, b in enumerate(self.filelist):
                if a <= b:
                    continue #Skip self-comparisions, and duplicates
                brd_logger.debug(f"Comparing {i}:{a} to {j}:{b}")

                similarity_score = brdtokenngram.compare_vectors(self.tokenized_ngrams_vectors[i],self.tokenized_ngrams_vectors[j])

                assert type(similarity_score) in [int, float], f"Similarity Score was not a number, but rather a {type(similarity_score)}"

                self.tokenized_ngrams_result.append([a, b, similarity_score])
        #TODO parallelize
        pass

    def do_winnowing_hash(self):
        self.winnowing_hash_result = []
        self.winnowing_hash_vectors = []

        brd_logger.warn("Winnowing hashes not yet implemented")
        for file in self.filelist:
            self.winnowing_hash_vectors.append(brdwinnow.file_to_vector(file))

        for i, a in enumerate(self.filelist):
            for j, b in enumerate(self.filelist):
                if a <= b:
                    continue #Skip self-comparisions, and duplicates
                brd_logger.debug(f"Comparing {i}:{a} to {j}:{b}")

                similarity_score = brdwinnow.compare_vectors(self.winnowing_hash_vectors[i],self.winnowing_hash_vectors[j])

                assert type(similarity_score) in [int, float], f"Similarity Score was not a number, but rather a {type(similarity_score)}"

                self.winnowing_hash_result.append([a, b, similarity_score])    
        #TODO parallelize
        pass

    def _compute_clusters(self):
        try:
            brd_logger.info("Computing Clusters of Results")
            self.clusters = []
            results = {
                "Whitespace Gestalt Test" : self.whitespace_results,
                "Tokenized Ngrams Test" : self.tokenized_ngrams_result,
                "Winnowing Hash Test" : self.winnowing_hash_result
            }
            names = list(self.thresholds.keys())

            self.pairs = []
            for result_src, resultset in results.items():
                threshold = self.thresholds[result_src]
                assert type(threshold) in [int, float], "Thresholds must be specified as integers or floats"
                assert 0 <= threshold <= 10, "Thresholds must be between 0 and 10, inclusive"

                for result in resultset:
                    
                    pathA = result[0]
                    pathB = result[1]
                    sscore = result[2]

                    assert type(sscore) in [int, float], f"Similarity score must be a number! I see a {type(sscore)} coming from {result_src}"
                    
                    if sscore >= threshold:
                        brd_logger.debug(f"Found a suspicious pair {pathA} <--> {pathB} from {result_src} with similarity score of {sscore} (Threshold was {threshold})")
                        self.pairs.append([result_src] + result)

        except Exception as err:
            brd_logger.error(f"Error while calculating pairs: {type(err)}: {err}")
            exit(70)
        try:
            self.pairgraph = {}

            # Turn pairs into a graph
            for pair in self.pairs:
                PathA = pair[1]
                PathB = pair[2]
                if PathA not in self.pairgraph:
                    self.pairgraph[PathA] = []
                if PathB not in self.pairgraph:
                    self.pairgraph[PathB] = []
                self.pairgraph[PathA].append(PathB)
                self.pairgraph[PathB].append(PathA)

            brd_logger.debug(f"Pairgraph formed: \n{self.pairgraph}")

            # Find connected components using bfs
            self.clusters = set()

            # BFS from every PathA
            for _, start, _, _ in self.pairs:
                cluster = set()
                nextcluster = set([start])
                while "".join(sorted(list(cluster))) != "".join(sorted(list(nextcluster))):
                #while cluster != nextcluster: 
                    cluster = nextcluster.copy()
                    
                    for node in cluster:
                        for reachable in self.pairgraph[node]:
                            nextcluster.add(reachable)
                brd_logger.debug(f"Adding a cluster: {cluster}")
                self.clusters.add(frozenset(cluster))

            brd_logger.info(f"Clusters found:")
            for cluster in self.clusters:
                brd_logger.info(list(cluster))

        except Exception as err:
            brd_logger.error(f"Error while calculating clusters: {type(err)}: {err}")
            raise(err)
            exit(71)
    def write_report(self):
        brd_logger.info("Preparing to write report")

        self._compute_clusters()


        # Actually write the report:
        try:

            msg = ""

            with open(self.outfile, "a") as report:

                # This is ideal, no clusters found :)
                # This will rarely happen in practice if, for example, skeleton code was provided as part of the assignment
                if self.pairs is None or len(self.pairs) == 0: 
                    report.write("No findings. All given files were below the threshold score values that would suggest similarity")
                    return
                
                waswere = f"were {len(self.clusters)} groups"
                if len(self.clusters) == 1:
                    waswere = "was 1 group"

                msg += f"""## TLDR
The BRD analyzer ran over {len(self.filelist)} files and identified {len(self.pairs)} suspiciously similar pairs of files.


After grouping similar files, it appears that there {waswere} of collaborators who shared code or worked with similar reference material.
                
## Similarity Tests Used

BRD uses a combination of techniques to detect similarities among files.

#### Whitespace Gestalt Test

This test detects similarity in structure, even if function and variable names have been changed.

#### Tokenized NGrams Test

This test is not yet implemented

#### Winnowing Hash Test

This test is not yet implemented

### Choosing Detection Thresholds

BRD is a tunable tool, that can be tweaked to handle many situations, including situations where large portions of code were provided as skeleton code.
In such a case, tuning the thresholds up from their defaults would be appropriate.
If you find one of the tests unreliable in your use case, setting the threshold to a full 10 will effectively ignore this test.

The thresholds used in this run were:
| Test Name | Threshold Used | Default Threshold |
| :---: | :---: | :---: |
"""
                for test, threshold in self.thresholds.items():
                    msg += f"| {test} | {threshold} | {self.default_thresholds[test]} |\n"

                msg += """

It is normal to try several parameters in an effort to avoid false positives.
Unfortunately, this tool cannot replace human analysis. 
The goal is merely to direct that attention to the most likely places.

## Sets of Similar Files
The following sets of similar files are strongly connected (in the graph theory sense) through pairwise similarity, but it may be the case that not every file is similar to every other.

*Warning: tuning detection parameters too low will result in one giant set of "similar" files.* If you see this happening (and not everyone plagiarized), take a look at which tests are finding the most similarities and increase their detection threshold.\n
"""

                clusters_sorted = sorted(list(self.clusters), key=lambda x: len(x), reverse=True)
                
                for i, cluster in enumerate(clusters_sorted):
                    msg += f"\n### Cluster {i+1} (size {len(cluster)})\n"
                    msg += "The following files were similar:\n"
                    for file in cluster:
                        msg += f"- {file.replace('_', md_escaped_backslash)}\n"

                    msg += "#### Details of the Detection\nThis cluster is based on the following pairwise matches\n| Path A | Path B | Similarity Score | Test |\n| :---: | :---: | :---: | :---: |\n"


                    for pair in self.pairs:
                        if pair[1] in cluster:
                            PathA = pair[1]
                            PathB = pair[2]
                            
                            msg += f"| {PathA.replace('_', md_escaped_backslash)} | {PathB.replace('_', md_escaped_backslash)} | {pair[3]:.2f}| {pair[0]} |\n"

                msg += "\n\n```\n==========================\nEnd Auto Generated Report\n==========================\n```"

                report.write(msg)
                brd_logger.debug(msg)

        except Exception as err:
            brd_logger.error(f"Error writing outfile: {type(err)}: {err}")
            brd_logger.error(f"Given filepath: {self.outfile}")
            exit(99)
