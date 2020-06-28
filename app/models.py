from datetime import datetime
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, InnerDoc, Nested


class Resolution(InnerDoc):
    timestamp = Date()
    address = Keyword()


class Domain(Document):
    added = Date()
    domain = Keyword()
    tag = Keyword()
    notes = Text()
    ttr = Integer()
    last_resolved = Date()
    alias_of = Keyword()
    resolutions = Nested(Resolution)

    class Index:
        name = "domain_resolutions"

    def add_resolution(self, address):
        self.resolutions.append(Resolution(address=address))
        self.last_resolved = datetime.utcnow()
        self.save()
