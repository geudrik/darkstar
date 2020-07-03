from elasticsearch_dsl import Document, Date, Integer, Boolean, Keyword, Text, InnerDoc, Nested
from functools import wraps


def paginate_esdsl(f):
    """ Decorator that consumes various arguments to handle pagination through data in ES, utilizing ESDSL
    instances. Handles both filtering and pagination.

    When using, you need only return an ES-DSL Search() instance from your decorated function. This decorator
    will take care of the rest.
    """

    @wraps(f)
    def decorated_function(self, *args, **kwargs):

        as_tuple = kwargs.get('as_tuple', False)
        offset = kwargs.get('offset', 0)
        size = kwargs.get('size', 100)
        q = kwargs.get('q', None)
        sort = kwargs.get("sort", None)
        include = kwargs.get("include", None)
        exclude = kwargs.get("exclude", None)

        # Get sorting .. sorted
        if sort is None:
            sort_by = kwargs.get("order_by", None)
            sort_order = kwargs.get("order_dir", "asc")
            if sort_order == "desc":
                sort_order = "-"
            else:
                sort_order = ""
            if sort_by:
                sort = f"{sort_order}{sort_by}"

        # Call our decorated function - remember, we need to be reuturning an ESDSAL Search() instance
        base_query = f(self, *args, **kwargs)

        # Lets us figure out what data from the _source field we want to have returned
        if include and exclude:
            base_query = base_query.source(include=include, exclude=exclude)
        elif include:
            base_query = base_query.source(include=include)
        elif exclude:
            base_query = base_query.source(exclude=exclude)

        # Begin figuring out our unfiltered counts
        unfiltered = base_query[:1].execute()
        if "_source" in unfiltered.to_dict():
            unfiltered_count = 1
        else:
            unfiltered_count = unfiltered.hits.total['value']

        # Apply our query string if we have one
        if q:
            base_query = base_query.query('query_string', query=q)

        # Apply sorting of our filter
        if sort:
            if hasattr(self, "search_alts"):
                for k, v in self.search_alts.items():
                    if sort.strip("-") == k:
                        sort = sort.replace(k, v)
                        break
            base_query = base_query.sort(sort)

        # Handle our offset
        base_query = base_query[offset:offset + size]

        # Finally thgouh all the chickenshit, get our data
        result = base_query.execute()

        # sad_trombone.wav
        if not result or not result.hits:
            page = []
            filtered_count = 0

        # Just about done
        page = list(result.hits)
        filtered_count = result.hits.total['value']

        if as_tuple:
            return page, filtered_count, unfiltered_count
        return page

    return decorated_function


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

    def add_resolution(self, address, timestamp):
        self.resolutions.append(Resolution(address=address, timestamp=timestamp))

        # Ensure that the parent objects always has an up to date timestamp for when we last successfully resolved
        self.last_resolved = timestamp

    @property
    def latest_resolutions(self):
        pass

    @classmethod
    @paginate_esdsl
    def list(cls, enabled_opt='all', **kwargs):
        """ Lists all DSL results, leveraging the paginate_esdsl decorator that lets us paginate and filter
        """

        s = Domain.search()

        if enabled_opt in ('enabled', 'disabled'):
            enabled = True if enabled_opt == 'enabled' else False
            s = s.filter("term", enabled=enabled)

        return s

