"""
@file      lib/utils/view_router.py
@author    David Neathery (dneathery@futurex.com)
@section LICENSE

This program is the property of Futurex, L.P.

No disclosure, reproduction, or use of any part thereof may be made without
express written permission of Futurex L.P.

Copyright by:  Futurex, LP. 2020

@section DESCRIPTION
Classes for routing to different views based on matching patterns in the request
"""

from itertools import zip_longest
from functools import partialmethod

from flask import request
from flask.views import MethodViewType
from werkzeug.datastructures import MultiDict

from utils.container_filters import dot_notation_get
from base_exceptions import UnroutableRequest


class Route:
    """
    Decorates a MethodView class so it calls the appropriate decorated method for the request
    """
    def __call__(self, cls):
        """
        Do the actual decoration to add "Lookup" view methods to the class
        """
        # Do not put decorator in Flask's 'decorators' list
        assert isinstance(cls, MethodViewType), f"{cls.__name__}: Decorate the ServerView class"

        # Find all attributes of the decorated class which have a '_route' attribute:
        handlers = {}
        for name in dir(cls):
            handler = getattr(cls, name)
            verb, patterns = getattr(handler, '_route', (None, None))
            if verb:  # merge lookup tables:
                table = handlers.setdefault(verb, [])
                handlers[verb] = [a|b for a, b in zip_longest(table, patterns, fillvalue=set())]

        # For each HTTP verb named in the _routes, create a new view function to do the lookups:
        for verb, table in handlers.items():
            lookup_view = LookupView(verb, table)
            curried_view = partialmethod(LookupView.view, lookup_view)
            setattr(cls, verb, curried_view)  # new view becomes ex: cls.post
        return cls

    @staticmethod
    def get(*params):
        """
        Decorates a view method to be called on GET with matching params
        """
        return ViewDecorator('get', *params)

    @staticmethod
    def delete(*params):
        """
        Decorates a view method to be called on DELETE with matching params
        """
        return ViewDecorator('delete', *params)

    @staticmethod
    def post(*body, action=None):
        """
        Decorates a view method to be called on given POST action with matching request body
        """
        if action is None:  # TODO(@dneathery): remove action code path once no views use action
            return ViewDecorator('post', *body)
        return ViewDecorator('post', {'action': action}, body=body)

    @staticmethod
    def put(*body, action=None):
        """
        Decorates a view method to be called on given PUT action with matching request body
        """
        if action is None:
            return ViewDecorator('put', *body)
        return ViewDecorator('put', {'action': action}, body=body)


class LookupView:
    """
    Class for a Flask view which checks the lookup tables to find a handling view

    Takes a table in the form of [{(view1, 'path.to.discriminator', )}]
    """
    def __init__(self, verb, tables):
        self.verb = verb
        self.tables = tables
        self.all_views = {pattern[0]:True for table in tables for pattern in table}

    def view(instance, self, *args, **kwargs):
        """
        The dispatching view called by Flask on a request, does a lookup to call the real view
        """
        request_data = self.get_data_from_request()
        handler = self.lookup(request_data)
        bound_handler = handler.__get__(instance, instance.__class__)
        frontend_response = bound_handler(*args, **kwargs)
        return frontend_response

    def lookup(self, request_data):
        """
        Does the lookup to find a view whose patterns match the fields of the request
        """
        matches = self.all_views

        for table in self.tables:  # iteratively eliminate non-matching views:
            new_matches = self.filter_with_table(matches, table, request_data)
            if not new_matches:
                raise MissingOptionsError(matches, table)
            matches = new_matches

        if len(matches) == 1:  # success if 1 matching view
            return matches.popitem()[0]
        specific_matches = [view for view, specific in matches.items() if specific]
        if len(specific_matches) == 1:  # success if 1 matching view when ignoring default
            return specific_matches[0]
        # else: there must be more than one specific match
        raise AmbiguousRequestError(specific_matches, self.tables, request_data)

    def get_data_from_request(self):
        """
        Get the request query params for GET/DELETE, or JSON in request body for PUT/POST
        """
        if self.verb in {'put', 'post'}:
            return request.get_json(force=True)
        if isinstance(request.args, MultiDict):  # sanitizer may have changed type to dict
            return request.args.to_dict(flat=True)
        return request.args

    @staticmethod
    def filter_with_table(views, table, request_data):
        """
        Return the subset of the views which match request_data using the table
        """
        matches = {}
        views_in_table = set()
        for view, path, value in table:
            if view not in views:
                continue
            views_in_table.add(view)
            if path == '*':
                matches.setdefault(view, False)
                continue
            request_value = dot_notation_get(request_data, path, default=Ellipsis)
            if request_value is Ellipsis:  # data could actually be None/null, use sentinel
                continue
            if request_value == value or value == '*':
                matches[view] = views[view]
                continue
        # add back any views which didn't have any patterns at all (they gave fewer args):
        matches.update({view:views[view] for view in views.keys() - views_in_table})
        return matches


class ViewDecorator:
    """
    Decorate a view method to tag it with its discriminators so it can be identified for routing

    Patterns are of the form {'path': 'value'}. Value is optional and defaults to '*'.
    Each argument expresses an OR relationship. Multiple arguments express an AND relationship.
    A default/fallback route can be indicated by giving a path of '*'.
    """
    def __init__(self, verb, *args, body=()):
        self.verb = verb
        request_data = []
        for arg in body:  # add body after args because we want to match the action first
            request_data.append({f'{"requestData."+k if k!="*" else k}':v for k, v in arg.items()})
        self.args = [*args, *request_data]

    def __call__(self, view):
        patterns = []
        for arg in self.args:
            if isinstance(arg, dict):
                arg_set = set()
                for path, value in arg.items():
                    # accept multiple values for one path:
                    if isinstance(value, (list, tuple)):
                        arg_set.update(set((view, path, option) for option in value))
                    else:
                        arg_set.add((view, path, value))
                patterns.append(arg_set)
            elif isinstance(arg, (list, tuple, set)):
                patterns.append(set((view, path, '*') for path in arg))
            elif isinstance(arg, str):  # implicit wildcard for value: matching only on hasattr
                patterns.append({(view, arg, '*')})
            else:
                raise NotImplementedError(type(arg))
        view._route = self.verb, patterns
        return view


class MissingOptionsError(UnroutableRequest):
    def __init__(self, prev_matches, table):
        options = [f"{path}{'='+value if value!='*' else ''}"
                   for handler, path, value in table if handler in prev_matches]
        err = f'Must specify at least one of: {", ".join(set(options))}'
        super().__init__(err)


class AmbiguousRequestError(UnroutableRequest):
    def __init__(self, matches, tables, request_data):
        for table in reversed(tables):
            overlap = [path for view, path, value in table if view in matches and path != '*'
                       and value in {dot_notation_get(request_data, path, ...), '*'}]
            if len(overlap) > 1:
                err = f"Cannot specify both '{overlap[0]}' and '{overlap[1]}'"
                break
        else: # this shouldn't happen unless the view patterns were duplicated
            err = 'Ambiguous request'
        super().__init__(err)
