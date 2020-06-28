from datetime import datetime
from elasticsearch_dsl import Document, Date, Integer, Boolean, Keyword, Text, InnerDoc, Nested


class Resolution(InnerDoc):
    timestamp = Date()
    address = Keyword()


class Domain(Document):
    added = Date()
    domain = Keyword()
    tag = Keyword()
    notes = Text()
    ttr = Integer()
    enabled = Boolean()
    last_resolved = Date()
    resolutions = Nested(Resolution)

    class Index:
        name = "domain_resolutions"

    def add_resolution(self, address):
        self.resolutions.append(Resolution(address=address))
        self.last_resolved = datetime.utcnow()

    @property
    def latest_resolutions(self):
        pass
