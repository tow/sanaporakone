import json
import random

from django.http import HttpResponse

from verbs.models import Verb
from . import generator

persons = {"minä": "SG1", "sinä": "SG2", "hän": "SG3", "me":"PL1", "te": "PL2", "he": "PL3"}
tenses = {"preseens": "PRESENT", "imperfekti": "PAST", "perfekti": "PERFECT", "plusqvamperfekti": "PLUSQUAMPERFECT"}

def get_word(req_verb, req_verbtypes):
    if req_verb:
        verb_qs = Verb.objects.filter(a_infinitive=req_verb.lower())
    elif req_verbtypes:
        verb_qs = Verb.objects.filter(verbtype_i=verbtype).exclude(glosses=[])
    else:
        verb_qs = Verb.objects.exclude(glosses=[])
    return verb_qs.order_by('?')[0]

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

def get_answer(a_infinitive, tense, negative, person):
    if tense in ("perfekti", "plusqvamperfekti"):
        if negative:
            answer = generator.generate_negated_perfect_verb(a_infinitive, persons[person], tenses[tense])
        else:
            answer = generator.generate_perfect_verb(a_infinitive, persons[person], tenses[tense])
    else:
        if negative:
            answer = generator.generate_negated_verb(a_infinitive, persons[person], tenses[tense])
        else:
            answer = generator.generate_simple_verb(a_infinitive, persons[person], tenses[tense])

    return answer

def generate_example(request):
    req_verb = request.GET.get("verb")
    req_verbtypes = request.GET.getlist("verbtype")
    verb_specified = bool(req_verb)

    verb = get_word(req_verb, req_verbtypes)

    req_tenses = request.GET.getlist("tense")
    req_negative = "ignore_negative" in request.GET
    tense, negative, person = get_modifiers(req_tenses, req_negative)

    answer = get_answer(verb.a_infinitive, tense, negative, person)

    index = str(verb.verbtype_i) + \
        {"preseens":"1", "imperfekti":"2", "perfekti":"3", "plusqvamperfekti":"4"}[tense] + \
        ("2" if negative else "1") + \
        {"minä":"1", "sinä":"2", "hän":"3", "me":"4", "te":"5", "he":"6"}[person]

    example = {"index": index, "infinitive": verb.a_infinitive, "glosses": verb.glosses, "person": person, "tense": tense, "negative": negative, "answer": answer}

    return HttpResponse(json.dumps(example))
