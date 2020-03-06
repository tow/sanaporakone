
import csv
import os

import omorfi

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

verbs = None

def read_verbtypes(filename):
    verbtypes = {}
    with open(filename) as csvfile:
        tsv_reader = csv.reader(csvfile, delimiter='\t')
        for row in tsv_reader:
            verbtypes[row[0]] = row[1]
    return verbtypes

def read_verbs(verbfilename, verbtypesfilename):
    verbtypes = read_verbtypes(verbtypesfilename)
    verbs = []
    with open(verbfilename) as csvfile:
        tsv_reader = csv.reader(csvfile, delimiter='\t')
        for row in tsv_reader:
            if row[0] == "VERB":
                verb = row[1]
                if row[2] != "1":
                    verb += "_"+row[2]
                verbtype = row[3]
                verbs.append((verb, verbtype, verbtypes[verbtype]))
    return verbs

def initialize_verbs():
    global verbs
    o = omorfi.Omorfi()
    o.load_generator(os.path.join(BASE_DIR, "data/omorfi.generate.hfst"))
    verbs = read_verbs(os.path.join(BASE_DIR, "data/master.tsv"), os.path.join(BASE_DIR, "data/verbityypit.tsv"))
