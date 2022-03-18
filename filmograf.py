import argparse
import concurrent.futures
import json
import logging as log
from imdb import Cinemagoer
from neo4j import GraphDatabase
from os import path
from typing import Set

NEO4J_USERNAME = 'guest'
NEO4J_PASSWORD = 'guest'
NEO4J_URI = 'neo4j+s://4169d4dc.databases.neo4j.io'

FILM_LIMIT = 250 # MAX 250
CAST_LIMIT = 25

VERBOSE = False

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='count', help='Toggle verbose output (-v for INFO, -vv for INFO with imdbpy logs, -vvv for DEBUG)')
parser.add_argument('-f', '--film-limit', help='Number of films to collect data on (max 250)')
parser.add_argument('-c', '--cast-limit', help='Number of actors for each film to collect data on')
args = parser.parse_args()

if args.verbose:
    VERBOSE = True
    if args.verbose <= 1:
        log.basicConfig(level=log.INFO)
        log.getLogger('imdbpy').setLevel(log.FATAL)
    elif args.verbose <= 2:
        log.basicConfig(level=log.INFO)
        log.getLogger('imdbpy').setLevel(log.INFO)
        log.getLogger('imdbpy.parser.http.piculet').setLevel(log.FATAL)
    else:
        log.basicConfig(level=log.DEBUG)

if args.film_limit:
    temp = FILM_LIMIT
    try:
        FILM_LIMIT = int(args.film_limit)
    except Exception:
        FILM_LIMIT = temp

if args.cast_limit:
    temp = CAST_LIMIT
    try:
        CAST_LIMIT = int(args.cast_limit)
    except Exception:
        CAST_LIMIT = temp

if VERBOSE: from tqdm import tqdm


class SetEncoder(json.JSONEncoder):
    '''JSON encoder class for converting classes with sets.'''
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return obj.__dict__


class FilmografDataEncoder(SetEncoder):
    '''JSON encoder class for the FilmografData class.'''
    def default(self, obj):
        if isinstance(obj, Neo4jConnection) or isinstance(obj, tqdm):
            return
        return super().default(obj)


class Film:
    id: str
    title: str
    cast: Set[str]

    def __init__(self, id, fromJSON=False, title=None, cast=None) -> None:
        if fromJSON:
            self.id = id
            self.title = title
            self.cast = cast
            return
        film = Cinemagoer().get_movie(id)
        self.id    = id
        self.title = film['title']
        self.cast  = [actor.getID() for actor in film['cast'][:CAST_LIMIT]]

    def toJSON(self) -> str:
        '''Converts the Film object into a JSON formatted string.'''
        return json.dumps(self, cls=SetEncoder, sort_keys=True, indent=4)

    def fromJSON(json_dict) -> None:
        '''Creates a new Film object from data from a JSON dictionary.'''
        return Film(fromJSON=True, id=json_dict['id'], title=json_dict['title'], cast=json_dict['cast'])


class Actor:
    id: str
    name: str
    filmography: Set[str]
    
    def __init__(self, id:str, films:Set[Film]=set(), fromJSON:bool=False, name:str=None, filmography:Set[str]=None) -> None:
        if fromJSON:
            self.id = id
            self.name = name
            self.filmography = set(filmography)
            return
        person = Cinemagoer().get_person(id)
        self.id   = id
        self.name = person['name']
        filmography = []
        if 'actor'   in person['filmography']: filmography += person['filmography']['actor']
        if 'actress' in person['filmography']: filmography += person['filmography']['actress']
        if 'self'    in person['filmography']: filmography += person['filmography']['self']
        filmography = [film.getID() for film in filmography]
        self.filmography = set(filmography) & set([film.id for film in films])

    def toJSON(self) -> str:
        '''Converts the Film object into a JSON formatted string.'''
        return json.dumps(self, cls=SetEncoder, sort_keys=True, indent=4)

    def fromJSON(json_dict) -> None:
        '''Creates a new Actor object from data from a JSON dictionary.'''
        return Actor(fromJSON=True, id=json_dict['id'], name=json_dict['name'], filmography=json_dict['filmography'])


class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri    = uri
        self.__user   = user
        self.__pwd    = pwd

    def query(self, query, params=None):
        session, response = None, None
        try:
            driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
            session = driver.session()
            response = list(session.run(query, params))
        except Exception as e:
            log.error(f'Failed to execute query: {e}')
        finally:
            if session is not None:
                session.close()
            driver.close()
            return response


class FilmografData:
    films:  Set[Film]
    actors: Set[Actor]
    n4j:    Neo4jConnection

    def __init__(self) -> None:
        self.films  = set()
        self.actors = set()
        if path.isfile('snapshot.json'):
            self.load_snapshot('snapshot.json')
        else:
            self.pull_data()
        self.populate_database()
                            

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

        merged_casts = set([id for film in self.films for id in film.cast])
        log.info(f'Pulling actor data for {len(merged_casts)} actors')
        if VERBOSE: self.progressbar = tqdm(total=len(merged_casts), position=0, leave=False)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for id in merged_casts:
                executor.submit(self.pull_actor_data, id)
        if VERBOSE: self.progressbar.clear()

        # Some actors are credited for a role on a film's page, but not on the actor's page.
        # This leads to their filmography being empty and them being isolated nodes in the databes.
        # To avoid this, these actors are weeded out before the database is populated.
        for actor in [actor for actor in self.actors if len(actor.filmography) == 0]:
            log.info(f'Removing {actor.name} (isolated node)')
            self.actors.remove(actor)

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

        log.info('Adding films to neo4j database')
        if VERBOSE: self.progressbar = tqdm(total=len(self.films), position=0, leave=False)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for film in self.films:
                executor.submit(self.add_film_to_database, film)
        if VERBOSE: self.progressbar.clear()
        
        log.info('Adding actors to neo4j database')
        if VERBOSE: self.progressbar = tqdm(total=len(self.actors), position=0, leave=False)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for actor in self.actors:
                executor.submit(self.add_actor_to_database, actor)
        if VERBOSE: self.progressbar.clear()


    def add_film_to_database(self, film:Film) -> None:
            self.n4j.query(f'CREATE (f:Film {{id: "{film.id}", title:"{film.title}", imdb:"httpsL//www.imdb.com/title/tt{film.id}"}})')
            if VERBOSE: self.progressbar.update()


    def add_actor_to_database(self, actor:Actor) -> None:
            self.n4j.query(f'CREATE (a:Actor {{id:"{actor.id}", name:"{actor.name}", imdb:"https://www.imdb.com/name/nm{actor.id}"}})')
            for film_id in actor.filmography:
                self.n4j.query(f'MATCH (actor:Actor {{id:"{actor.id}"}}), (film:Film {{id:"{film_id}"}}) MERGE (actor)-[:STARRED_IN]->(film)')
            if VERBOSE: self.progressbar.update()


    def get_actor(self, id:str=None, name:str=None) -> Actor:
        '''
        Returns an Actor object with matching name or ID, if one exists in the databank.\n
        If an ID is provided, name check is skipped.\n
        Returns None if no ID or name is given, or if there are no matching Actors in the databank.
        '''
        filtered_list = []
        if   id:   filtered_list = [actor for actor in self.actors if actor.id == id]
        elif name: filtered_list = [actor for actor in self.actors if actor.name == name]
        if not filtered_list:
            return None
        return filtered_list[0]


    def get_film(self, id:str=None, title:str=None) -> Film:
        '''
        Returns a Film object with matching title or id, if one exists in the databank.\n
        If an ID is provided, title check is skipped.
        Returns None if no ID or title is given, or if there are no matching Films in the databank.
        '''
        filtered_list = []
        if   id:    filtered_list = [film for film in self.films if film.id == id]
        elif title: filtered_list = [film for film in self.films if film.title == title]
        if not filtered_list:
            return None
        return filtered_list[0]


    def toJSON(self) -> str:
        '''Converts the databank to a JSON formatted string.'''
        return json.dumps(self, cls=FilmografDataEncoder, sort_keys=True, indent=4)


db = FilmografData()

log.info(f' Number of films:  {len(db.films)}')
log.info(f' Number of actors: {len([actor for actor in db.actors if len(actor.filmography)>0])}')

# print(n4j.query('MATCH (root:Actor {name:"Emma Stone"})\
                #  CALL apoc.path.spanningTree(root, { maxLevel: 1 })\
                #  YIELD path\
                #  RETURN path'))