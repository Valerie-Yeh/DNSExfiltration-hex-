#!/usr/bin/env python3

import json
import requests
from elasticsearch.connection import create_ssl_context
from elasticsearch import Elasticsearch


requests.packages.urllib3.disable_warnings()

class ElasticSearch:
    """Wrapper of Elasticsearch module.

    This module is designed for using elastic search more friendly.
    """

    def __init__(self, host, credential):
        self._set_condition_func()
        self._last = None

        self._es = Elasticsearch(
                hosts=[host],
                http_auth=credential,
                verify_certs=False,
                timeout=60)
        self._index = '*'
        self._query = {
            'query': {'bool': {'must': []}},
            'sort': {'@timestamp': {'order': 'asc'}}
        }

    def index(self, index):
        self._index = index
        self._last = None

    def query(self, query=None):
        if query:
            self._query.update(query)
            res = self._es.search(
                    index=self._index,
                    body=self._query)
        else:
            res = self._query

        self._last = None
        return res

    def time(self, start=None, end=None):
        self._query['query']['bool']['filter'] = {
            'range': {'@timestamp': {'gte': start, 'lt': end}}
        }

        # Clean history if `start` is set.
        if start:
            self._last = None

    def column(self, column):
        self._query['_source'] = {'includes': column}
        self._last = None

    def sort(self, column, order):
        self._query['sort'] = {column: {'order': order}}
        self._last = None

    def range(self, column, start=None, end=None):
        self._query['query']['bool']['must'].append({
            'bool': {
                'filter': [{'range': {column: {'gte': start, 'lt': end}}}]
            }
        })
        self._last = None

    def clear(self):
        self._query['query']['bool']['must'] = []
        self._last = None

    def _set_condition_func(self):
        """Generate functions dynamically for setting conditions.

        This function will generate 6 funcions, including:
            must(conditions):
                All of the conditions must be satisfied.
            must_reg(conditions)
                All of the conditions must be satisfied in regular
                    expression matching.
            must_not(conditions)
                All of the conditions must not be satisfied.
            must_not_reg(conditions)
                All of the conditions must not be satisfied in regular
                    expression matching.
            should(conditions)
                One of the conditions must be satisfied.
            should_reg(conditions)
                One of the conditions must be satisfied in regular
                    expression matching.

        All these funcions have one parameter in `list of dict` type.
        Each element in `list` is a `dict` which have only one
            key-value pair.
        """
        def generator(operation, method):
            func_name = operation + ('_reg' if method == 'regexp' else '')
            def func_code(conditions):
                clause = {
                    'bool': {operation: [{method: c} for c in conditions]}
                }
                if operation == 'should':
                    clause['bool']['minimum_should_match'] = 1
                self._query['query']['bool']['must'].append(clause)
            setattr(self, func_name, func_code)

        for operation in ['must', 'must_not', 'should']:
            for method in ['match_phrase', 'regexp']:
                generator(operation, method)

    def search(self, size=None, clear=False):
        data = []
        if size:
            self._last = None
        while True:
            if self._last:
                self._query['search_after'] = self._last

            res = self._es.search(
                    index=self._index,
                    size=10000,
                    body=self._query
            )
            if len(res['hits']['hits']) == 0:
                break
            data += res['hits']['hits']
            self._last = data[-1]['sort']

        data = data[::-1]
        self._query.pop('search_after', None)

        if clear:
            self.clear()
        
        return [datum['_source'] for datum in data][:size]



