
import csv
import os

import omorfi

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


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
    vbvt = {'0':[], '1':[], '2':[], '3':[], '4':[], '5':[], '6':[]}
    lastverb = ""
    with open(verbfilename) as csvfile:
        tsv_reader = csv.reader(csvfile, delimiter='\t')
        for row in tsv_reader:
            if row[0] == "VERB":
                verb = row[1]
                if row[2] != "1" and lastverb == verb:
                    # TODO. Work out something sensible to do with duplicate verbs
                    continue
                verbtype = row[3]
                gen_vt = verbtypes[verbtype]
                verbs.append((verb, verbtype, gen_vt))
                vbvt[gen_vt].append((verb, verbtype))
                lastverb = verb

    return verbs, vbvt


omorfi_instance = omorfi.Omorfi()
omorfi_instance.load_generator(os.path.join(BASE_DIR, "data/omorfi.generate.hfst"))
verbs, verbs_by_verbtype = read_verbs(os.path.join(BASE_DIR, "data/master.tsv"), os.path.join(BASE_DIR, "data/verbityypit.tsv"))


def generate(word, upos, omors=""):
    """Generate word-form."""
    wf = omorfi_instance.generate("[WORD_ID=" + word + "][UPOS=" + upos + "]" +
                            omors)
    if not wf:
        return '---'
    else:
        return wf

def generate_negative_verb(person):
    return {
        "SG1": "en",
        "SG2": "et",
        "SG3": "ei",
        "PL1": "emme",
        "PL2": "ette",
        "PL3": "eivät",
    }[person]

def generate_simple_verb(word, person, tense):
    spec = "[VOICE=ACT][MOOD=INDV][TENSE={tense}][PERS={person}]"
    return generate(word, "VERB", spec.format(person=person, tense=tense))

def generate_negated_verb(word, person, tense):
    negative_verb = generate_negative_verb(person)
    if tense == "PRESENT":
        spec = "[VOICE=ACT][MOOD=INDV][TENSE=PRESENT][NEG=CON]"
    elif tense == "PAST":
        spec = "[VOICE=ACT][MOOD=INDV][TENSE=PAST][NUM={pers}][NEG=CON]"
    conneg = generate(word, "VERB", spec.format(pers=person[:2]))
    return negative_verb + " " + conneg


def generate_perfect_verb(word, person, tense):
    spec = "[VOICE=ACT][MOOD=INDV][TENSE=PRESENT][PERS={person}]"
    verb = generate("olla_2", "VERB", spec.format(person=person))
    if tense == "PLUSQUAMPERFECT":
        if person[:2] == "SG":
            ollut = "ollut"
        elif person[:2] == "PL":
            ollut = "olleet"
        verb = verb + " " + ollut
    spec = "[VOICE=ACT][MOOD=INDV][TENSE=PAST][NUM={pers}][NEG=CON]"
    pcp = generate(word, "VERB", spec.format(pers=person[:2]))
    return verb + " " + pcp

def generate_negated_perfect_verb(word, person, tense):
    if tense == "PERFECT":
        verb = generate_negated_verb("olla_2", person, "PRESENT")
    else:
        verb = generate_negative_verb(person)
        if person[:2] == "SG":
            ollut = "ollut"
        elif person[:2] == "PL":
            ollut = "olleet"
        verb = verb + " " + ollut
    spec = "[VOICE=ACT][MOOD=INDV][TENSE=PAST][NUM={pers}][NEG=CON]"
    pcp = generate(word, "VERB", spec.format(pers=person[:2]))
    return verb + " " + pcp
