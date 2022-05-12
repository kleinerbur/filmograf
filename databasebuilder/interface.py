import argparse
import concurrent.futures
import json
import logging as log
from imdb import Cinemagoer
from neo4j import GraphDatabase
from neo4j.exceptions import ConstraintError
from os import path
from typing import Set
from tqdm import tqdm

NEO4J_USERNAME = 'guest'
NEO4J_PASSWORD = 'guest'
NEO4J_URI = 'neo4j+s://4169d4dc.databases.neo4j.io'

FILM_LIMIT = 250 # MAX 250
CAST_LIMIT = 25

VERBOSE = False


class SetEncoder(json.JSONEncoder):
    '''JSON encoder class for converting classes with sets.'''
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return obj.__dict__


class DatabaseBuilderEncoder(SetEncoder):
    '''JSON encoder class for the FilmografData class.'''
    def default(self, obj):
        if isinstance(obj, Neo4jConnection) or isinstance(obj, tqdm):
            return
        return super().default(obj)


class Film:
    id: str
    title: str
    image: str
    cast: Set[str]

    def __init__(self, id:str, fromJSON:bool=False, title:str=None, cast:Set[tuple]=None, image:str=None, poster:str=None) -> None:
        if fromJSON:
            self.id = id
            self.title = title
            self.cast = cast
            self.image = image
            self.poster = poster
            return
        film = Cinemagoer().get_movie(id)
        self.id    = id
        self.title = film['title']
        self.image = film['cover url']
        self.poster = film['full-size cover url']
        self.cast = set()
        for actor in film['cast'][:CAST_LIMIT]:
            try:
                rolename = actor.currentRole['name']
            except: # actor has multiple credited roles
                try:
                    rolename = actor.currentRole[0]['name']
                except: # actor's role has no name
                    rolename = ''
            self.cast.add((actor.getID(), rolename))
        
    def toJSON(self) -> str:
        '''Converts the Film object into a JSON formatted string.'''
        return json.dumps(self, cls=SetEncoder, sort_keys=True, indent=4)

    def fromJSON(json_dict) -> None:
        '''Creates a new Film object from data from a JSON dictionary.'''
        return Film(fromJSON=True, id=json_dict['id'], title=json_dict['title'], cast=json_dict['cast'], image=json_dict['image'], poster=json_dict['poster'])


class Actor:
    id: str
    name: str
    image: str
    
    def __init__(self, id:str, films:Set[Film]=set(), fromJSON:bool=False, name:str=None, image:str=None, poster:str=None) -> None:
        if fromJSON:
            self.id = id
            self.name = name
            self.image = image
            self.poster = poster
            return
        person = Cinemagoer().get_person(id)
        self.id   = id
        self.name = person['name']

        try:
            self.image = person['headshot']
            self.poster = person['full-size headshot']
        except Exception:
            self.image = "https://cdn-icons-png.flaticon.com/128/1077/1077114.png"
            self.poster = "https://t4.ftcdn.net/jpg/00/64/67/63/360_F_64676383_LdbmhiNM6Ypzb3FM4PPuFP9rHe7ri8Ju.jpg"
        
    def toJSON(self) -> str:
        '''Converts the Film object into a JSON formatted string.'''
        return json.dumps(self, cls=SetEncoder, sort_keys=True, indent=4)

    def fromJSON(json_dict) -> None:
        '''Creates a new Actor object from data from a JSON dictionary.'''
        return Actor(fromJSON=True, id=json_dict['id'], name=json_dict['name'], image=json_dict['image'])


class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.uri  = uri
        self.user = user
        self.pwd  = pwd

    def query(self, query, params=None):
        session, response = None, None
        try:
            driver = GraphDatabase.driver(self.uri, auth=(self.user, self.pwd))
            session = driver.session()
            response = list(session.run(query, params))
        except ConstraintError as e:
            log.debug(f'Query ran into constraint error, skipping: {e}')
        except Exception as e:
            log.error(f'Failed to execute query: {e}')
        finally:
            if session is not None:
                session.close()
            driver.close()
            return response


class DatabaseBuilder:
    films:  Set[Film]
    actors: Set[Actor]
    n4j:    Neo4jConnection

    def __init__(self, force:bool=False) -> None:
        self.films  = set()
        self.actors = set()
        if not force and path.isfile('snapshot.json'):
            self.load_snapshot('snapshot.json')
        else:
            self.pull_data()
                            

    def load_snapshot(self, path:str) -> None:
        log.info('Loading JSON snapshot')
        with open(path) as jsonfile:
            data = json.load(jsonfile)
            for actor in data['actors']:
                self.actors.add(json.loads(json.dumps(actor), object_hook=Actor.fromJSON))
            for film in data['films']:
                self.films.add(json.loads(json.dumps(film), object_hook=Film.fromJSON))


    def pull_data(self) -> None:
        top_films = Cinemagoer().get_top250_movies()[:FILM_LIMIT]
        
        log.info(f'Pulling film data for {FILM_LIMIT} films (max 250)')
        if VERBOSE: self.progressbar = tqdm(total=FILM_LIMIT, position=0, leave=False)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for film in top_films:
                executor.submit(self.pull_film_data, film.getID())
        if VERBOSE: self.progressbar.clear()

        merged_casts = set([id for film in self.films for (id, role) in film.cast])
        log.info(f'Pulling actor data for {len(merged_casts)} actors')
        if VERBOSE: self.progressbar = tqdm(total=len(merged_casts), position=0, leave=False)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for id in merged_casts:
                executor.submit(self.pull_actor_data, id)
        if VERBOSE: self.progressbar.clear()

        log.info('Saving JSON snapshot')
        with open('snapshot.json', 'w') as jsonfile:
            jsonfile.write(self.toJSON())


    def pull_film_data(self, id:str) -> None:
        '''Looks up a film based on its ID, creates a Film object from the data and adds it to the databank.'''
        self.films.add(Film(id))
        if VERBOSE: self.progressbar.update()


    def pull_actor_data(self, id:str) -> None:
        '''Looks up an actor based on their ID, creates an Actor object from the data and adds it to the API's databank.'''
        self.actors.add(Actor(id, films=self.films))
        if VERBOSE: self.progressbar.update()


    def populate_database(self) -> None:
        self.n4j = Neo4jConnection(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)

        log.info('Adding actors to neo4j database')
        if VERBOSE: self.progressbar = tqdm(total=len(self.actors), position=0, leave=False)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for actor in self.actors:
                executor.submit(self.add_actor_to_database, actor)
        if VERBOSE: self.progressbar.clear()

        log.info('Adding films to neo4j database')
        if VERBOSE: self.progressbar = tqdm(total=len(self.films), position=0, leave=False)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for film in self.films:
                executor.submit(self.add_film_to_database, film)
        if VERBOSE: self.progressbar.clear()

        log.info('Removing isolated nodes')
        self.n4j.query(f'MATCH (n) WHERE NOT (n)--() DETACH DELETE n')
        log.info('Done')


    def add_actor_to_database(self, actor:Actor) -> None:
        try:
            self.n4j.query(f'''
            CREATE (a:Actor {{
                group:"actors", 
                imdb_id:"{actor.id}", 
                name:"{actor.name}", 
                image:"{actor.image}", 
                poster:"{actor.poster}", 
                imdb_uri:"https://www.imdb.com/name/nm{actor.id}"}})
            ''')
        except ConstraintError:
            log.error(f'Actor with ID {actor.id} ({actor.name}) already exists, skipping')
        if VERBOSE: self.progressbar.update()


    def add_film_to_database(self, film:Film) -> None:
        try:
            self.n4j.query(f'''
            CREATE (f:Film {{
                group:"films", 
                imdb_id:"{film.id}", 
                title:"{film.title}", 
                image:"{film.image}", 
                poster:"{film.poster}", 
                imdb_uri:"https://www.imdb.com/title/tt{film.id}"}})
            ''')
            for (actor_id, role) in film.cast:
                self.n4j.query(f'''
                MATCH (actor:Actor {{imdb_id:"{actor_id}"}}), (film:Film {{imdb_id:"{film.id}"}}) 
                MERGE (actor)-[:STARRED_IN {{role: "{role}"}}]->(film)
                ''')
        except ConstraintError:
            log.error(f'Film with ID {film.id} ("{film.title}") already exists, skipping')
        if VERBOSE: self.progressbar.update()
        

    def toJSON(self) -> str:
        '''Converts the databank to a JSON formatted string.'''
        return json.dumps(self, cls=DatabaseBuilderEncoder, sort_keys=True, indent=4)


class DatabaseInterface:
    n4j: Neo4jConnection

    def __init__(self):
        self.n4j = Neo4jConnection(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    
    def __compare_against_actor(self, alias:str, keyword:str) -> str:
        return f'''toUpper({alias}.name) =~ toUpper(".*{keyword}.*") OR 
                   toUpper({alias}.id)   =~ toUpper(".*{keyword}.*") OR 
                   toUpper({alias}.imdb) =~ toUpper(".*{keyword}.*")'''
    
    def __compare_against_film(self, alias:str, keyword:str) -> str:
        return f'''toUpper({alias}.title) =~ toUpper(".*{keyword}.*") OR 
                   toUpper({alias}.id)    =~ toUpper(".*{keyword}.*") OR 
                   toUpper({alias}.imdb)  =~ toUpper(".*{keyword}.*")'''

    def actor_exists(self, keyword:str) -> bool:
        count = self.n4j.query(f'''
            MATCH (n:Actor)
            WHERE {self.__compare_against_actor('n', keyword)}
            RETURN count(n) AS count
        ''')[0].data()['count']
        return count > 0
    
    def film_exists(self, keyword:str) -> bool:
        count = self.n4j.query(f'''
            MATCH (n:Film)
            WHERE {self.__compare_against_film('n', keyword)}
            RETURN count(n) AS count
        ''')[0].data()['count']
        return count > 0
    
    def node_exists(self, keyword:str) -> bool:
        return self.actor_exists(keyword) or self.film_exists(keyword)

    def get_distance(self, left:str, right:str) -> str:
        assert self.node_exists(left),  f'No node in the database matches the given keyword: {left}'
        assert self.node_exists(right), f'No node in the database matches the given keyword: {right}'
        return json.dumps(self.n4j.query(f'''
            CALL {{
                MATCH (left)
                WHERE {self.__compare_against_actor('left', left)}
                RETURN left LIMIT 1
            }}
            CALL {{
                MATCH (right) 
                WHERE {self.__compare_against_actor('right', right)}
                RETURN right LIMIT 1
            }}
            MATCH path=shortestPath((left)-[*]-(right))
            RETURN length(path) AS distance''')[0].data())

    def get_path(self, left:str, right:str) -> str:
        assert self.node_exists(left),  f'No node in the database matches the given keyword: {left}'
        assert self.node_exists(right), f'No node in the database matches the given keyword: {right}'
        return json.dumps(self.n4j.query(f'''
            CALL {{
                MATCH (left)
                WHERE {self.__compare_against_actor('left', left)}
                RETURN left LIMIT 1
            }}
            CALL {{
                MATCH (right)
                WHERE {self.__compare_against_actor('right', right)}
                RETURN right LIMIT 1
            }}
            MATCH path=shortestPath((left)-[*]-(right))
            RETURN path''')[0].data())
            
    def get_graph(self, root:str, depth:int) -> str:
        assert self.node_exists(root), f'No node in the database matches the given keyword: {root}'
        # Odd distances are films, even distances are costars,
        # so depth has to be doubled
        return json.dumps([result.data() for result in self.n4j.query(f'''
            MATCH (root:Actor)
            WHERE {self.__compare_against_actor('root', root)}
            CALL apoc.path.spanningTree(root, {{ maxLevel: {depth * 2} }})
            YIELD path
            RETURN path
        ''')]) # the graph is returned as a list of paths

    def cypher(self, query:str) -> str:
        return [result.data() for result in self.n4j.query(query)]


class Parser:
    parser: argparse.ArgumentParser
    args: argparse.Namespace

    def __init__(self):
        global NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-v', '--verbose', action='count', help='Toggle verbose output (-v for INFO, -vv for INFO with imdbpy logs, -vvv for DEBUG)')
        self.parser.add_argument('-b', '--build-database', action='store_true', help='Creates a DatabaseBuilder object either by loading an existing snapshot or pulling data from IMDb, then populates the Neo4j database.')
        self.parser.add_argument('-f', '--film-limit', metavar='<limit>', type=int, help='Number of films to collect data on (max 250)')
        self.parser.add_argument('-c', '--cast-limit', metavar='<limit>', type=int, help='Number of actors for each film to collect data on')
        self.parser.add_argument('-uri', metavar='<uri>', help='Neo4j database URI')
        self.parser.add_argument('-u', '--user', metavar='<username>', help='Neo4j username')
        self.parser.add_argument('-pw', '--password', metavar='<password>', help='Neo4j password')
        self.parser.add_argument('-d', '--distance', nargs=2, metavar=('<name|IMDb ID|IMDb URL> <name|IMDb ID|IMDb URL>'), help='Returns the distance between two nodes')
        self.parser.add_argument('-p', '--path', nargs=2, metavar=('<name|IMDb ID|IMDb URL> <name|IMDb ID|IMDb URL>'), help='Returns the shortest path between two nodes')
        self.parser.add_argument('-g', '--graph', nargs=2, metavar=('<name|IMDb ID|IMDb URL> <depth>'), help='Returns a graph from the given root node up to the given depth')
        self.parser.add_argument('-e', '--exists', metavar='<name|title|IMDb ID|IMDb URL>', help='Checks if a node with the given property exists in the database.')
        self.parser.add_argument('--force', action='store_true', help='Force pulling of new data even if a JSON snapshot is present.')
        self.parser.add_argument('--cypher', metavar='<query>', help='Run a cypher query on the Neo4j database.')
        self.args = self.parser.parse_args()

        # set global variables
        if self.args.uri:      NEO4J_URI      = self.args.uri
        if self.args.user:     NEO4J_USERNAME = self.args.user
        if self.args.password: NEO4J_PASSWORD = self.args.password

        # handle more complex flags
        if self.args.verbose:        self.__handle_verbose()
        if self.args.build_database: self.__handle_build_database()
        if self.args.distance:       self.__handle_distance()
        if self.args.path:           self.__handle_path()
        if self.args.graph:          self.__handle_graph()
        if self.args.exists:         self.__handle_exists()
        if self.args.cypher:         self.__handle_cypher()

    def __handle_verbose(self):
        global VERBOSE
        VERBOSE = True
        if self.args.verbose <= 1:
            log.basicConfig(level=log.INFO)
            log.getLogger('imdbpy').setLevel(log.FATAL)
        elif self.args.verbose <= 2:
            log.basicConfig(level=log.INFO)
            log.getLogger('imdbpy').setLevel(log.INFO)
            log.getLogger('imdbpy.parser.http.piculet').setLevel(log.FATAL)
        else:
            log.basicConfig(level=log.DEBUG)

    def __handle_build_database(self):
        global FILM_LIMIT, CAST_LIMIT
        if self.args.film_limit: FILM_LIMIT = int(self.args.film_limit)
        if self.args.cast_limit: CAST_LIMIT = int(self.args.cast_limit)
        DatabaseBuilder(self.args.force).populate_database()

    def __handle_distance(self):
        left  = self.args.distance[0]
        right = self.args.distance[1]
        try:
            print(DatabaseInterface().get_distance(left, right))
        except AssertionError as e:
            log.error(e)

    def __handle_path(self):
        left  = self.args.path[0]
        right = self.args.path[1]
        try:
            print(DatabaseInterface().get_path(left, right))
        except AssertionError as e:
            log.error(e)

    def __handle_graph(self):
        root  = self.args.graph[0]
        try:
            depth = int(self.args.graph[1])
            try:
                print(DatabaseInterface().get_graph(root, depth))
            except AssertionError as e:
                log.error(e)
        except TypeError as e:
            log.error(e)

    def __handle_exists(self):
        param = self.args.exists
        print(DatabaseInterface().node_exists(param))

    def __handle_cypher(self):
        print(DatabaseInterface().cypher(self.args.cypher))

Parser()