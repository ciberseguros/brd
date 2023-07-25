import logging
import threading
from multiprocessing import cpu_count

brd_logger = logging.getLogger('brd_log')

class brdanalyzer:

    def __init__(self, filelist, outfile):
        try:
            with open(outfile, "w") as of:
                of.write("# BRD Plagiarism Analysis Engine Report\n\n")
        except Exception as err:
            brd_logger.error(f"Error initializing outfile: {type(err)}: {err}")
            brd_logger.error(f"Given filepath: {outfile}")
            exit(42)
        brd_logger.debug(f"Outfile successfully initialized at {outfile}.")
        
        self.threadcount = cpu_count()
        self.filelist = filelist
        self.outfile = outfile
        return None
    
    def do_whitespace_ngrams(self):
        brd_logger.warn("Whitespace ngrams not yet implemented")
        pass

    def do_tokenized_ngrams(self):
        brd_logger.warn("Tokenized ngrams not yet implemented")
        pass

    def do_winnowing_hash(self):
        brd_logger.warn("Winnowing hashes not yet implemented")
        pass

    def write_report(self):
        brd_logger.debug("Writing report")

        try:
            with open(self.outfile) as report:
                report.write("No findings")

        except Exception as err:
            brd_logger.error(f"Error initializing outfile: {type(err)}: {err}")
            brd_logger.error(f"Given filepath: {outfile}")
            exit(99)
