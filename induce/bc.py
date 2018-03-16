import induce.config as config

class bc:
    header = '\033[95m'
    okblue = '\033[94m'
    okgreen = '\033[92m'
    warning = '\033[93m'
    fail = '\033[91m'
    endc = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'
    def __init__(self, c): self.c = c
    def o(self, v): return self.c + v + bc.endc if config.Show_Colors else v
    def __call__(self, v): return self.o(v)
