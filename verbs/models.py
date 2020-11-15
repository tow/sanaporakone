from django.db import models

class Verb(models.Model):
    a_infinitive = models.CharField(max_length=50)
    glosses = models.JSONField()
    verbtype = models.CharField(max_length=25)
    verbtype_i = models.SmallIntegerField()

    def __str__(self):
        return 'Verb(a_infinitive="%s", verbtype="%s", verbtype_i=%i)' % (self.a_infinitive, self.verbtype, self.verbtype_i)
