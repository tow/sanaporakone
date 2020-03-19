import json
import random

from django.http import HttpResponse


from . import generator

persons = {"minä": "SG1", "sinä": "SG2", "hän": "SG3", "me":"PL1", "te": "PL2", "he": "PL3"}
tenses = {"preseens": "PRESENT", "imperfekti": "PAST", "perfekti": "PERFECT", "plusqvamperfekti": "PLUSQUAMPERFECT"}

def get_word(req_verb, req_verbtypes):
    if req_verb:
        verbs = [(req_verb.lower(),)]
    elif req_verbtypes:
        verbs = []
        for verbtype in req_verbtypes:
            verbs.extend(generator.verbs_by_verbtype[verbtype])
    else:
        verbs = generator.verbs
    word = random.choice(verbs)
    return word

def get_modifiers(req_tenses, req_negative):
    if req_tenses:
        tense_list = req_tenses
    else:
        tense_list = list(tenses)
    tense = random.choice(tense_list)

    if req_negative:
        negative = False
    else:
        negative = random.choice((True, False))

    person = random.choice(list(persons))

    return tense, negative, person

def get_answer(word, tense, negative, person):
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

    return answer

def generate_example(request):
    req_verb = request.GET.get("verb")
    req_verbtypes = request.GET.getlist("verbtype")
    word = get_word(req_verb, req_verbtypes)
    verbtype = word[2]

    req_tenses = request.GET.getlist("tense")
    req_negative = "ignore_negative" in request.GET
    tense, negative, person = get_modifiers(req_tenses, req_negative)

    answer = get_answer(word, tense, negative, person)

    index = str(verbtype) + \
        {"preseens":"1", "imperfekti":"2", "perfekti":"3", "plusqvamperfekti":"4"}[tense] + \
        ("2" if negative else "1") + \
        {"minä":"1", "sinä":"2", "hän":"3", "me":"4", "te":"5", "he":"6"}[person]

    example = {"index": index, "infinitive": word[0], "person": person, "tense": tense, "negative": negative, "answer": answer}

    return HttpResponse(json.dumps(example))
