import fnmatch
import logging

brd_logger = logging.getLogger('brd_log')

class brdignorelist:

    def __init__(self, brdignore_path):
        brd_logger.debug("Creating new brdignorelist object.")
        self.brdignore_directives = []

        try:
            # load .brdignore if it exists, split by newlines, and ignore those file extensions
            with open(brdignore_path) as brdignore_file:
                self.brdignore_directives = sorted(list(set(list(a.strip() for a in brdignore_file.read().split("\n")))))
                if "" in self.brdignore_directives:
                    self.brdignore_directives.remove("")
                self.brdignore_directives.append(brdignore_path)
                brd_logger.info(f"Ignoring the following wildcards: {self.brdignore_directives}")


        except Exception as err:
            brd_logger.error(f"Error reading .brdignore file at {brdignore_path}: {type(err)}: {err}")
            exit(8)

    # Return None if the filepath should not be ignored
    # Return the directive that ignores the file otherwise
    def ignore(self, filepath):
        for d in self.brdignore_directives:
            if fnmatch.fnmatch(filepath, d):
                return d
        return None    
        