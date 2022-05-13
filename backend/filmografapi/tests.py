from .views import *
from django.test import SimpleTestCase
from django.test.client import RequestFactory
from django.http import JsonResponse
from typing import Set
import json
import logging

FACTORY = RequestFactory()

def getValue(response:JsonResponse, key:str):
    try:
        return json.loads(response.content)[key]
    except json.JSONDecodeError:
        logging.error('JsonResponse was not in correct format.')
    except KeyError:
        logging.error(f'Invalid key: {key}')


class TestNodeExists(SimpleTestCase):
    def setUp(self):
        self.shortened       = 'hanks'
        self.lowercaseName   = 'tom hanks'
        self.uppercaseName   = 'TOM HANKS'
        self.mixedcaseName   = 'tOm HaNKs'
        self.extraWhitespace = 't   o m    h       a n    k s'
        self.filmTitle       = 'green mile'
        self.numericId       = '0000158'
        self.alphanumericId  = 'nm0000158'
        self.uriWithSlash    = 'https://www.imdb.com/name/nm0000158/'
        self.uriWithoutSlash = 'https://www.imdb.com/name/nm0000158'

    def makeRequest(self, keyword:str):
        return FACTORY.get(f'exists?search={keyword}')

    def testExists(self):
        self.assertTrue(getValue(nodeExists(self.makeRequest(self.shortened)), 'nodeExists'))
        self.assertTrue(getValue(nodeExists(self.makeRequest(self.lowercaseName)), 'nodeExists'))
        self.assertTrue(getValue(nodeExists(self.makeRequest(self.uppercaseName)), 'nodeExists'))
        self.assertTrue(getValue(nodeExists(self.makeRequest(self.mixedcaseName)), 'nodeExists'))
        self.assertTrue(getValue(nodeExists(self.makeRequest(self.extraWhitespace)), 'nodeExists'))
        self.assertTrue(getValue(nodeExists(self.makeRequest(self.filmTitle)), 'nodeExists'))
        self.assertTrue(getValue(nodeExists(self.makeRequest(self.numericId)), 'nodeExists'))
        self.assertTrue(getValue(nodeExists(self.makeRequest(self.alphanumericId)), 'nodeExists'))
        self.assertTrue(getValue(nodeExists(self.makeRequest(self.uriWithSlash)), 'nodeExists'))
        self.assertTrue(getValue(nodeExists(self.makeRequest(self.uriWithoutSlash)), 'nodeExists'))


class TestGetDistance(SimpleTestCase):
    def setUp(self):
        self.sameNode = ('tom hanks', 'TOM HANKS')
        self.halfStep = ('tom hanks', 'green mile')
        self.oneStep  = ('tom hanks', 'dicaprio')
        self.twoStep  = ('tom hanks', 'jessica chastain')
        self.invalid  = ('tom hanks', 'hitler')
    
    def makeRequest(self, keywords):
        return FACTORY.get(f'distance?left={keywords[0]}&right={keywords[1]}')

    def testDistance(self):
        self.assertEqual(
            getValue(getDistance(self.makeRequest(self.sameNode)), 'distance'),
            0
        )
        self.assertEqual(
            getValue(getDistance(self.makeRequest(self.halfStep)), 'distance'),
            0.5
        )
        self.assertEqual(
            getValue(getDistance(self.makeRequest(self.oneStep)), 'distance'),
            1
        )
        self.assertEqual(
            getValue(getDistance(self.makeRequest(self.twoStep)), 'distance'),
            2
        )
        self.assertEqual(
            getValue(getDistance(self.makeRequest(self.invalid)), 'distance'),
            '-'
        )


class TestGetPath(SimpleTestCase):
    def setUp(self):
        self.sameNode = ('tom hanks', 'TOM HANKS')
        self.halfStep = ('tom hanks', 'green mile')
        self.oneStep  = ('tom hanks', 'dicaprio')
        self.twoStep  = ('tom hanks', 'jessica chastain')
        self.invalid  = ('tom hanks', 'hitler')
    
    def makeRequest(self, keywords:Set[str]):
        return FACTORY.get(f'path?left={keywords[0]}&right={keywords[1]}')

    def testPath(self):
        response = getPath(self.makeRequest(self.sameNode))
        self.assertEqual(
            len(getValue(response, 'nodes')),
            1
        )
        self.assertEqual(
            len(getValue(response, 'edges')),
            0
        )

        response = getPath(self.makeRequest(self.halfStep))
        self.assertEqual(
            len(getValue(response, 'nodes')),
            2
        )
        self.assertEqual(
            len(getValue(response, 'edges')),
            1
        )

        response = getPath(self.makeRequest(self.oneStep))
        self.assertEqual(
            len(getValue(response, 'nodes')),
            3
        )
        self.assertEqual(
            len(getValue(response, 'edges')),
            2
        )

        response = getPath(self.makeRequest(self.twoStep))
        self.assertEqual(
            len(getValue(response, 'nodes')),
            5
        )
        self.assertEqual(
            len(getValue(response, 'edges')),
            4
        )

        response = getPath(self.makeRequest(self.invalid))
        self.assertEqual(
            len(getValue(response, 'nodes')),
            1
        )
        self.assertEqual(
            len(getValue(response, 'edges')),
            0
        )
        node = getValue(response, 'nodes')[0]
        self.assertEqual(
            node.keys(),
            set(['hidden'])
        )
        self.assertTrue(node['hidden'])


class TestGetGraph(SimpleTestCase):
    def setUp(self):
        self.actor = ('tom hanks', 0)
        self.film  = ('green mile', 0)
        self.negative = ('tom hanks', -1)

    def makeRequest(self, keywords:Set[str]):
        return FACTORY.get(f'graph?root={keywords[0]}&depth={keywords[1]}')

    def testGraph(self):
        response = getGraph(self.makeRequest(self.actor))
        self.assertEqual(
            len(getValue(response, 'nodes')),
            1
        )
        self.assertEqual(
            len(getValue(response, 'edges')),
            0
        )
        node = getValue(response, 'nodes')[0]
        self.assertEqual(
            node.keys(),
            set(['group', 'id', 'label', 'image', 'poster', 'uri'])
        )
        self.assertEqual(
            node['group'],
            'actors'
        )

        response = getGraph(self.makeRequest(self.film))
        self.assertEqual(
            len(getValue(response, 'nodes')),
            1
        )
        self.assertEqual(
            len(getValue(response, 'edges')),
            0
        )
        node = getValue(response, 'nodes')[0]
        self.assertEqual(
            node.keys(),
            set(['group', 'id', 'label', 'image', 'poster', 'uri'])
        )
        self.assertEqual(
            node['group'],
            'films'
        )

        response = getGraph(self.makeRequest(self.negative))
        self.assertEqual(
            len(getValue(response, 'nodes')),
            1
        )
        self.assertEqual(
            len(getValue(response, 'edges')),
            0
        )