import json
import random

from django.http import HttpResponse


from . import generator

persons = {"minä": "SG1", "sinä": "SG2", "hän": "SG3", "me":"PL1", "te": "PL2", "he": "PL3"}
tenses = {"preseens": "PRESENT", "imperfekti": "PAST", "perfekti": "PERFECT", "plusqvamperfekti": "PLUSQUAMPERFECT"}

def generate_example(request):
    req_verb = request.GET.get("verb")
    req_verbtypes = request.GET.getlist("verbtype")
    if req_verb:
        verbs = [(req_verb,)]
    elif req_verbtypes:
        verbs = []
        for verbtype in req_verbtypes:
            verbs.extend(generator.verbs_by_verbtype[verbtype])
    else:
        verbs = generator.verbs
    word = random.choice(verbs)

    req_tenses = request.GET.getlist("tense")
    if req_tenses:
        tense_list = req_tenses
    else:
        tense_list = list(tenses)
    tense = random.choice(tense_list)

    if "ignore_negative" in request.GET:
        negative = False
    else:
        negative = random.choice((True, False))

    person = random.choice(list(persons))

    if tense in ("perfekti", "plusqvamperfekti"):
        if negative:
            answer = generator.generate_negated_perfect_verb(word[0], persons[person], tenses[tense])
        else:
            answer = generator.generate_perfect_verb(word[0], persons[person], tenses[tense])
    else:
        if negative:
            answer = generator.generate_negated_verb(word[0], persons[person], tenses[tense])
        else:
            answer = generator.generate_simple_verb(word[0], persons[person], tenses[tense])

    example = {"infinitive": word[0], "person": person, "tense": tense, "negative": negative, "answer": answer}

    return HttpResponse(json.dumps(example))
