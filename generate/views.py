import json
import random

from django.http import HttpResponse


from . import generator

persons = {"minä": "SG1", "sinä": "SG2", "hän": "SG3", "me":"PL1", "te": "PL2", "he": "PL3"}
tenses = {"preseens": "PRESENT", "imperfekti": "PAST", "perfekti": "PERFECT", "plusqvamperfekti": "PLUSQUAMPERFECT"}

def generate_example(request):
    print(request.GET)
    req_verb = request.GET.get("verb")
    if req_verb:
        word = req_verb
    else:
        word = random.choice(generator.verbs)
    req_tenses = request.GET.getlist("tense")
    if req_tenses:
        tense_list = req_tenses
    else:
        tense_list = tenses.keys()
    tense = random.choice(tense_list)
    negatives = (True, False)
    person, negative = random.choice(list(persons)), random.choice(negatives)
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
