import json
import random

from django.http import HttpResponse


from . import generator

def generate_example(request):
    persons = {"minä": "SG1", "sinä": "SG2", "hän": "SG3", "me":"PL1", "te": "PL2", "he": "PL3"}
    tenses = {"preseens": "PRESENT", "imperfekti": "PAST", "perfekti": "PERFECT", "plusqvamperfekti": "PLUSQUAMPERFECT"}
    negatives = (True, False)
    word, person, tense, negative = random.choice(generator.verbs), random.choice(list(persons)), random.choice(list(tenses)), random.choice(negatives)
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
