from context import quit
import os
from os import path

from urllib.parse import quote_plus
from datetime import datetime
from pygit2 import GIT_SORT_TOPOLOGICAL, Signature, GIT_OBJ_BLOB
from quit.conf import Feature
import quit.application as quitApp
from quit.web.app import create_app
import unittest
from helpers import TemporaryRepository, TemporaryRepositoryFactory
import json
from helpers import createCommit, assertResultBindingsEqual
from tempfile import TemporaryDirectory
from quit.utils import iri_to_name


class SparqlProtocolTests(unittest.TestCase):
    """Test if requests are handled as specified in SPARQL 1.1. Protocol."""

    query = 'SELECT * WHERE {?s ?p ?o}'
    query_base = 'BASE <http://example.org/> SELECT * WHERE {?s ?p <O>}'
    update = 'INSERT {?s ?p ?o} WHERE {?s ?p ?o}'
    update_base = 'BASE <http://example.org/> INSERT {?s ?p ?o} WHERE {?s ?p ?o}'

    def setUp(self):
        return

    def tearDown(self):
        return

    def testQueryViaGet(self):
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z> .'
        repoContent = {'http://example.org/': content}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            payload = {'query': self.query}
            response = app.get('/sparql', query_string=payload)
            self.assertEqual(response.status_code, 200)

            payload = {'query': self.query, 'default-graph-uri': 'http://example.org/'}
            response = app.get('/sparql', query_string=payload)
            self.assertEqual(response.status_code, 200)

            payload = {'query': self.query, 'named-graph-uri': 'http://example.org/'}
            response = app.get('/sparql', query_string=payload)
            self.assertEqual(response.status_code, 400)

            payload = {'query': self.query,
                       'named-graph-uri': 'http://example.org/1/',
                       'default-graph-uri': 'http://example.org/2/'}
            response = app.get('/sparql', query_string=payload)
            self.assertEqual(response.status_code, 400)

            payload = {'query': self.query_base}
            response = app.get('/sparql', query_string=payload)
            self.assertEqual(response.status_code, 200)

            payload = {'query': self.update}
            response = app.get('/sparql', query_string=payload)
            self.assertEqual(response.status_code, 400)

    def testQueryViaUrlEncodedPost(self):
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z> .'
        repoContent = {'http://example.org/': content}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

            payload = {'query': self.query}
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 200)

            payload = {'query': self.query, 'default-graph-uri': 'http://example.org/'}
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 200)

            payload = {'query': self.query, 'named-graph-uri': 'http://example.org/'}
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 400)

            payload = {'query': self.query,
                       'named-graph-uri': 'http://example.org/1/',
                       'default-graph-uri': 'http://example.org/2/'}
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 400)

            payload = {'query': self.query_base}
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 200)

            payload = {'query': self.update}
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 400)

    def testQueryViaPostDirectly(self):
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z> .'
        repoContent = {'http://example.org/': content}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            headers = {'Content-Type': 'application/sparql-query'}

            payload = {}
            response = app.post('/sparql', query_string=payload, data=self.query, headers=headers)
            self.assertEqual(response.status_code, 200)

            payload = {'default-graph-uri': 'http://example.org/'}
            response = app.post('/sparql', query_string=payload, data=self.query, headers=headers)
            self.assertEqual(response.status_code, 200)

            payload = {'named-graph-uri': 'http://example.org/'}
            response = app.post('/sparql', query_string=payload, data=self.query, headers=headers)
            self.assertEqual(response.status_code, 400)

            payload = {'default-graph-uri': 'http://example.org/1/',
                       'named-graph-uri': 'http://example.org/2/'}
            response = app.post('/sparql', query_string=payload, data=self.query, headers=headers)
            self.assertEqual(response.status_code, 400)

            payload = {'default-graph-uri': 'http://example.org/1/',
                       'named-graph-uri': 'http://example.org/2/'}
            response = app.post('/sparql', query_string=payload, data=self.query_base, headers=headers)
            self.assertEqual(response.status_code, 400)

            response = app.post('/sparql', data=self.update, headers=headers)
            self.assertEqual(response.status_code, 400)

    def testUpdateViaUrlEncodedPost(self):
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z> .'
        repoContent = {'http://example.org/': content}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

            payload = {'update': self.update}
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 200)

            payload = {'update': self.update, 'using-graph-uri': 'http://example.org/'}
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 200)

            payload = {'update': self.update, 'using-named-graph-uri': 'http://example.org/'}
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 400)

            payload = {'update': self.update,
                       'using-named-graph-uri': 'http://example.org/1/',
                       'using-graph-uri': 'http://example.org/2/'}
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 400)

            payload = {'update': self.update_base}
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 200)

            payload = {'query': self.update}
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 400)

    def testUpdateViaPostDirectly(self):
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z> .'
        repoContent = {'http://example.org/': content}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            headers = {'Content-Type': 'application/sparql-update'}

            payload = {}
            response = app.post('/sparql', query_string=payload, data=self.update, headers=headers)
            self.assertEqual(response.status_code, 200)

            payload = {'using-graph-uri': 'http://example.org/'}
            response = app.post('/sparql', query_string=payload, data=self.update, headers=headers)
            self.assertEqual(response.status_code, 200)

            payload = {'using-named-graph-uri': 'http://example.org/'}
            response = app.post('/sparql', query_string=payload, data=self.update, headers=headers)
            self.assertEqual(response.status_code, 400)

            payload = {'using-graph-uri': 'http://example.org/1/',
                       'using-named-graph-uri': 'http://example.org/2/'}
            response = app.post('/sparql', query_string=payload, data=self.update, headers=headers)
            self.assertEqual(response.status_code, 400)

            payload = {'named-graph-uri': 'http://example.org/1/',
                       'using-named-graph-uri': 'http://example.org/2/'}
            response = app.post('/sparql', query_string=payload, data=self.update_base, headers=headers)
            self.assertEqual(response.status_code, 400)

            payload = {'default-graph-uri': 'http://example.org/1/',
                       'named-graph-uri': 'http://example.org/2/'}
            response = app.post('/sparql', query_string=payload, data=self.query, headers=headers)
            self.assertEqual(response.status_code, 400)

    def testUpdateUsingGraphUri(self):
        select = "SELECT * WHERE {graph <urn:graph> {?s ?p ?o .}} ORDER BY ?s ?p ?o"

        # Prepate a git Repository
        content1 = '<urn:x> <urn:y> <urn:z> .'
        content2 = '<urn:1> <urn:2> <urn:3> .'
        repoContent = {'http://example.org/1/': content1,
                       'http://example.org/2/': content2,
                       'urn:graph': ''}

        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before UPDATE
            select_resp = app.post(
                '/sparql',
                data=dict(query=select),
                headers=dict(accept="application/sparql-results+json")
            )

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 0)

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            payload = {'update': 'INSERT {GRAPH <urn:graph> {?s ?p ?o}} WHERE {?s ?p ?o}', 'using-graph-uri': 'http://example.org/1/'}

            # execute UPDATE
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 200)

            # execute SELECT query after UPDATE
            select_resp = app.post(
                '/sparql',
                data=dict(query=select),
                headers=dict(accept="application/sparql-results+json")
            )

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

    @unittest.skip("Skipped until rdflib properly handles FROM NAMED and USING NAMED")
    def testUpdateUsingNamedGraphUri(self):
        select = "SELECT * WHERE {graph <http://example.org/test/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"

        # Prepate a git Repository
        content1 = '<urn:x> <urn:y> <urn:z> .'
        content2 = '<urn:1> <urn:2> <urn:3> .'
        repoContent = {'http://example.org/graph1/': content1, 'http://example.org/graph2/': content2, 'http://example.org/test/': ''}

        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before UPDATE
            select_resp = app.post(
                '/sparql',
                data=dict(query=select),
                headers=dict(accept="application/sparql-results+json")
            )

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 0)

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            payload = {'update': 'INSERT {GRAPH <http://example.org/test/> {?s ?p ?o}} WHERE {graph ?g {?s ?p ?o}}',
                       'using-named-graph-uri': 'http://example.org/graph1/'}

            # execute UPDATE
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 400)

            # execute SELECT query after UPDATE
            select_resp = app.post(
                '/sparql',
                data=dict(query=select),
                headers=dict(accept="application/sparql-results+json")
            )

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            self.assertDictEqual(obj["results"]["bindings"][1], {
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

    def testMultioperationalUpdate(self):
        """Execute a multioperational Update query and test store and file content."""
        select = "SELECT * WHERE {graph <urn:graph> {?s ?p ?o .}} ORDER BY ?s ?p ?o"

        update = 'DELETE DATA { GRAPH <urn:graph> { <urn:I> <urn:II> <urn:III> }} ; '
        update += 'INSERT DATA { GRAPH <urn:graph> { <urn:a> <urn:b> <urn:c> }}'

        # Prepate a git Repository
        repoContent = {'urn:graph': '<urn:I> <urn:II> <urn:III> .'}

        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before UPDATE
            select_resp = app.post(
                '/sparql',
                data=dict(query=select),
                headers=dict(accept="application/sparql-results+json")
            )

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            payload = {'update': update}

            # execute UPDATE
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 200)

            # execute SELECT query after UPDATE
            select_resp = app.post(
                '/sparql',
                data=dict(query=select),
                headers=dict(accept="application/sparql-results+json")
            )

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'urn:a'},
                "p": {'type': 'uri', 'value': 'urn:b'},
                "o": {'type': 'uri', 'value': 'urn:c'}})
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('<urn:a> <urn:b> <urn:c> .\n', f.read())

    def testAbortedMultioperationalUpdate(self):
        """Execute two multioperational Update queries and test store and file content.

        The first query sequence contains an error in the second query.

        """
        select = "SELECT * WHERE {graph <urn:graph> {?s ?p ?o .}} ORDER BY ?s ?p ?o"

        update = 'INSERT DATA { GRAPH <urn:graph> { <urn:I> <urn:II> <urn:III> }}; '
        update += 'INSERT {GRAPH <urn:graph> {?s ?p ?o}} USING NAMED <http://http://example.org/1/> '
        update += 'WHERE {graph ?g {?s ?p ?o .}};'

        update2 = 'DELETE DATA { GRAPH <urn:graph> { <urn:I> <urn:II> <urn:III> }}; '
        update2 += 'INSERT DATA { GRAPH <urn:graph> { <urn:a> <urn:b> <urn:c> }}'

        # Prepate a git Repository
        content1 = '<urn:x> <urn:y> <urn:z> .'
        content2 = '<urn:1> <urn:2> <urn:3> .'
        repoContent = {'http://example.org/1/': content1,
                       'http://example.org/2/': content2,
                       'urn:graph': ''}

        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before UPDATE
            select_resp = app.post(
                '/sparql',
                data=dict(query=select),
                headers=dict(accept="application/sparql-results+json")
            )

            obj = json.loads(select_resp.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 0)

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            payload = {'update': update}

            # execute UPDATE
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 400)

            # execute SELECT query after UPDATE
            select_resp = app.post(
                '/sparql',
                data=dict(query=select),
                headers=dict(accept="application/sparql-results+json")
            )

            obj = json.loads(select_resp.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 1)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'urn:I'},
                "p": {'type': 'uri', 'value': 'urn:II'},
                "o": {'type': 'uri', 'value': 'urn:III'}})

            with open(path.join(repo.workdir, 'graph_2.nt'), 'r') as f:
                self.assertEqual('<urn:I> <urn:II> <urn:III> .\n', f.read())

            payload = {'update': update2}

            # execute UPDATE2
            response = app.post('/sparql', data=payload, headers=headers)
            self.assertEqual(response.status_code, 200)

            # execute SELECT query after UPDATE2
            select_resp = app.post(
                '/sparql',
                data=dict(query=select),
                headers=dict(accept="application/sparql-results+json")
            )

            obj = json.loads(select_resp.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 1)
            with open(path.join(repo.workdir, 'graph_2.nt'), 'r') as f:
                self.assertEqual('<urn:a> <urn:b> <urn:c> .\n', f.read())
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'urn:a'},
                "p": {'type': 'uri', 'value': 'urn:b'},
                "o": {'type': 'uri', 'value': 'urn:c'}})

    def testSelectFrom(self):
        select = "SELECT ?s ?p ?o FROM <http://example.org/graph1/> "
        select += "WHERE {?s ?p ?o . } ORDER BY ?s ?p ?o"

        # Prepate a git Repository
        content1 = '<urn:x> <urn:y> <urn:z> .'
        content2 = '<urn:1> <urn:2> <urn:3> .'
        repoContent = {'http://example.org/graph1/': content1, 'http://example.org/graph2/': content2}

        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            resp = app.post(
                '/sparql',
                data=dict(query=select),
                headers=dict(accept="application/sparql-results+json")
            )

            obj = json.loads(resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

    @unittest.skip("Skipped until rdflib properly handles FROM NAMED and USING NAMED")
    def testSelectFromNamed(self):
        select = "SELECT ?s ?p ?o FROM NAMED <http://example.org/graph1/> "
        select += "WHERE {GRAPH ?g {?s ?p ?o . }} ORDER BY ?s ?p ?o"

        # Prepate a git Repository
        content1 = '<urn:x> <urn:y> <urn:z> .'
        content2 = '<urn:1> <urn:2> <urn:3> .'
        repoContent = {'http://example.org/graph1/': content1, 'http://example.org/graph2/': content2}

        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            resp = app.post(
                '/sparql',
                data=dict(query=select),
                headers=dict(accept="application/sparql-results+json")
            )

            obj = json.loads(resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

    def testQueryProvenanceViaGet(self):
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z> .'
        repoContent = {'http://example.org/': content}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            args['features'] = Feature.Provenance
            app = create_app(args).test_client()

            payload = {'query': self.query}
            response = app.get('/provenance', query_string=payload)
            self.assertEqual(response.status_code, 200)

            payload = {'query': self.query, 'default-graph-uri': 'http://example.org/'}
            response = app.get('/provenance', query_string=payload)
            self.assertEqual(response.status_code, 200)

            payload = {'query': self.query, 'named-graph-uri': 'http://example.org/'}
            response = app.get('/provenance', query_string=payload)
            self.assertEqual(response.status_code, 400)

            payload = {'query': self.query,
                       'named-graph-uri': 'http://example.org/1/',
                       'default-graph-uri': 'http://example.org/2/'}
            response = app.get('/provenance', query_string=payload)
            self.assertEqual(response.status_code, 400)

            payload = {'query': self.query_base}
            response = app.get('/provenance', query_string=payload)
            self.assertEqual(response.status_code, 200)

            payload = {'query': self.update}
            response = app.get('/provenance', query_string=payload)
            self.assertEqual(response.status_code, 400)

    def testQueryProvenanceViaUrlEncodedPost(self):
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z> .'
        repoContent = {'http://example.org/': content}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            args['features'] = Feature.Provenance
            app = create_app(args).test_client()

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

            payload = {'query': self.query}
            response = app.post('/provenance', data=payload, headers=headers)
            self.assertEqual(response.status_code, 200)

            payload = {'query': self.query, 'default-graph-uri': 'http://example.org/'}
            response = app.post('/provenance', data=payload, headers=headers)
            self.assertEqual(response.status_code, 200)

            payload = {'query': self.query, 'named-graph-uri': 'http://example.org/'}
            response = app.post('/provenance', data=payload, headers=headers)
            self.assertEqual(response.status_code, 400)

            payload = {'query': self.query,
                       'named-graph-uri': 'http://example.org/1/',
                       'default-graph-uri': 'http://example.org/2/'}
            response = app.post('/provenance', data=payload, headers=headers)
            self.assertEqual(response.status_code, 400)

            payload = {'query': self.query_base}
            response = app.post('/provenance', data=payload, headers=headers)
            self.assertEqual(response.status_code, 200)

            payload = {'query': self.update}
            response = app.post('/provenance', data=payload, headers=headers)
            self.assertEqual(response.status_code, 400)

    def testQueryProvenanceViaPostDirectly(self):
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z> .'
        repoContent = {'http://example.org/': content}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            args['features'] = Feature.Provenance
            app = create_app(args).test_client()

            headers = {'Content-Type': 'application/sparql-query'}

            payload = {}
            response = app.post('/provenance', query_string=payload, data=self.query, headers=headers)
            self.assertEqual(response.status_code, 200)

            payload = {'default-graph-uri': 'http://example.org/'}
            response = app.post('/provenance', query_string=payload, data=self.query, headers=headers)
            self.assertEqual(response.status_code, 200)

            payload = {'named-graph-uri': 'http://example.org/'}
            response = app.post('/provenance', query_string=payload, data=self.query, headers=headers)
            self.assertEqual(response.status_code, 400)

            payload = {'default-graph-uri': 'http://example.org/1/',
                       'named-graph-uri': 'http://example.org/2/'}
            response = app.post('/provenance', query_string=payload, data=self.query, headers=headers)
            self.assertEqual(response.status_code, 400)

            payload = {'default-graph-uri': 'http://example.org/1/',
                       'named-graph-uri': 'http://example.org/2/'}
            response = app.post('/provenance', query_string=payload, data=self.query_base, headers=headers)
            self.assertEqual(response.status_code, 400)

            response = app.post('/provenance', data=self.update, headers=headers)
            self.assertEqual(response.status_code, 400)


class QuitAppTestCase(unittest.TestCase):
    """Test API and synchronization of Store and Git."""

    author = Signature('QuitStoreTest', 'quit@quit.aksw.org')
    comitter = Signature('QuitStoreTest', 'quit@quit.aksw.org')

    def setUp(self):
        return

    def tearDown(self):
        return

    def testBaseNamespaceArgument(self):
        """Test if the base namespace is working when changed with by argument.

        1. Prepare a git repository with an empty graph
        2. Start Quit
        3. execute INSERT DATA query
        4. execute SELECT query
        """
        # Prepate a git Repository
        with TemporaryRepositoryFactory().withEmptyGraph("http://example.org/") as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            args['namespace'] = 'http://example.org/newNS/'
            app = create_app(args).test_client()

            # execute INSERT DATA query
            update = "INSERT DATA {graph <http://example.org/> {<relativeURI> <http://ex.org/b> <http://ex.org/c> .}}"
            app.post('/sparql', data=dict(update=update))

            # execute SELECT query
            select = "SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"
            select_resp = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'http://example.org/newNS/relativeURI'},
                "p": {'type': 'uri', 'value': 'http://ex.org/b'},
                "o": {'type': 'uri', 'value': 'http://ex.org/c'}})

    def testBaseNamespaceDefault(self):
        """Test if the base namespace is working.

        1. Prepare a git repository with an empty graph
        2. Start Quit
        3. execute INSERT DATA query
        4. execute SELECT query
        """
        # Prepate a git Repository
        with TemporaryRepositoryFactory().withEmptyGraph("http://example.org/") as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute INSERT DATA query
            update = "INSERT DATA {graph <http://example.org/> {<relativeURI> <http://ex.org/b> <http://ex.org/c> .}}"
            app.post('/sparql', data=dict(update=update))

            # execute SELECT query
            select = "SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"
            select_resp = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'http://quit.instance/relativeURI'},
                "p": {'type': 'uri', 'value': 'http://ex.org/b'},
                "o": {'type': 'uri', 'value': 'http://ex.org/c'}})

    def testBaseNamespaceOverwriteInQuery(self):
        """Test if the base namespace is working.

        1. Prepare a git repository with an empty graph
        2. Start Quit
        3. execute INSERT DATA query
        4. execute SELECT query
        """
        # Prepate a git Repository
        with TemporaryRepositoryFactory().withEmptyGraph("http://example.org/") as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute INSERT DATA query
            update = "BASE <http://example.org/newNS/>\nINSERT DATA {graph <http://example.org/> "
            update += "{<relativeURI> <http://ex.org/b> <http://ex.org/c> .}}"
            app.post('/sparql', data=dict(update=update))

            # execute SELECT query
            select = "SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"
            select_resp = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'http://example.org/newNS/relativeURI'},
                "p": {'type': 'uri', 'value': 'http://ex.org/b'},
                "o": {'type': 'uri', 'value': 'http://ex.org/c'}})

    def testBlame(self):
        """Test if feature responds with correct values.

        1. Prepare a git repository with a non empty graph
        2. Get id of the existing commit
        3. Call /blame/master resp. /blame/main and /blame/{commitId} with all specified accept headers and test the
           response data
        """
        # Prepate a git Repository
        graphContent = '<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .'
        with TemporaryRepositoryFactory().withGraph("http://example.org/", graphContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            args['features'] = Feature.Provenance
            app = create_app(args).test_client()

            for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL):
                oid = str(commit.id)

            current_head = repo.head.shorthand

            expected = {
                's': {'type': 'uri', 'value': 'http://ex.org/x'},
                'p': {'type': 'uri', 'value': 'http://ex.org/y'},
                'o': {'type': 'uri', 'value': 'http://ex.org/z'},
                'context': {'type': 'uri', 'value': 'http://example.org/'},
                'hex': {'type': 'literal', 'value': oid},
                'name': {'type': 'literal', 'value': 'QuitStoreTest'},
                'email': {'type': 'literal', 'value': 'quit@quit.aksw.org'}
            }

            for apiPath in [current_head, 'HEAD', oid]:
                response = app.get('/blame/{}'.format(apiPath))
                resultBindings = json.loads(response.data.decode("utf-8"))['results']['bindings']
                results = resultBindings[0]

                self.assertEqual(len(resultBindings), 1)
                # compare expected date separately without time
                self.assertTrue(
                    results['date']['value'].startswith(datetime.now().strftime('%Y-%m-%d'))
                )
                self.assertEqual(
                    results['date']['datatype'], 'http://www.w3.org/2001/XMLSchema#dateTime'
                )
                self.assertIn(results['date']['type'], ['typed-literal', 'literal'])

                del results['date']

                queryVariables = ['s', 'p', 'o', 'context', 'hex', 'name', 'email']

                # compare lists (without date)
                assertResultBindingsEqual(self, [expected], resultBindings, queryVariables)

    def testBlameApi(self):
        """Test if feature is active or not.

        1. Prepare a git repository with a non empty graph
        2. Get id of the existing commit
        3. Call /blame/master resp /blame/main and /blame/{commitId} with all specified accept headers and test the
           response status
        """
        # Prepate a git Repository
        graphContent = '<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .'
        with TemporaryRepositoryFactory().withGraph("http://example.org/", graphContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            args['features'] = Feature.Provenance
            app = create_app(args).test_client()

            self.assertFalse(repo.head_is_detached)

            current_head = repo.head.shorthand

            for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL):
                oid = str(commit.id)

            graphUri = 'http://example.org/'

            mimetypes = [
                'text/html', 'application/xhtml_xml', '*/*',
                'application/json', 'application/sparql-results+json',
                'application/rdf+xml', 'application/xml', 'application/sparql-results+xml',
                'application/csv', 'text/csv'
            ]

            # Test API with existing paths and specified accept headers
            for apiPath in [current_head, 'HEAD', oid]:
                for header in mimetypes:
                    response = app.get('/blame/{}'.format(apiPath), headers={'Accept': header})
                    self.assertEqual(response.status, '200 OK')

            # Test API default accept header
            response = app.get('/blame/' + current_head)
            self.assertEqual(response.status, '200 OK')

            # Test API default accept header
            response = app.get('/blame/HEAD')
            self.assertEqual(response.status, '200 OK')

            # Test API with not acceptable header
            response = app.get('/blame/foobar', headers={'Accept': 'foo/bar'})
            self.assertEqual(response.status, '400 BAD REQUEST')

            # Test API with non existing path
            response = app.get('/blame/foobar')
            self.assertEqual(response.status, '400 BAD REQUEST')

    def testBranchAndDeleteBranch(self):
        """Test branching and deleting the branch."""

        # Prepate a git Repository
        content = "<http://ex.org/a> <http://ex.org/b> <http://ex.org/c> ."
        with TemporaryRepositoryFactory().withGraph("http://example.org/", content) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args["targetdir"] = repo.workdir
            app = create_app(args).test_client()

            current_head = repo.head.shorthand


            self.assertEqual(len(repo.raw_listall_branches()), 1)

            app.post("/branch", data={"oldbranch": current_head, "newbranch": "develop"})

            self.assertEqual(len(repo.raw_listall_branches()), 2)

            # execute INSERT DATA query
            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .}}"
            res = app.post("/sparql", data={"update": update})
            self.assertEqual(res.status, '200 OK')

            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/z> <http://ex.org/z> <http://ex.org/z> .}}"
            res = app.post("/sparql/develop", data={"update": update})
            self.assertEqual(res.status, '200 OK')

            # Currently we need to checkout master resp. main again, because the commit always checks out the latest updated branch
            # If develop is checked out, it is the current HEAD and thus can not be deleted
            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/x> <http://ex.org/a> <http://ex.org/b> .}}"
            res = app.post("/sparql/" + current_head, data={"update": update})
            self.assertEqual(res.status, '200 OK')

            query = "ASK {graph <http://example.org/> {<http://ex.org/z> <http://ex.org/z> <http://ex.org/z> .}}"
            res = app.post("/sparql/develop", data={"query": query})
            self.assertEqual(res.status, '200 OK')

            query = "ASK {graph <http://example.org/> {<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .}}"
            res = app.post("/sparql/" + current_head, data={"query": query})
            self.assertEqual(res.status, '200 OK')

            self.assertEqual(len(repo.raw_listall_branches()), 2)

            res = app.post("/delete/branch/develop")
            self.assertEqual(res.status, '200 OK')

            self.assertEqual(len(repo.raw_listall_branches()), 1)

            query = "ASK {graph <http://example.org/> {<http://ex.org/z> <http://ex.org/z> <http://ex.org/z> .}}"
            res = app.post("/sparql/develop", data={"query": query}, headers={"Accept": "application/json"})
            self.assertEqual(res.status, '400 BAD REQUEST')

    def testBranchWithRefspec(self):
        """Test branching."""

        # Prepate a git Repository
        content = "<http://ex.org/a> <http://ex.org/b> <http://ex.org/c> ."
        with TemporaryRepositoryFactory().withGraph("http://example.org/", content) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()
            current_head = repo.head.shorthand

            self.assertEqual(len(repo.raw_listall_branches()), 1)

            app.post("/branch/" + current_head + ":develop")

            self.assertEqual(len(repo.raw_listall_branches()), 2)

            # execute INSERT DATA query
            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .}}"
            res = app.post('/sparql', data={"update": update})
            self.assertEqual(res.status, '200 OK')

            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/z> <http://ex.org/z> <http://ex.org/z> .}}"
            res = app.post('/sparql/develop', data={"update": update})
            self.assertEqual(res.status, '200 OK')

            query = "ASK {graph <http://example.org/> {<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .}}"
            res = app.post("/sparql", data={"query": query})
            self.assertEqual(res.status, '200 OK')

            query = "ASK {graph <http://example.org/> {<http://ex.org/z> <http://ex.org/z> <http://ex.org/z> .}}"
            res = app.post("/sparql/develop", data={"query": query})
            self.assertEqual(res.status, '200 OK')

    def testCommits(self):
        """Test /commits API request."""
        with TemporaryRepository() as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            response = app.get('/commits', headers={'Accept': 'application/json'})
            self.assertEqual(response.status, '200 OK')
            responseData = json.loads(response.data.decode("utf-8"))
            self.assertListEqual(responseData, [])

            response = app.get('/commits')
            self.assertEqual(response.status, '200 OK')

            response = app.get('/commits', headers={'Accept': 'text/html'})
            self.assertEqual(response.status, '200 OK')

            response = app.get('/commits', headers={'Accept': 'test/nothing'})
            self.assertEqual(response.status, '406 NOT ACCEPTABLE')

            # Create graph with content and commit
            graphContent = "<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> <http://example.org/> ."
            with open(path.join(repo.workdir, "graph.nt"), "w") as graphFile:
                graphFile.write(graphContent)

            with open(path.join(repo.workdir, "graph.nt.graph"), "w") as graphFile:
                graphFile.write('http://example.org')

            createCommit(repository=repo)

            # go on with tests
            response = app.get('/commits', headers={'Accept': 'application/json'})
            self.assertEqual(response.status, '200 OK')
            responseData = json.loads(response.data.decode("utf-8"))
            self.assertEqual(len(responseData), 1)

            response = app.get('/commits', headers={'Accept': 'text/html'})
            self.assertEqual(response.status, '200 OK')

    def testContentNegotiation(self):
        """Test SPARQL with different Accept Headers."""
        # Prepate a git Repository
        with TemporaryRepositoryFactory().withEmptyGraph("urn:graph") as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            args['features'] = Feature.Provenance
            app = create_app(args).test_client()

            query = 'SELECT * WHERE {graph ?g {?s ?p ?o .}} LIMIT 1'
            ask = 'ASK {graph <urn:graph> {<urn:bla> <urn:blub> <urn:foo> .}} LIMIT 1'
            construct = 'CONSTRUCT {?s ?p ?o} WHERE {graph ?g {?s ?p ?o .}} LIMIT 1'

            test_values = {
                'sparql': [query, {
                        '*/*': 'application/sparql-results+xml',
                        'application/sparql-results+xml': 'application/sparql-results+xml',
                        'application/xml': 'application/xml',
                        'application/json': 'application/json',
                        'application/sparql-results+json': 'application/sparql-results+json',
                        'text/csv': 'text/csv',
                        'text/html': 'text/html',
                        'application/xhtml+xml': 'application/xhtml+xml',
                        'foo/bar,application/sparql-results+xml;q=0.5': 'application/sparql-results+xml'}],
                'ask': [ask, {
                        '*/*': 'application/sparql-results+xml',
                        'application/sparql-results+xml': 'application/sparql-results+xml',
                        'application/xml': 'application/xml',
                        'application/json': 'application/json',
                        'application/sparql-results+json': 'application/sparql-results+json',
                        'text/html': 'text/html',
                        'application/xhtml+xml': 'application/xhtml+xml',
                        'foo/bar,application/sparql-results+xml;q=0.5': 'application/sparql-results+xml'}],
                'construct': [construct, {
                        '*/*': 'text/turtle',
                        'text/turtle': 'text/turtle',
                        'application/x-turtle': 'application/x-turtle',
                        'application/rdf+xml': 'application/rdf+xml',
                        'application/xml': 'application/xml',
                        'application/n-triples': 'application/n-triples',
                        'application/trig': 'application/trig',
                        'application/json': 'application/json',
                        'application/ld+json': 'application/ld+json',
                        'foo/bar,text/turtle;q=0.5': 'text/turtle'}]}

            for ep_path in ['/sparql', '/provenance']:
                for query_type, values in test_values.items():
                    query_string = values[0]

                    # test supported
                    for accept_type, content_type in values[1].items():
                        response = app.post(
                            ep_path,
                            data=dict(query=query_string),
                            headers={'Accept': accept_type}
                        )
                        self.assertEqual('200 OK', response.status)
                        self.assertEqual(content_type, response.headers['Content-Type'])

                    # test default
                    resp = app.post(ep_path, data=dict(query=query_string))
                    self.assertEqual('200 OK', resp.status)
                    self.assertEqual(values[1]['*/*'], resp.headers['Content-Type'])

                    # test unsupported
                    resp = app.post(ep_path, data=dict(query=query_string), headers={'Accept': 'foo/bar'})
                    self.assertEqual('406 NOT ACCEPTABLE', resp.status)

    def testCreateAppArgs(self):
        """Test create_app with command line arguments"""
        with TemporaryRepository() as repo:
            # Start Quit
            defaults = quitApp.getDefaults()
            cliArgs = quitApp.parseArgs(['-t', repo.workdir, '-f', 'provenance', 'garbagecollection'])
            app = create_app({**defaults, **cliArgs})
            self.assertTrue(app.config['quit'].config.hasFeature(Feature.Provenance))
            self.assertFalse(app.config['quit'].config.hasFeature(Feature.Persistence))
            self.assertTrue(app.config['quit'].config.hasFeature(Feature.GarbageCollection))

    def testCreateAppArgsOnlyProv(self):
        """Test create_app with command line arguments"""
        with TemporaryRepository() as repo:
            # Start Quit
            defaults = quitApp.getDefaults()
            cliArgs = quitApp.parseArgs(['-t', repo.workdir, '-f', 'provenance', '-v'])
            app = create_app({**defaults, **cliArgs})
            self.assertTrue(app.config['quit'].config.hasFeature(Feature.Provenance))
            self.assertFalse(app.config['quit'].config.hasFeature(Feature.Persistence))
            self.assertFalse(app.config['quit'].config.hasFeature(Feature.GarbageCollection))

    def testCreateAppEnv(self):
        """Test create_app with environemnt variables"""
        with TemporaryRepository() as repo:
            os.environ['QUIT_TARGETDIR'] = repo.workdir
            with TemporaryDirectory() as logs:
                listOfFile = os.listdir(logs)
                self.assertEqual(0, len(listOfFile))
                logfile = os.path.join(logs, 'quit.log')
                os.environ['QUIT_LOGFILE'] = logfile
                # Start Quit
                defaults = quitApp.getDefaults()
                env = quitApp.parseEnv()
                app = create_app({**defaults, **env})
                self.assertFalse(app.config['quit'].config.hasFeature(Feature.Provenance))
                self.assertFalse(app.config['quit'].config.hasFeature(Feature.Persistence))
                self.assertFalse(app.config['quit'].config.hasFeature(Feature.GarbageCollection))
                listOfFile = os.listdir(logs)
                self.assertEqual(1, len(listOfFile))
                with open(logfile) as logfilepointer:
                    num_lines = sum(1 for line in logfilepointer)
                    self.assertTrue(num_lines > 1)

    def testCreateAppFail(self):
        """Test create_app without targert directory, which should fail"""
        with TemporaryRepository() as repo:
            # Start Quit
            defaults = quitApp.getDefaults()
            with self.assertRaises(SystemExit):
                create_app(defaults)

    def testDeleteInsertWhere(self):
        """Test DELETE INSERT WHERE with an empty and a non empty graph.

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute SELECT query
        4. execute DELETE INSERT WHERE query
        5. execute SELECT query
        """
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z> .'
        repoContent = {'http://example.org/': content, 'http://aksw.org/': ''}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before DELETE INSERT WHERE
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute DELETE INSERT WHERE query
            update = 'DELETE {GRAPH <http://example.org/> {?a <urn:y> <urn:z> .}} INSERT {GRAPH <http://aksw.org/> {?a <urn:1> "new" .}} WHERE {GRAPH <http://example.org/> {?a <urn:y> <urn:z> .}}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after DELETE INSERT WHERE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(1, len(obj["results"]["bindings"]))
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(1, len(obj["results"]["bindings"]))
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:1'},
                "o": {'type': 'literal', 'value': 'new'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:1> "new" .\n', f.read())
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual('\n', f.read())

    def testDeleteInsertWhereProvenance(self):
        """Test DELETE INSERT WHERE with an empty and a non empty graph with provenance feature.

        This test must behave like testDeleteInsertWhere plus writing the correct Provenance
        informations to the provenance store.

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute SELECT queries (/sparql, /provenance)
        4. execute DELETE INSERT WHERE query
        5. execute SELECT queries (/sparql, /provenance)
        6. test results
        """
        # Create queries
        prov = 'SELECT DISTINCT ?op ?s ?p ?o '
        prov += 'WHERE {?activity <http://quit.aksw.org/vocab/updates> ?update ; '
        prov += '<http://www.w3.org/ns/prov#endedAtTime> ?time . '
        prov += '?update ?op ?g . GRAPH ?g {?s ?p ?o .} FILTER ( '
        prov += 'sameTerm(?op, <http://quit.aksw.org/vocab/additions>) '
        prov += '|| sameTerm(?op, <http://quit.aksw.org/vocab/removals>) ) } '
        prov += 'ORDER BY ?time ?update ?g ?s ?p ?o'

        select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"

        update = 'DELETE {GRAPH <http://example.org/> {?a <urn:y> <urn:z> .}} '
        update += 'INSERT {GRAPH <http://aksw.org/> {?a <urn:1> "new" .}} '
        update += 'WHERE {GRAPH <http://example.org/> {?a <urn:y> <urn:z> .}}'

        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z>  .'
        repoContent = {'http://example.org/': content, 'http://aksw.org/': ''}

        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            args['features'] = Feature.Provenance
            app = create_app(args).test_client()

            # execute SELECT query before DELETE INSERT WHERE
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute PROVENANCE query before DELETE INSERT WHERE
            prov_before = app.post('/provenance', data=dict(query=prov), headers=dict(accept="application/sparql-results+json"))

            # execute DELETE INSERT WHERE query
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after DELETE INSERT WHERE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute PROVENANCE query after DELETE INSERT WHERE
            prov_after = app.post('/provenance', data=dict(query=prov), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 1)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test prov before
            changesets = json.loads(prov_before.data.decode("utf-8"))
            self.assertEqual(len(changesets["results"]["bindings"]), 1)
            self.assertDictEqual(changesets["results"]["bindings"][0], {
                "op": {'type': 'uri', 'value': 'http://quit.aksw.org/vocab/additions'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 1)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:1'},
                "o": {'type': 'literal', 'value': 'new'}})

            # test prov after
            changesets = json.loads(prov_after.data.decode("utf-8"))
            self.assertEqual(len(changesets["results"]["bindings"]), 3)
            self.assertDictEqual(changesets["results"]["bindings"][0], {
                "op": {'type': 'uri', 'value': 'http://quit.aksw.org/vocab/additions'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})
            self.assertDictEqual(changesets["results"]["bindings"][1], {
                "op": {'type': 'uri', 'value': 'http://quit.aksw.org/vocab/additions'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:1'},
                "o": {'type': 'literal', 'value': 'new'}})
            self.assertDictEqual(changesets["results"]["bindings"][2], {
                "op": {'type': 'uri', 'value': 'http://quit.aksw.org/vocab/removals'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:1> "new" .\n', f.read())
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual('\n', f.read())

    def testMultioperationalUpdateProvenance(self):
        """Test multioperational update and compare created provenance information.

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        4. Execute multioperational update query
        5. Execute SELECT query against provenace endpoint
        6. Re-start Quit
        7. Re-execute SELECT query against provenance endpoint
        8. Compare both query results
        """
        # Create querystrings
        prov = 'SELECT DISTINCT ?op ?s ?p ?o '
        prov += 'WHERE {?activity <http://quit.aksw.org/vocab/updates> ?update ; '
        prov += '<http://www.w3.org/ns/prov#endedAtTime> ?time . '
        prov += '?update ?op ?g . GRAPH ?g {?s ?p ?o .} FILTER ( '
        prov += 'sameTerm(?op, <http://quit.aksw.org/vocab/additions>) '
        prov += '|| sameTerm(?op, <http://quit.aksw.org/vocab/removals>) ) } '
        prov += 'ORDER BY ?time ?update ?g ?s ?p ?o'

        update = 'INSERT DATA {graph <http://example.org/> {<urn:1> <urn:2> <urn:3> . <urn:11> <urn:22> <urn:33>. }}; '
        update += 'INSERT DATA {graph <http://aksw.org/> {<urn:do> <urn:something> <urn:here> }}; '
        update += 'DELETE {GRAPH <http://example.org/> {<urn:1> <urn:2> <urn:3> .}} '
        update += 'INSERT {GRAPH <http://example.org/> {<urn:I> <urn:II> <urn:III> .}} '
        update += 'WHERE {GRAPH <http://example.org/> {<urn:1> <urn:2> <urn:3> .}}'

        # Prepate a git Repository
        repoContent = {'http://example.org/': '', 'http://aksw.org/': ''}

        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            args['features'] = Feature.Provenance
            app = create_app(args).test_client()

            # execute multioperational update query
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute PROVENANCE query
            prov_1 = app.post('/provenance', data=dict(query=prov), headers=dict(accept="application/sparql-results+json"))
            changesets_1 = json.loads(prov_1.data.decode("utf-8"))

            # re-start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            args['features'] = Feature.Provenance
            app = create_app(args).test_client()

            # execute PROVENANCE query again
            prov_2 = app.post('/provenance', data=dict(query=prov), headers=dict(accept="application/sparql-results+json"))
            changesets_2 = json.loads(prov_2.data.decode("utf-8"))

            # compare provenance queries
            self.assertDictEqual(changesets_1, changesets_2)

    @unittest.skip("Skipped until rdflib properly handles FROM NAMED and USING NAMED")
    def testDeleteInsertUsingNamedWhere(self):
        """Test DELETE INSERT WHERE with one graph

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute SELECT query
        4. execute DELETE INSERT USING NAMED WHERE query
        5. execute SELECT query
        """
        # Prepate a git Repository
        content1 = '<urn:x> <urn:y> <urn:z> .'
        content2 = '<urn:1> <urn:2> <urn:3> .'
        repoContent = {'http://example.org/': content1, 'http://aksw.org/': content2}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before UPDATE
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute DELETE INSERT USING NAMED WHERE query
            update = 'DELETE {graph <http://example.org/> {?s1 <urn:y> <urn:z> .} graph <http://aksw.org/> {?s2 <urn:2> <urn:3> .}} '
            update += 'INSERT {graph <http://example.org/> {?s2 <urn:2> ?g2 .} graph <http://aksw.org/> {?s1 <urn:y> ?g1 .}} '
            update += 'USING NAMED <http://example.org/> USING NAMED <http://aksw.org> '
            update += 'WHERE {GRAPH ?g1 {?s1 <urn:y> <urn:z>} . GRAPH ?g2 {?s2 <urn:2> <urn:3> .}}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after UPDATE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:1'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'http://example.org/'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:1'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'http://aksw.org/'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:y> <http://example.org/> .\n', f.read())
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual('<urn:1> <urn:2> <http://aksw.org/> .\n', f.read())

    def testDeleteInsertUsingWhere(self):
        """Test DELETE INSERT WHERE with one graph

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute SELECT query
        4. execute DELETE INSERT USING WHERE query
        5. execute SELECT query
        """
        # Prepate a git Repository
        content1 = '<urn:x> <urn:y> <urn:z> .'
        content2 = '<urn:1> <urn:2> <urn:3> .'
        repoContent = {'http://example.org/': content1, 'http://aksw.org/': content2}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before UPDATE
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute DELETE INSERT USING NAMED WHERE query
            update = 'DELETE {graph <http://example.org/> {?s1 <urn:y> <urn:z> .} graph <http://aksw.org/> {?s2 <urn:2> <urn:3> .}} '
            update += 'INSERT {graph <http://example.org/> {?s2 <urn:2> <urn:3> .} graph <http://aksw.org/> {?s1 <urn:y> <urn:z> .}} '
            update += 'USING <http://example.org/> USING <http://aksw.org/> '
            update += 'WHERE {?s1 <urn:y> <urn:z> . ?s2 <urn:2> <urn:3> .}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after UPDATE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:1'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:1'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:y> <urn:z> .\n', f.read())
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual('<urn:1> <urn:2> <urn:3> .\n', f.read())

    def testDeleteMatchWhere(self):
        """Test DELETE WHERE with two non empty graphs.

        1. Prepare a git repository two non empty graphs
        2. Start Quit
        3. execute SELECT query
        4. execute DELETE match WHERE query
        5. execute SELECT query
        """
        # Prepate a git Repository
        content_example = '<urn:x> <urn:y> <urn:z> .'
        content_aksw = '<urn:x> <urn:2> <urn:3> .'
        repoContent = {'http://example.org/': content_example, 'http://aksw.org/': content_aksw}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute DELETE WHERE query
            update = 'DELETE {GRAPH <http://aksw.org/> {?a <urn:2> <urn:3> .}} WHERE {GRAPH <http://example.org/> {?a <urn:y> <urn:z> .}}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 1)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('\n', f.read())
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:y> <urn:z> .\n', f.read())

    def testDeleteWhere(self):
        """Test DELETE WHERE with two non empty graphs.

        1. Prepare a git repository two non empty graphs
        2. Start Quit
        3. execute SELECT query
        4. execute DELETE match WHERE query
        5. execute SELECT query
        """
        # Prepate a git Repository
        content_example = "<urn:x> <urn:2> <urn:3> .\n"
        content_example+= "<urn:y> <urn:2> <urn:3> .\n"
        repoContent = {'http://example.org/': content_example}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute DELETE WHERE query
            update = 'DELETE WHERE {GRAPH <http://example.org/> {?a <urn:2> <urn:3> .}} '
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:y'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 0)

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('\n', f.read())

    def testDeleteUsingWhere(self):
        """Test DELETE USING WHERE with two non empty graphs.

        1. Prepare a git repository two non empty graphs
        2. Start Quit
        3. execute SELECT query
        4. execute DELETE USING WHERE query
        5. execute SELECT query
        """
        # Prepate a git Repository
        content_example = '<urn:x> <urn:y> <urn:z> .'
        content_aksw = '<urn:x> <urn:2> <urn:3> .'
        repoContent = {'http://example.org/': content_example, 'http://aksw.org/': content_aksw}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute DELETE USING WHERE query
            update = 'DELETE {GRAPH <http://aksw.org/> {?a <urn:2> <urn:3> .}} USING <http://example.org/> WHERE {?a <urn:y> <urn:z> .}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 1)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('\n', f.read())
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:y> <urn:z> .\n', f.read())

    def testFeatureProvenance(self):
        """Test if feature is active or not."""
        # Prepate a git Repository
        with TemporaryRepository() as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            args['features'] = Feature.Provenance
            app = create_app(args).test_client()

            query = "SELECT * WHERE {graph ?g {?s ?p ?o .}}"
            response = app.post('/provenance', data=dict(query=query))
            self.assertEqual(response.status, '200 OK')

            query = "foo bar"
            response = app.post('/provenance', data=dict(query=query))
            self.assertEqual(response.status, '400 BAD REQUEST')

            query = "INSERT DATA {graph <urn:graph> {<urn:x> <urn:y> <urn:z> .}}"
            response = app.post('/provenance', data=dict(query=query))
            self.assertEqual(response.status, '400 BAD REQUEST')

    def testInitAndSelectFromEmptyGraph(self):
        """Test select from newly created app, starting with an empty graph.

        1. Prepare a git repository with an empty graph
        2. Start Quit
        3. execute SELECT query
        """
        # Prepate a git Repository
        with TemporaryRepositoryFactory().withEmptyGraph("http://example.org/") as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp = app.post(
                '/sparql',
                data=dict(query=select),
                headers=dict(accept="application/sparql-results+json")
            )

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 0)

    def testInitAndSelectFromNonEmptyGraphPost(self):
        """Test select from newly created app, starting with a non empty graph.

        1. Prepare a git repository with a non empty graph
        2. Start Quit
        3. execute SELECT query
        """
        # Prepate a git Repository
        graphContent = '<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .'
        with TemporaryRepositoryFactory().withGraph("http://example.org/", graphContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query
            select = 'SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o'
            select_resp = app.post(
                '/sparql',
                data=dict(query=select),
                headers=dict(accept="application/sparql-results+json")
            )

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            # obj = json.load(select_resp.data)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'http://ex.org/x'},
                "p": {'type': 'uri', 'value': 'http://ex.org/y'},
                "o": {'type': 'uri', 'value': 'http://ex.org/z'}})

    def testInitAndSelectFromNonEmptyGraphPostDataInBody(self):
        """Test select from newly created app, starting with a non empty graph.

        1. Prepare a git repository with a non empty graph
        2. Start Quit
        3. execute SELECT query
        """

        # Prepate a git Repository
        graphContent = '<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .'
        with TemporaryRepositoryFactory().withGraph("http://example.org/", graphContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query
            select = "SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"
            select_resp = app.post(
                '/sparql',
                data=select,
                content_type="application/sparql-query",
                headers={"accept": "application/sparql-results+json"}
            )

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            # obj = json.load(select_resp.data)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'http://ex.org/x'},
                "p": {'type': 'uri', 'value': 'http://ex.org/y'},
                "o": {'type': 'uri', 'value': 'http://ex.org/z'}})

    def testInitAndSelectFromNonEmptyGraphGet(self):
        """Test select from newly created app, starting with a non empty graph.

        1. Prepare a git repository with a non empty graph
        2. Start Quit
        3. execute SELECT query
        """

        # Prepate a git Repository
        graphContent = '<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .'
        with TemporaryRepositoryFactory().withGraph("http://example.org/", graphContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query
            select = "SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"

            select_resp = app.get(
                '/sparql',
                query_string=dict(query=select),
                headers=dict(accept="application/sparql-results+json")
            )

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            # obj = json.load(select_resp.data)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'http://ex.org/x'},
                "p": {'type': 'uri', 'value': 'http://ex.org/y'},
                "o": {'type': 'uri', 'value': 'http://ex.org/z'}})

    def testInsertDataIntoEmptyRepository(self):
        """Test inserting data and selecting it, starting with an empty directory.

        1. Prepare an empty directory
        2. Start Quit
        3. execute INSERT DATA query
        4. execute SELECT query
        """
        # Prepate a git Repository
        with TemporaryDirectory() as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo
            app = create_app(args).test_client()

            # execute INSERT DATA query
            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/a> <http://ex.org/b> <http://ex.org/c> .}}"
            app.post('/sparql', data=dict(update=update))

            # execute SELECT query
            select = "SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"
            select_resp = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'http://ex.org/a'},
                "p": {'type': 'uri', 'value': 'http://ex.org/b'},
                "o": {'type': 'uri', 'value': 'http://ex.org/c'}})

    def testInsertDataIntoEmptyRepositoryStopRestart(self):
        """Test inserting data starting with an empty directory, restarting quit and  selecting it.

        1. Prepare an empty directory
        2. Start Quit
        3. execute INSERT DATA query
        4. Restart Quit
        4. execute SELECT query
        """
        # Prepate a git Repository
        with TemporaryDirectory() as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo
            app = create_app(args).test_client()

            # execute INSERT DATA query
            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/a> <http://ex.org/b> <http://ex.org/c> .}}"
            app.post('/sparql', data=dict(update=update))

            # Restart Quit
            re_app = create_app(args).test_client()

            # execute SELECT query
            select = "SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"
            select_resp = re_app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'http://ex.org/a'},
                "p": {'type': 'uri', 'value': 'http://ex.org/b'},
                "o": {'type': 'uri', 'value': 'http://ex.org/c'}})

    def testInsertDataAndSelectFromEmptyGraph(self):
        """Test inserting data and selecting it, starting with an empty graph.

        1. Prepare a git repository with an empty graph
        2. Start Quit
        3. execute INSERT DATA query
        4. execute SELECT query
        """
        # Prepate a git Repository
        with TemporaryRepositoryFactory().withEmptyGraph("http://example.org/") as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute INSERT DATA query
            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/a> <http://ex.org/b> <http://ex.org/c> .}}"
            app.post('/sparql', data=dict(update=update))

            # execute SELECT query
            select = "SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"
            select_resp = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'http://ex.org/a'},
                "p": {'type': 'uri', 'value': 'http://ex.org/b'},
                "o": {'type': 'uri', 'value': 'http://ex.org/c'}})

    def testInsertDataAndSelectFromEmptyGraphPostDataInBody(self):
        """Test inserting data and selecting it, starting with an empty graph.

        1. Prepare a git repository with an empty graph
        2. Start Quit
        3. execute INSERT DATA query
        4. execute SELECT query
        """
        # Prepate a git Repository
        with TemporaryRepositoryFactory().withEmptyGraph("http://example.org/") as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute INSERT DATA query
            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/a> <http://ex.org/b> <http://ex.org/c> .}}"
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query
            select = "SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"
            select_resp = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'http://ex.org/a'},
                "p": {'type': 'uri', 'value': 'http://ex.org/b'},
                "o": {'type': 'uri', 'value': 'http://ex.org/c'}})

    def testInsertDataAndSelectFromNonEmptyGraph(self):
        """Test inserting data and selecting it, starting with a non empty graph.

        1. Prepare a git repository with a non empty graph
        2. Start Quit
        3. execute INSERT DATA query
        4. execute SELECT query
        """
        # Prepate a git Repository
        graphContent = '<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .'
        with TemporaryRepositoryFactory().withGraph("http://example.org/", graphContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query
            select = "SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"
            select_resp = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute INSERT DATA query
            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/a> <http://ex.org/b> <http://ex.org/c> .}}"
            app.post('/sparql', data=dict(update=update))

            # execute SELECT query
            select = "SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"
            select_resp = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 2)

            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'http://ex.org/a'},
                "p": {'type': 'uri', 'value': 'http://ex.org/b'},
                "o": {'type': 'uri', 'value': 'http://ex.org/c'}})

    def testInsertDataIntoRepositoryDontOverwriteLocalFile(self):
        """Test inserting data wile locally changing the graph file.

        1. Prepare a repository
        2. Start Quit
        3. execute INSERT DATA query
        4. change file in filesystem
        """
        # Prepate a git Repository
        graphContent = '<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .\n'
        with TemporaryRepositoryFactory().withGraph("http://example.org/", graphContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            with open(path.join(repo.workdir, "graph.nt"), "w") as graphFile:
                graphContent += '<http://ex.org/z> <http://ex.org/z> <http://ex.org/z> .\n'
                graphFile.write(graphContent)

            # execute INSERT DATA query
            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/a> <http://ex.org/b> <http://ex.org/c> .}}"
            app.post('/sparql', data=dict(update=update))

            # execute SELECT query
            select = "SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"
            select_resp = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 2)

            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'http://ex.org/a'},
                "p": {'type': 'uri', 'value': 'http://ex.org/b'},
                "o": {'type': 'uri', 'value': 'http://ex.org/c'}})

            self.assertDictEqual(obj["results"]["bindings"][1], {
                "s": {'type': 'uri', 'value': 'http://ex.org/x'},
                "p": {'type': 'uri', 'value': 'http://ex.org/y'},
                "o": {'type': 'uri', 'value': 'http://ex.org/z'}})

            with open(path.join(repo.workdir, "graph.nt"), "r") as graphFile:
                self.assertEqual(graphFile.read(), graphContent)

    def testInsertDeleteFromEmptyGraph(self):
        """Test inserting and deleting data and selecting it, starting with an empty graph.

        1. Prepare a git repository with an empty graph
        2. Start Quit
        3. execute INSERT DATA/DELET DATA query
        4. execute SELECT query
        """
        # Prepate a git Repository
        graphContent = '<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .'
        with TemporaryRepositoryFactory().withGraph("http://example.org/", graphContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # fill graph with one triple
            insert = "INSERT DATA {graph <http://example.org/> {<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .}}"
            app.post('/sparql', data=dict(query=insert))

            # execute SELECT query
            select = "SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"
            select_resp = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute INSERT and DELETE query
            update = "DELETE DATA {graph <http://example.org/> {<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .}};"
            update += "INSERT DATA {graph <http://example.org/> {<http://ex.org/a> <http://ex.org/b> <http://ex.org/c> .}}"
            app.post('/sparql', data=dict(update=update))

            # test file content
            expectedFileContent = '<http://ex.org/a> <http://ex.org/b> <http://ex.org/c> .\n'
            with open(path.join(repo.workdir, 'graph.nt'), 'r') as f:
                self.assertEqual(expectedFileContent, f.read())

            self.assertFalse(os.path.isfile(path.join(repo.workdir, 'unassigned')))

            # execute SELECT query
            select = "SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"
            select_resp = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'http://ex.org/a'},
                "p": {'type': 'uri', 'value': 'http://ex.org/b'},
                "o": {'type': 'uri', 'value': 'http://ex.org/c'}})

    def testInsertDeleteFromNonEmptyGraph(self):
        """Test inserting and deleting data and selecting it, starting with a non empty graph.

        1. Prepare a git repository with a non empty graph
        2. Start Quit
        3. execute INSERT DATA/DELET DATA query
        4. execute SELECT query
        """
        # Prepate a git Repository
        graphContent = '<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .'
        with TemporaryRepositoryFactory().withGraph("http://example.org/", graphContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query
            select = "SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"
            select_resp = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute INSERT and DELETE query
            update = "DELETE DATA {graph <http://example.org/> {<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .}};"
            update += "INSERT DATA {graph <http://example.org/> {<http://ex.org/a> <http://ex.org/b> <http://ex.org/c> .}}"
            app.post('/sparql', data=dict(update=update))

            # test file content
            expectedFileContent = '<http://ex.org/a> <http://ex.org/b> <http://ex.org/c> .\n'
            with open(path.join(repo.workdir, 'graph.nt'), 'r') as f:
                self.assertEqual(expectedFileContent, f.read())

            self.assertFalse(os.path.isfile(path.join(repo.workdir, 'unassigned')))

            # execute SELECT query
            select = "SELECT * WHERE {graph <http://example.org/> {?s ?p ?o .}} ORDER BY ?s ?p ?o"
            select_resp = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'http://ex.org/a'},
                "p": {'type': 'uri', 'value': 'http://ex.org/b'},
                "o": {'type': 'uri', 'value': 'http://ex.org/c'}})

    def testInsertWhere(self):
        """Test INSERT WHERE with an empty and a non empty graph.

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute SELECT query
        4. execute INSERT WHERE query
        5. execute SELECT query
        """
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z> .'
        repoContent = {'http://example.org/': content, 'http://aksw.org/': ''}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before INSERT WHERE
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute INSERT WHERE query
            update = 'INSERT {GRAPH <http://aksw.org/> {?a <urn:1> "new" .}} WHERE {GRAPH <http://example.org/> {?a <urn:y> <urn:z> .}}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after INSERT WHERE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 1)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:1'},
                "o": {'type': 'literal', 'value': 'new'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:1> "new" .\n', f.read())
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:y> <urn:z> .\n', f.read())

    def testInsertWhereVariables(self):
        """Test INSERT WHERE with an empty and a non empty graph.

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute SELECT query
        4. execute INSERT WHERE query
        5. execute SELECT query
        """
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z1> .\n'
        content += '<urn:x> <urn:y> <urn:z2> .'
        repoContent = {'http://example.org/': content, 'http://aksw.org/': ''}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before INSERT WHERE
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute INSERT WHERE query
            update = 'INSERT {GRAPH <http://aksw.org/> {?a <urn:1> "new" .}} WHERE {GRAPH <http://example.org/> {?a <urn:y> ?x .}}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after INSERT WHERE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z1'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z2'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 3)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:1'},
                "o": {'type': 'literal', 'value': 'new'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z1'}})
            self.assertDictEqual(obj["results"]["bindings"][2], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z2'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:1> "new" .\n', f.read())
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual(
                    '<urn:x> <urn:y> <urn:z1> .\n<urn:x> <urn:y> <urn:z2> .\n', f.read())

    def testTwoInsertWhereVariables(self):
        """Test two INSERT WHERE (; concatenated) with an empty and a non empty graph.

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute SELECT query
        4. execute INSERT WHERE queries
        5. execute SELECT query
        """
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z1> .\n'
        content += '<urn:x> <urn:y> <urn:z2> .'
        repoContent = {'http://example.org/': content, 'http://aksw.org/': ''}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before INSERT WHERE
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute INSERT WHERE query
            update = 'INSERT {GRAPH <http://aksw.org/> {?a <urn:1> "new" .}} WHERE {GRAPH <http://example.org/> {?a <urn:y> ?x .}}; '
            update += 'INSERT {GRAPH <http://aksw.org/> {?a <urn:1> "new" .}} WHERE {GRAPH <http://example.org/> {?a <urn:y> ?x .}}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after INSERT WHERE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z1'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z2'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 3)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:1'},
                "o": {'type': 'literal', 'value': 'new'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z1'}})
            self.assertDictEqual(obj["results"]["bindings"][2], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z2'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:1> "new" .\n', f.read())
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual(
                    '<urn:x> <urn:y> <urn:z1> .\n<urn:x> <urn:y> <urn:z2> .\n', f.read())

    def testInsertUsingWhere(self):
        """Test INSERT USING WHERE with an empty and a non empty graph.

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute SELECT query
        4. execute INSERT WHERE query
        5. execute SELECT query
        """
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z> .'
        repoContent = {'http://example.org/': content, 'http://aksw.org/': ''}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before INSERT WHERE
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute INSERT USING WHERE query
            update = 'INSERT {GRAPH <http://aksw.org/> {?a <urn:1> "new" .}} USING <http://example.org/> WHERE {?a <urn:y> <urn:z> .}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after INSERT WHERE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 1)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:1'},
                "o": {'type': 'literal', 'value': 'new'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:1> "new" .\n', f.read())
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:y> <urn:z> .\n', f.read())

    def testLoadIntoGraph(self):
        """Test LOAD <resource> INTO GRAPH <http://example.org/> ."""
        # Prepate a git Repository
        content = ''
        repoContent = {'http://example.org/': content}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            select = "ASK {graph <http://example.org/> {?s ?p ?o .}}"
            select_resp_after = app.post('/sparql', data={"query": select}, headers=dict(accept="application/sparql-results+json"))
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertFalse(obj["boolean"])

            # execute SELECT query before INSERT WHERE
            load = "LOAD <http://aksw.org/Projects/Quit> INTO GRAPH <http://example.org/>"
            resp = app.post('/sparql', data={"update": load})
            self.assertEqual(resp.status, "200 OK")

            select = "ASK {graph <http://example.org/> {?s ?p ?o .}}"
            select_resp_after = app.post('/sparql', data={"query": select}, headers=dict(accept="application/sparql-results+json"))
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertTrue(obj["boolean"])


    def testLogfileExists(self):
        """Test if a logfile is created."""
        with TemporaryRepositoryFactory().withEmptyGraph("urn:graph") as repo:
            logFile = path.join(repo.workdir, 'quit.log')
            self.assertFalse(os.path.isfile(logFile))

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            args['logfile'] = logFile
            app = create_app(args).test_client()

            self.assertTrue(os.path.isfile(logFile))

    def testLogfileNotExists(self):
        """Test start of quit store without logfile."""
        with TemporaryRepositoryFactory().withEmptyGraph("urn:graph") as repo:
            logFile = path.join(repo.workdir, 'quit.log')
            self.assertFalse(os.path.isfile(logFile))

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            self.assertFalse(os.path.isfile(logFile))

    def testThreeWayMerge(self):
        """Test merging two commits."""

        # Prepate a git Repository
        content = "<http://ex.org/a> <http://ex.org/b> <http://ex.org/c> ."
        with TemporaryRepositoryFactory().withGraph("http://example.org/", content) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()
            current_head = repo.head.shorthand

            response = app.post("/branch", data={"oldbranch": current_head, "newbranch": "develop"})
            self.assertEqual(response.status, '201 CREATED')

            # execute INSERT DATA query
            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .}}"
            response = app.post('/sparql', data={"update": update})
            self.assertEqual(response.status, '200 OK')

            app = create_app(args).test_client()
            # start new app to syncAll()

            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/z> <http://ex.org/z> <http://ex.org/z> .}}"
            response = app.post('/sparql/develop?ref=develop', data={"update": update})
            self.assertEqual(response.status, '200 OK')

            response = app.post("/merge", data={"target": current_head, "branch": "develop", "method": "three-way"})
            self.assertEqual(response.status, '201 CREATED')

    def testContextMergeConflict(self):
        """Test merging two commits."""

        # Prepate a git Repository
        content = "<http://ex.org/a> <http://ex.org/b> <http://ex.org/c> ."
        with TemporaryRepositoryFactory().withGraph("http://example.org/", content) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()
            current_head = repo.head.shorthand

            response = app.post("/branch", data={"oldbranch": current_head, "newbranch": "develop"})
            self.assertEqual(response.status, '201 CREATED')

            # execute INSERT DATA query
            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .}}"
            response = app.post('/sparql', data={"update": update})
            self.assertEqual(response.status, '200 OK')

            app = create_app(args).test_client()
            # start new app to syncAll()

            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/z> <http://ex.org/z> <http://ex.org/z> .}}"
            response = app.post('/sparql/develop?ref=develop', data={"update": update})
            self.assertEqual(response.status, '200 OK')

            response = app.post("/merge", data={"target": current_head, "branch": "develop", "method": "context"})
            self.assertEqual(response.status, '409 CONFLICT')

            # The merge shoudl detect the node <http://ex.org/z> as a potential conflict


    def testContextMerge(self):
        """Test merging two commits."""

        # Prepate a git Repository
        content = "<http://ex.org/a> <http://ex.org/b> <http://ex.org/c> ."
        with TemporaryRepositoryFactory().withGraph("http://example.org/", content) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()
            current_head = repo.head.shorthand

            response = app.post("/branch", data={"oldbranch": current_head, "newbranch": "develop"})
            self.assertEqual(response.status, '201 CREATED')

            # execute INSERT DATA query
            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/x> <http://ex.org/y> <http://ex.org/z> .}}"
            response = app.post('/sparql', data={"update": update})
            self.assertEqual(response.status, '200 OK')

            app = create_app(args).test_client()
            # start new app to syncAll()

            update = "INSERT DATA {graph <http://example.org/> {<http://ex.org/r> <http://ex.org/r> <http://ex.org/r> .}}"
            response = app.post('/sparql/develop?ref=develop', data={"update": update})
            self.assertEqual(response.status, '200 OK')

            response = app.post("/merge", data={"target": current_head, "branch": "develop", "method": "context"})
            self.assertEqual(response.status, '201 CREATED')

    def testPull(self):
        """Test /pull API request."""
        graphContent = """
            <http://ex.org/x> <http://ex.org/x> <http://ex.org/x> ."""
        with TemporaryRepositoryFactory().withGraph("http://example.org/", graphContent) as remote:
            with TemporaryRepository(clone_from_repo=remote) as local:

                with open(path.join(remote.workdir, "graph.nt"), "a") as graphFile:
                    graphContent = """
                        <http://ex.org/x> <http://ex.org/y> <http://ex.org/z> ."""
                    graphFile.write(graphContent)

                createCommit(repository=remote)

                args = quitApp.getDefaults()
                args['targetdir'] = local.workdir
                app = create_app(args).test_client()

                beforePull = {'s': {'type': 'uri', 'value': 'http://ex.org/x'},
                              'p': {'type': 'uri', 'value': 'http://ex.org/x'},
                              'o': {'type': 'uri', 'value': 'http://ex.org/x'},
                              'g': {'type': 'uri', 'value': 'http://example.org/'}}

                query = "SELECT * WHERE {graph ?g {?s ?p ?o .}}"

                response = app.post('/sparql', data=dict(query=query),
                                    headers={'Accept': 'application/sparql-results+json'})
                resultBindings = json.loads(response.data.decode("utf-8"))['results']['bindings']

                self.assertEqual(len(resultBindings), 1)
                self.assertDictEqual(resultBindings[0], beforePull)
                assertResultBindingsEqual(self, resultBindings, [beforePull])

                response = app.get('/pull/origin')
                self.assertEqual(response.status, '200 OK')

                afterPull = {'s': {'type': 'uri', 'value': 'http://ex.org/x'},
                             'p': {'type': 'uri', 'value': 'http://ex.org/y'},
                             'o': {'type': 'uri', 'value': 'http://ex.org/z'},
                             'g': {'type': 'uri', 'value': 'http://example.org/'}}

                response = app.post('/sparql', data=dict(query=query),
                                    headers={'Accept': 'application/sparql-results+json'})
                resultBindings = json.loads(response.data.decode("utf-8"))['results']['bindings']

                self.assertEqual(response.status, '200 OK')
                self.assertEqual(len(resultBindings), 2)

                assertResultBindingsEqual(self, resultBindings, [beforePull, afterPull])

    def testPullEmptyInitialGraph(self):
        """Test /pull API request starting with an initially empty graph."""
        with TemporaryRepositoryFactory().withGraph("http://example.org/", "") as remote:
            with TemporaryRepository(clone_from_repo=remote) as local:

                with open(path.join(remote.workdir, "graph.nt"), "a") as graphFile:
                    graphContent = """
                        <http://ex.org/x> <http://ex.org/y> <http://ex.org/z> ."""
                    graphFile.write(graphContent)

                createCommit(repository=remote)

                args = quitApp.getDefaults()
                args['targetdir'] = local.workdir
                app = create_app(args).test_client()

                query = "SELECT * WHERE {graph ?g {?s ?p ?o .}}"

                response = app.post('/sparql', data=dict(query=query),
                                    headers={'Accept': 'application/sparql-results+json'})
                resultBindings = json.loads(response.data.decode("utf-8"))['results']['bindings']

                self.assertEqual(len(resultBindings), 0)
                assertResultBindingsEqual(self, resultBindings, [])

                response = app.get('/pull/origin')
                self.assertEqual(response.status, '200 OK')

                afterPull = {'s': {'type': 'uri', 'value': 'http://ex.org/x'},
                             'p': {'type': 'uri', 'value': 'http://ex.org/y'},
                             'o': {'type': 'uri', 'value': 'http://ex.org/z'},
                             'g': {'type': 'uri', 'value': 'http://example.org/'}}

                response = app.post('/sparql', data=dict(query=query),
                                    headers={'Accept': 'application/sparql-results+json'})
                resultBindings = json.loads(response.data.decode("utf-8"))['results']['bindings']

                self.assertEqual(response.status, '200 OK')
                self.assertEqual(len(resultBindings), 1)

                assertResultBindingsEqual(self, resultBindings, [afterPull])

    def testPullStartFromEmptyRepository(self):
        """Test /pull API request starting the store from an empty repository.
        """
        graphContent = """
            <http://ex.org/x> <http://ex.org/y> <http://ex.org/z> ."""
        with TemporaryRepositoryFactory().withGraph("http://example.org/", graphContent) as remote:
            with TemporaryRepository() as local:
                local.remotes.create("origin", remote.path)

                args = quitApp.getDefaults()
                args['targetdir'] = local.workdir
                app = create_app(args).test_client()

                query = "SELECT * WHERE {graph ?g {?s ?p ?o .}}"

                response = app.post('/sparql', data=dict(query=query),
                                    headers={'Accept': 'application/sparql-results+json'})
                resultBindings = json.loads(response.data.decode("utf-8"))['results']['bindings']

                self.assertEqual(len(resultBindings), 0)

                current_remote_head = remote.head.shorthand

                response = app.get('/pull/origin/' + current_remote_head)
                self.assertEqual(response.status, '200 OK')

                afterPull = {'s': {'type': 'uri', 'value': 'http://ex.org/x'},
                             'p': {'type': 'uri', 'value': 'http://ex.org/y'},
                             'o': {'type': 'uri', 'value': 'http://ex.org/z'},
                             'g': {'type': 'uri', 'value': 'http://example.org/'}}

                response = app.post('/sparql', data=dict(query=query),
                                    headers={'Accept': 'application/sparql-results+json'})
                resultBindings = json.loads(response.data.decode("utf-8"))['results']['bindings']

                self.assertEqual(response.status, '200 OK')
                self.assertEqual(len(resultBindings), 1)

                assertResultBindingsEqual(self, resultBindings, [afterPull])

    def testReloadStore(self):
        """Test reload of quit store, starting with an emtpy graph.

        1. Start app
        2. Execute INSERT query
        3. Restart app
        4. Execute SELECT query and expect one result
        """
        # Prepate a git Repository
        with TemporaryRepositoryFactory().withEmptyGraph("urn:graph") as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute INSERT DATA query
            update = "INSERT DATA {graph <urn:graph> {<urn:x> <urn:y> <urn:z> .}}"
            app.post('/sparql', data=dict(update=update))

            # reload the store
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            newApp = create_app(args).test_client()

            # execute SELECT query
            select = "SELECT * WHERE {graph <urn:graph> {?s ?p ?o .}} ORDER BY ?s ?p ?o"
            select_resp = newApp.post(
                '/sparql',
                data=dict(query=select),
                headers=dict(accept="application/sparql-results+json")
            )

            obj = json.loads(select_resp.data.decode("utf-8"))

            self.assertEqual(len(obj["results"]["bindings"]), 1)

            self.assertDictEqual(obj["results"]["bindings"][0], {
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

    def testRepoDataAfterInitWithEmptyContent(self):
        """Test file content from newly created app, starting with an empty graph.

        1. Prepare a git repository with a non empty graph
        2. Start Quit
        3. check file content
        """
        # Prepate a git Repository
        graphContent = "<urn:x> <urn:y> <urn:z> ."
        with TemporaryRepositoryFactory().withGraph('urn:graph', graphContent) as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # get commit message
            for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL):
                self.assertEqual(commit.message, 'init')

            # compare file content
            with open(path.join(repo.workdir, 'graph.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:y> <urn:z> .', f.read())

    def testRepoDataAfterInitWithNonEmptyGraph(self):
        """Test file content from newly created app, starting with a non empty graph/repository.

        1. Prepare a git repository with a non empty graph
        2. Start Quit
        3. check file content
        """
        # Prepate a git Repository
        with TemporaryRepositoryFactory().withGraph('urn:graph') as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # get commit message
            for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL):
                self.assertEqual(commit.message, 'init')

            # compare file content
            with open(path.join(repo.workdir, 'graph.nt'), 'r') as f:
                self.assertEqual('', f.read())

    def testRepoDataAfterInsertStaringWithEmptyGraph(self):
        """Test inserting data and check the file content, starting with an empty graph.

        1. Prepare a git repository with an empty graph
        2. Start Quit
        3. execute INSERT DATA query
        4. check file content
        """
        # Prepate a git Repository
        with TemporaryRepositoryFactory().withEmptyGraph("urn:graph") as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute INSERT DATA query
            update = "INSERT DATA {graph <urn:graph> {<urn:x> <urn:y> <urn:z> .}}"
            app.post('/sparql', data=dict(update=update))

            # test file content
            expectedFileContent = '<urn:x> <urn:y> <urn:z> .\n'

            with open(path.join(repo.workdir, 'graph.nt'), 'r') as f:
                self.assertEqual(expectedFileContent, f.read())

            # check commit messages
            expectedCommitMsg = set()
            expectedCommitMsg.add("New Commit from QuitStore")
            expectedCommitMsg.add("Query: \"INSERT DATA {graph <urn:graph> "
                                  "{<urn:x> <urn:y> <urn:z> .}}\"")
            expectedCommitMsg.add("OperationTypes: \"INSERT\"")
            expectedCommitMsg.add("")

            commits = []

            for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL):
                commits.append(commit.message.strip())


            expectedCommits = [['init'], expectedCommitMsg]
            for commit in commits:
                expectedMessage = expectedCommits.pop()
                self.assertEqual(sorted(set(commit.split("\n"))), sorted(expectedMessage))

    def testRepoDataAfterInsertStaringWithNonEmptyGraph(self):
        """Test inserting data and check the file content, starting with a non empty graph.

        1. Prepare a git repository with an empty graph
        2. Start Quit
        3. execute INSERT DATA query
        4. check file content
        """
        # Prepate a git Repository
        graphContent = '<urn:x> <urn:y> <urn:z> .'
        with TemporaryRepositoryFactory().withGraph("urn:graph", graphContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            update = 'INSERT DATA {graph <urn:graph> {<urn:x2> <urn:y2> "literal" .}}'
            app.post('/sparql', data=dict(update=update))

            # test file content
            expectedFileContent = '<urn:x2> <urn:y2> "literal" .\n'
            expectedFileContent += '<urn:x> <urn:y> <urn:z> .\n'

            with open(path.join(repo.workdir, 'graph.nt'), 'r') as f:
                self.assertEqual(expectedFileContent, f.read())

            # check commit messages
            expectedCommitMsg = set()
            expectedCommitMsg.add("New Commit from QuitStore")
            expectedCommitMsg.add("Query: \"INSERT DATA {graph <urn:graph> "
                                  "{<urn:x2> <urn:y2> \\\"literal\\\" .}}\"")
            expectedCommitMsg.add("OperationTypes: \"INSERT\"")
            expectedCommitMsg.add("")

            commits = []

            for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL):
                commits.append(commit.message.strip())

            expectedCommits = [['init'], expectedCommitMsg]
            for commit in commits:
                expectedMessage = expectedCommits.pop()
                self.assertEqual(sorted(set(commit.split("\n"))), sorted(expectedMessage))

    def testStartApp(self):
        """Test start of quit store."""
        # Prepate a git Repository
        with TemporaryRepository() as repo:
            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            query = "SELECT * WHERE {graph ?g {?s ?p ?o .}}"
            response = app.post('/sparql', data=dict(query=query))
            self.assertEqual(response.status, '200 OK')

            response = app.post('/provenance', data=dict(query=query))
            self.assertEqual(response.status, '404 NOT FOUND')

    def testSubdirectoriesGraphfile(self):
        """Test if subdirectories are recognized and commits are working using graphfiles."""
        # Prepare a Repository with subdirectories
        repo_content = {'urn:graph0': '<urn:0> <urn:0> <urn:0> .\n',
                        'urn:graph1': '<urn:1> <urn:1> <urn:1> .\n'}

        with TemporaryRepositoryFactory().withGraphs(repo_content, 'graphfiles', True) as repo:
            select = 'SELECT ?s ?p ?o WHERE {{ GRAPH <urn:graph{}> {{ ?s ?p ?o }} }}'
            update = """
                DELETE DATA {{
                    GRAPH <urn:graph{i}> {{
                        <urn:{i}> <urn:{i}> <urn:{i}> . }} }} ;
                INSERT DATA {{
                    GRAPH <urn:graph{i}> {{
                        <urn:{i}{i}> <urn:{i}{i}> <urn:{i}{i}> . }} }}"""

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # check states after init
            for i in [0, 1]:
                self.assertTrue(
                    path.isfile(path.join(repo.workdir,
                                          'sub{}'.format(i),
                                          'graph_{}.nt.graph'.format(i))))
                # check store content
                res = app.post('/sparql',
                               data=dict(query=select.format(i)),
                               headers=dict(accept='application/sparql-results+json'))
                obj = json.loads(res.data.decode("utf-8"))
                self.assertEqual(len(obj["results"]["bindings"]), 1)
                self.assertDictEqual(obj["results"]["bindings"][0], {
                    "s": {'type': 'uri', 'value': 'urn:{}'.format(i)},
                    "p": {'type': 'uri', 'value': 'urn:{}'.format(i)},
                    "o": {'type': 'uri', 'value': 'urn:{}'.format(i)}})

                # check file existence
                with open(path.join(repo.workdir,
                                    'sub{}'.format(i),
                                    'graph_{}.nt'.format(i)), 'r') as f:
                    self.assertEqual(
                        '<urn:{i}> <urn:{i}> <urn:{i}> .\n'.format(i=i),
                        f.read())

            # check states after update
            for i in [0, 1]:
                # perform update
                app.post('/sparql', data=dict(update=update.format(i=i)))

                # check store content
                res = app.post('/sparql',
                               data=dict(query=select.format(i)),
                               headers=dict(accept='application/sparql-results+json'))
                obj = json.loads(res.data.decode("utf-8"))

                # check file existence
                with open(path.join(repo.workdir,
                                    'sub{}'.format(i),
                                    'graph_{}.nt'.format(i)), 'r') as f:
                    self.assertEqual(
                        '<urn:{i}{i}> <urn:{i}{i}> <urn:{i}{i}> .\n'.format(i=i),
                        f.read())

                self.assertEqual(len(obj["results"]["bindings"]), 1)
                self.assertDictEqual(obj["results"]["bindings"][0], {
                    "s": {'type': 'uri', 'value': 'urn:{i}{i}'.format(i=i)},
                    "p": {'type': 'uri', 'value': 'urn:{i}{i}'.format(i=i)},
                    "o": {'type': 'uri', 'value': 'urn:{i}{i}'.format(i=i)}})

    def testSubdirectoriesConfigfile(self):
        """Test if subdirectories are recognized and commits are working using configfile."""
        # Prepare a Repository with subdirectories
        repo_content = {'urn:graph0': '<urn:0> <urn:0> <urn:0> .\n',
                        'urn:graph1': '<urn:1> <urn:1> <urn:1> .\n'}

        with TemporaryRepositoryFactory().withGraphs(repo_content, 'configfile', True) as repo:
            select = 'SELECT ?s ?p ?o WHERE {{ GRAPH <urn:graph{}> {{ ?s ?p ?o }} }}'
            update = """
                DELETE DATA {{
                    GRAPH <urn:graph{i}> {{
                        <urn:{i}> <urn:{i}> <urn:{i}> . }} }} ;
                INSERT DATA {{
                    GRAPH <urn:graph{i}> {{
                        <urn:{i}{i}> <urn:{i}{i}> <urn:{i}{i}> . }} }}"""

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # check states after init
            for i in [0, 1]:
                self.assertFalse(path.isfile(path.join(repo.workdir,
                                             'sub{}'.format(i),
                                             'graph_{}.nt.graph'.format(i))))
                # check store content
                res = app.post('/sparql',
                               data=dict(query=select.format(i)),
                               headers=dict(accept='application/sparql-results+json'))
                obj = json.loads(res.data.decode("utf-8"))
                self.assertEqual(len(obj["results"]["bindings"]), 1)
                self.assertDictEqual(obj["results"]["bindings"][0], {
                    "s": {'type': 'uri', 'value': 'urn:{}'.format(i)},
                    "p": {'type': 'uri', 'value': 'urn:{}'.format(i)},
                    "o": {'type': 'uri', 'value': 'urn:{}'.format(i)}})

                # check file existence
                with open(path.join(repo.workdir,
                                    'sub{}'.format(i),
                                    'graph_{}.nt'.format(i)), 'r') as f:
                    self.assertEqual(
                        '<urn:{i}> <urn:{i}> <urn:{i}> .\n'.format(i=i),
                        f.read())

            # check states after update
            for i in [0, 1]:
                # perform update
                app.post('/sparql', data=dict(update=update.format(i=i)))

                # check store content
                res = app.post('/sparql',
                               data=dict(query=select.format(i)),
                               headers=dict(accept='application/sparql-results+json'))
                obj = json.loads(res.data.decode("utf-8"))

                # check file existence
                with open(path.join(repo.workdir,
                                    'sub{}'.format(i),
                                    'graph_{}.nt'.format(i)), 'r') as f:
                    self.assertEqual(
                        '<urn:{i}{i}> <urn:{i}{i}> <urn:{i}{i}> .\n'.format(i=i),
                        f.read())

                self.assertEqual(len(obj["results"]["bindings"]), 1)
                self.assertDictEqual(obj["results"]["bindings"][0], {
                    "s": {'type': 'uri', 'value': 'urn:{i}{i}'.format(i=i)},
                    "p": {'type': 'uri', 'value': 'urn:{i}{i}'.format(i=i)},
                    "o": {'type': 'uri', 'value': 'urn:{i}{i}'.format(i=i)}})

    def testWithOnDeleteAndInsert(self):
        """Test WITH on DELETE and INSERT plus USING.

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute SELECT query
        4. execute update
        5. execute SELECT query
        """
        # Prepate a git Repository
        content_example = '<urn:x> <urn:y> <urn:z> .'
        content_aksw = '<urn:x> <urn:2> <urn:3> .'
        repoContent = {'http://example.org/': content_example, 'http://aksw.org/': content_aksw}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before UPDATE
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute UPDATE
            update = 'WITH <http://example.org/> '
            update += 'DELETE {?s1 <urn:y> <urn:z> . GRAPH <http://aksw.org/> {?s1 <urn:2> <urn:3> .}} '
            update += 'INSERT {?s1 <urn:2> <urn:3> . GRAPH <http://aksw.org/> {?s1 <urn:y> <urn:z> .}} '
            update += 'WHERE {?s1 <urn:y> <urn:z> .}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after UPDATE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:y> <urn:z> .\n', f.read())
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:2> <urn:3> .\n', f.read())

    def testWithOnDeleteAndInsertUsing(self):
        """Test WITH on DELETE and INSERT plus USING.

        1. Prepare a git repository
        2. Start Quit
        3. execute SELECT query
        4. execute update
        5. execute SELECT query
        """
        # Prepate a git Repository
        content_example = '<urn:x> <urn:y> <urn:z> .'
        content_aksw = '<urn:1> <urn:2> <urn:3> .'
        repoContent = {'http://example.org/': content_example, 'http://aksw.org/': content_aksw}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before UPDATE
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute UPDATE
            update = 'WITH <http://aksw.org/> '
            update += 'DELETE {GRAPH <http://example.org/> {?s ?p ?o .} GRAPH <http://aksw.org/> {?s ?p ?o .}} '
            update += 'INSERT {GRAPH <http://aksw.org/> {?s ?p ?o .}} '
            update += 'USING <http://example.org/> '
            update += 'WHERE {?s ?p ?o .}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after UPDATE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:1'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:1'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual(
                    '<urn:1> <urn:2> <urn:3> .\n<urn:x> <urn:y> <urn:z> .\n',
                    f.read())
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual('\n', f.read())

    @unittest.skip("Skipped until rdflib properly handles FROM NAMED and USING NAMED")
    def testWithOnDeleteAndInsertUsingNamed(self):
        """Test WITH on DELETE and INSERT plus USING NAMED.

        It is expected that USING NAMED will win over WITH and the graph graph IRI can be derived
        from WHERE clause.

        1. Prepare a git repository
        2. Start Quit
        3. execute SELECT query
        4. execute update
        5. execute SELECT query
        """
        # Prepate a git Repository
        content_example = '<urn:x> <urn:y> <urn:z> .'
        content_aksw = '<urn:1> <urn:2> <urn:3> .'
        repoContent = {'http://example.org/': content_example, 'http://aksw.org/': content_aksw}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before UPDATE
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute UPDATE
            update = 'WITH <http://aksw.org/> '
            update += 'DELETE {GRAPH ?g {?s ?p ?o .}} '
            update += 'INSERT {?s ?p ?o .} '
            update += 'USING NAMED <http://example.org/> '
            update += 'WHERE {GRAPH ?g {?s ?p ?o .}}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after UPDATE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:1'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:1'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual(
                    '<urn:1> <urn:2> <urn:3> .\n<urn:x> <urn:y> <urn:z> .\n',
                    f.read())
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual('', f.read())

    def testWithOnDeleteAndInsert(self):
        """Test WITH on DELETE and INSERT.

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute SELECT query
        4. execute update
        5. execute SELECT query
        """
        # Prepate a git Repository
        content_example = '<urn:x> <urn:y> <urn:z> .'
        content_aksw = '<urn:x> <urn:2> <urn:3> .'
        repoContent = {'http://example.org/': content_example, 'http://aksw.org/': content_aksw}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before UPDATE
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute UPDATE
            update = 'WITH <http://example.org/> '
            update += 'DELETE {?s1 <urn:y> <urn:z> . GRAPH <http://aksw.org/> {?s1 <urn:2> <urn:3> .}} '
            update += 'INSERT {?s1 <urn:2> <urn:3> . GRAPH <http://aksw.org/> {?s1 <urn:y> <urn:z> .}} '
            update += 'WHERE {?s1 <urn:y> <urn:z> .}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after UPDATE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:y> <urn:z> .\n', f.read())
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:2> <urn:3> .\n', f.read())

    def testWithOnDelete(self):
        """Test WITH on DELETE and not on INSERT.

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute SELECT query
        4. execute update
        5. execute SELECT query
        """
        # Prepate a git Repository
        content_example = '<urn:x> <urn:y> <urn:z> .'
        content_aksw = ''
        repoContent = {'http://example.org/': content_example, 'http://aksw.org/': content_aksw}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before UPDATE
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute UPDATE
            update = 'WITH <http://example.org/> '
            update += 'DELETE {?s1 <urn:y> <urn:z> .} '
            update += 'INSERT {?s1 <urn:Y> <urn:Z> . GRAPH <http://aksw.org/> {?s1 <urn:2> <urn:3> .}} '
            update += 'WHERE {?s1 <urn:y> <urn:z> .}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after UPDATE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 1)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:Y'},
                "o": {'type': 'uri', 'value': 'urn:Z'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:2> <urn:3> .\n', f.read())
            # compare file content
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:Y> <urn:Z> .\n', f.read())

    def testWithOnDeleteUsing(self):
        """Test WITH on DELETE and not on INSERT plus USING.

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute SELECT query
        4. execute update
        5. execute SELECT query
        """
        # Prepate a git Repository
        content_example = '<urn:x> <urn:y> <urn:z> .'
        content_aksw = '<urn:1> <urn:2> <urn:3> .'
        repoContent = {'http://example.org/': content_example, 'http://aksw.org/': content_aksw}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before UPDATE
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute UPDATE
            update = 'WITH <http://aksw.org/> '
            update += 'DELETE {?s ?p ?o . GRAPH <http://example.org/> {?s ?p ?o .}} '
            update += 'INSERT {?s ?p ?o .} '
            update += 'USING <http://example.org/> '
            update += 'WHERE {?s ?p ?o .}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after UPDATE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:1'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:1'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual(
                    '<urn:1> <urn:2> <urn:3> .\n<urn:x> <urn:y> <urn:z> .\n',
                    f.read())
            # compare file content
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual('\n', f.read())

    @unittest.skip("Skipped until rdflib properly handles FROM NAMED and USING NAMED")
    def testWithOnDeleteUsingNamed(self):
        """Test WITH Delete and not on Insert plus USING NAMED.

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute SELECT query
        4. execute update
        5. execute SELECT query
        """
        # Prepate a git Repository
        content_example = '<urn:x> <urn:y> <urn:z> .'
        content_aksw = '<urn:1> <urn:2> <urn:3> .'
        repoContent = {'http://example.org/': content_example, 'http://aksw.org/': content_aksw}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before UPDATE
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute UPDATE
            update = 'WITH <http://aksw.org/> '
            update += 'DELETE {GRAPH ?g {?s ?p ?o .}} '
            update += 'INSERT {?s ?p ?o .} '
            update += 'USING NAMED <http://example.org/> '
            update += 'WHERE {GRAPH ?g {?s ?p ?o .}}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after UPDATE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:1'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:1'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual(
                    '<urn:1> <urn:2> <urn:3> .\n<urn:x> <urn:y> <urn:z> .\n',
                    f.read())
            # compare file content
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual('', f.read())

    def testWithOnInsert(self):
        """Test WITH on INSERT and not on DELETE.

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute SELECT query
        4. execute update
        5. execute SELECT query
        """
        # Prepate a git Repository
        content_example = '<urn:x> <urn:y> <urn:z> .'
        content_aksw = '<urn:1> <urn:x> <urn:3> .'
        repoContent = {'http://example.org/': content_example, 'http://aksw.org/': content_aksw}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before UPDATE
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute UPDATE
            update = 'WITH <http://example.org/> '
            update += 'DELETE {GRAPH <http://aksw.org/> {<urn:1> ?s1 <urn:3> .}} '
            update += 'INSERT {?s1 <urn:2> <urn:3> . GRAPH <http://aksw.org/> {?s1 <urn:y> <urn:z> .}} '
            update += 'WHERE {?s1 <urn:y> <urn:z> .}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after UPDATE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 2)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:1'},
                "p": {'type': 'uri', 'value': 'urn:x'},
                "o": {'type': 'uri', 'value': 'urn:3'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 3)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})
            self.assertDictEqual(obj["results"]["bindings"][2], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})
            self.assertDictEqual(obj["results"]["bindings"][1], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:2'},
                "o": {'type': 'uri', 'value': 'urn:3'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:y> <urn:z> .\n', f.read())
            # compare file content
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual(
                    '<urn:x> <urn:2> <urn:3> .\n<urn:x> <urn:y> <urn:z> .\n',
                    f.read())

    def testWithOnInsertUsing(self):
        """Test WITH on INSERT and not on DELETE plus USING.

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute SELECT query
        4. execute update
        5. execute SELECT query
        """
        # Prepate a git Repository
        content_example = '<urn:x> <urn:y> <urn:z> .'
        content_aksw = ''
        repoContent = {'http://example.org/': content_example, 'http://aksw.org/': content_aksw}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            # execute SELECT query before UPDATE
            select = "SELECT * WHERE {graph ?g {?s ?p ?o .}} ORDER BY ?g ?s ?p ?o"
            select_resp_before = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # execute UPDATE
            update = 'WITH <http://aksw.org/> '
            update += 'DELETE {GRAPH <http://example.org/> {?s ?p ?o .}} '
            update += 'INSERT {?s ?p ?o .} '
            update += 'USING <http://example.org/> '
            update += 'WHERE {?s ?p ?o .}'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            # execute SELECT query after UPDATE
            select_resp_after = app.post('/sparql', data=dict(query=select), headers=dict(accept="application/sparql-results+json"))

            # test select before
            obj = json.loads(select_resp_before.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 1)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://example.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # test select after
            obj = json.loads(select_resp_after.data.decode("utf-8"))
            self.assertEqual(len(obj["results"]["bindings"]), 1)
            self.assertDictEqual(obj["results"]["bindings"][0], {
                "g": {'type': 'uri', 'value': 'http://aksw.org/'},
                "s": {'type': 'uri', 'value': 'urn:x'},
                "p": {'type': 'uri', 'value': 'urn:y'},
                "o": {'type': 'uri', 'value': 'urn:z'}})

            # compare file content
            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:y> <urn:z> .\n', f.read())
            # compare file content
            with open(path.join(repo.workdir, 'graph_1.nt'), 'r') as f:
                self.assertEqual('\n', f.read())


class FileHandlingTests(unittest.TestCase):
    def testNewNamedGraph(self):
        """Test if a new graph is added to the repository.

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute Update query
        4. check filesystem for new .nt and .nt.graph file with expected content
        """
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z> .\n'
        repoContent = {'http://example.org/': content}
        with TemporaryRepositoryFactory().withGraphs(repoContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()
            filename = iri_to_name('http://aksw.org/') + '.nt'

            self.assertFalse(path.isfile(path.join(repo.workdir, filename)))
            self.assertFalse(path.isfile(path.join(repo.workdir, filename + '.graph')))

            # execute UPDATE query
            update = 'INSERT DATA { GRAPH <http://aksw.org/> { <urn:1> <urn:2> <urn:3> . } }'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:y> <urn:z> .\n', f.read())
            with open(path.join(repo.workdir, filename), 'r') as f:
                self.assertEqual('<urn:1> <urn:2> <urn:3> .\n', f.read())
            with open(path.join(repo.workdir, filename + '.graph'), 'r') as f:
                self.assertEqual('http://aksw.org/', f.read().strip())

    def testNewNamedGraphConfigfile(self):
        """Test if a new graph is added to the repository.

        1. Prepare a git repository with an empty and a non empty graph
        2. Start Quit
        3. execute Update query
        4. check filesystem and configfile content (before/after)
        """
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z> .\n'
        repoContent = {'http://example.org/': content}
        with TemporaryRepositoryFactory().withGraphs(repoContent, 'configfile') as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            with open(path.join(repo.workdir, 'config.ttl'), 'r') as f:
                configfile_before = f.read()

            # execute DELETE INSERT WHERE query
            update = 'INSERT DATA { GRAPH <http://aksw.org/> { <urn:1> <urn:2> <urn:3> . } }'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            filename = iri_to_name('http://aksw.org/') + '.nt'

            with open(path.join(repo.workdir, 'graph_0.nt'), 'r') as f:
                self.assertEqual('<urn:x> <urn:y> <urn:z> .\n', f.read())
            with open(path.join(repo.workdir, filename), 'r') as f:
                self.assertEqual('<urn:1> <urn:2> <urn:3> .\n', f.read())
            with open(path.join(repo.workdir, 'config.ttl'), 'r') as f:
                configfile_after = f.read()

            config_before = [x.strip() for x in configfile_before.split('\n')]
            config_after = [x.strip() for x in configfile_after.split('\n')]
            diff = list(set(config_after) - set(config_before))

            self.assertFalse('ns1:graphFile "' + filename + '" ;' in config_before)
            self.assertFalse('ns1:hasFormat "nt" .' in config_before)
            self.assertFalse('ns1:graphUri <http://aksw.org/> ;' in config_before)

            self.assertTrue('ns1:graphFile "' + filename + '" ;' in diff)
            self.assertTrue('ns1:hasFormat "nt" .' in diff)
            self.assertTrue('ns1:graphUri <http://aksw.org/> ;' in diff)


    def testFirstFileNameCollision(self):
        """Test if a new graph is added to the repository and if the filename collision detections works.

        1. Prepare a git repository with files that use hashed names of a graph that will be inserted
        2. Start Quit
        3. check filesystem for filenames
        4. execute Update query
        5. check filesystem for filenames
        """
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z> .\n'
        with TemporaryRepository() as repo:

            hashed_identifier = iri_to_name('http://aksw.org/')

            files = {hashed_identifier + '.nt': ('http://example.org/', content)}

            # Prepare Git Repository
            for filename, (graph_iri, content) in files.items():
                with open(path.join(repo.workdir, filename), 'w') as graph_file:
                        graph_file.write(content)

                # Set Graph URI to http://example.org/
                with open(path.join(repo.workdir, filename + '.graph'), 'w') as graph_file:
                    graph_file.write(graph_iri)

            createCommit(repo, "init")

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            commit = repo.revparse_single('HEAD')

            for entry in commit.tree:
                if entry.type == GIT_OBJ_BLOB and entry.name.endswith('.nt'):
                    self.assertTrue(entry.name in files.keys())
                else:
                    self.assertTrue(entry.name[:-6] in files.keys())

            for filename, (graph_iri, content) in files.items():
                with open(path.join(repo.workdir, filename), 'r') as f:
                    self.assertEqual(content, f.read())
                with open(path.join(repo.workdir, filename + '.graph'), 'r') as f:
                    self.assertEqual(graph_iri, f.read())

            # execute Update query
            update = 'INSERT DATA { GRAPH <http://aksw.org/> { <urn:1> <urn:2> <urn:3> . } }'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            #  add the new file we expext after Update Query
            files[hashed_identifier + '_1.nt'] = (
                'http://aksw.org/', '<urn:1> <urn:2> <urn:3> .\n')

            commit = repo.revparse_single('HEAD')

            for entry in commit.tree:
                if entry.type == GIT_OBJ_BLOB and entry.name.endswith('.nt'):
                    self.assertTrue(entry.name in files.keys())
                else:
                    self.assertTrue(entry.name[:-6] in files.keys())

            for filename, (graph_iri, content) in files.items():
                with open(path.join(repo.workdir, filename), 'r') as f:
                    self.assertEqual(content, f.read())
                with open(path.join(repo.workdir, filename + '.graph'), 'r') as f:
                    self.assertEqual(graph_iri, f.read().strip())

    def testFileNameCollision(self):
        """Test if a new graph is added to the repository.

        1. Prepare a git repository with files that use hashed names of a graph that will be inserted
        2. Start Quit
        3. check filesystem for filenames
        4. execute Update query
        5. check filesystem for filenames
        """
        # Prepate a git Repository
        content = '<urn:x> <urn:y> <urn:z> .\n'
        with TemporaryRepository() as repo:

            hashed_identifier = iri_to_name('http://aksw.org/')

            files = {
                hashed_identifier + '.nt': ('http://example.org/', content),
                hashed_identifier + '_1.nt': ('urn:graph1', '\n'),
                hashed_identifier + '_11.nt': ('urn:graph2', '\n')}

            # Prepare Git Repository
            for filename, (graph_iri, content) in files.items():
                with open(path.join(repo.workdir, filename), 'w') as graph_file:
                        graph_file.write(content)

                # Set Graph URI to http://example.org/
                with open(path.join(repo.workdir, filename + '.graph'), 'w') as graph_file:
                    graph_file.write(graph_iri)

            createCommit(repo, "init")

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            commit = repo.revparse_single('HEAD')

            for entry in commit.tree:
                if entry.type == GIT_OBJ_BLOB and entry.name.endswith('.nt'):
                    self.assertTrue(entry.name in files.keys())
                else:
                    self.assertTrue(entry.name[:-6] in files.keys())

            for filename, (graph_iri, content) in files.items():
                with open(path.join(repo.workdir, filename), 'r') as f:
                    self.assertEqual(content, f.read())
                with open(path.join(repo.workdir, filename + '.graph'), 'r') as f:
                    self.assertEqual(graph_iri, f.read().strip())

            # execute Update query
            update = 'INSERT DATA { GRAPH <http://aksw.org/> { <urn:1> <urn:2> <urn:3> . } }'
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            #  add the new file we expext after Update Query
            files[hashed_identifier + '_12.nt'] = (
                'http://aksw.org/', '<urn:1> <urn:2> <urn:3> .\n')

            commit = repo.revparse_single('HEAD')

            for entry in commit.tree:
                if entry.type == GIT_OBJ_BLOB and entry.name.endswith('.nt'):
                    self.assertTrue(entry.name in files.keys())
                else:
                    self.assertTrue(entry.name[:-6] in files.keys())

            for filename, (graph_iri, content) in files.items():
                with open(path.join(repo.workdir, filename), 'r') as f:
                    self.assertEqual(content, f.read())
                with open(path.join(repo.workdir, filename + '.graph'), 'r') as f:
                    self.assertEqual(graph_iri, f.read().strip())

    def testDeleteWithWhitespaceFile(self):
        """Test deleting data from a nt-file with additional whitespace in serialization.

        1. Prepare a git repository with one graph
        2. Start Quit
        3. compare File content
        4. execute DELETE DATA query
        5. compare File content
        """
        # Prepate a git Repository
        graphContent = "<urn:x>  <urn:y>   <urn:z>   . "
        with TemporaryRepositoryFactory().withGraph("http://example.org/", graphContent) as repo:

            # Start Quit
            args = quitApp.getDefaults()
            args['targetdir'] = repo.workdir
            app = create_app(args).test_client()

            with open(path.join(repo.workdir, 'graph.nt'), 'r') as f:
                self.assertEqual(graphContent, f.read())

            # execute DELETE query
            update = "DELETE DATA {graph <http://example.org/> {<urn:x> <urn:y> <urn:z> .}};"
            app.post('/sparql',
                     content_type="application/sparql-update",
                     data=update)

            with open(path.join(repo.workdir, 'graph.nt'), 'r') as f:
                self.assertEqual('\n', f.read())


if __name__ == '__main__':
    unittest.main()
