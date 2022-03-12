from progressbar import ProgressBar, streams
from imdb import Cinemagoer, IMDbDataAccessError
from socket import timeout
from os import path
from typing import Any, List, Set, Dict, Tuple

import concurrent.futures
import json

LIMIT = 100
PROGRESSBAR = None

class Encoder(json.JSONEncoder):
    """JSON encoder class to help with converting sets."""
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return obj.__dict__


class Film:
    id: str
    title: str
    cast: Set[str]

    def __init__(self, id, fromJSON=False, title=None, cast=None):
        if fromJSON:
            self.id = id
            self.title = title
            self.cast = cast
            return
        film = Cinemagoer().get_movie(id)
        self.id    = id
        self.title = film['title']
        self.cast  = [actor.getID() for actor in film['cast']]

    def __str__(self):
        return f"[FILM] Title: {self.title}; ID: {self.id}; Size of cast: {len(self.cast)}"
    
    def __repr__(self):
        return str(self)

    def toJSON(self):
        """Converts the Film object into a JSON formatted string."""
        return json.dumps(self, cls=Encoder, sort_keys=True, indent=4)

    def fromJSON(json_dict):
        """Creates a new Film object from data from a JSON dictionary."""
        return Film(fromJSON=True, id=json_dict['id'], title=json_dict['title'], cast=json_dict['cast'])


class Actor:
    id: str
    name: str
    filmography: Set[str]
    
    def __init__(self, id:str, films:Set[Film]=set(), fromJSON:bool=False, name:str=None, filmography:Set[str]=None):
        if fromJSON:
            self.id = id
            self.name = name
            self.filmography = set(filmography)
            return
        person = Cinemagoer().get_person(id)
        self.id   = id
        self.name = person['name']
        filmography = person['filmography']
        if   'actor'   in filmography: filmography = filmography['actor']
        elif 'actress' in filmography: filmography = filmography['actress']
        else:                          filmography = filmography['self']
        filmography = [film.getID() for film in filmography]
        self.filmography = set(filmography) & set([film.id for film in films])

    def __str__(self):
        return f"[ACTOR] Name: {self.name}; ID: {self.id}; # of films: {len(self.filmography)}"

    def __repr__(self):
        return str(self)

    def toJSON(self) -> str:
        """Converts the Film object into a JSON formatted string."""
        return json.dumps(self, cls=Encoder, sort_keys=True, indent=4)

    def fromJSON(json_dict):
        """Creates a new Actor object from data from a JSON dictionary."""
        return Actor(fromJSON=True, id=json_dict['id'], name=json_dict['name'], filmography=json_dict['filmography'])

    def get_intersection(self, other) -> Set[str]:
        """Returns a set of films both actors are credited on."""
        if self.id == other.id:
            return set()
        return set.intersection(self.filmography, other.filmography)
    
    def has_credit_with(self, other) -> bool:
        """Returns True if the two actors worked together on at least one film."""
        return len(self.get_intersection(other)) > 0


def process_film(id:str, dataset:Set[Film]):
    """
    Helper function that looks up a film based on its ID, creates a Film object from the data and adds it to the API's databank.
    """
    film = Film(id)
    dataset.add(film)
    PROGRESSBAR.update(len(dataset))

def process_actor(id:str, films:Set[Film], dataset:Set[Actor]):
    """
    Helper function that looks up an actor based on their ID, creates an Actor object from the data and adds it to the API's databank.
    """
    actor = Actor(id, films)
    dataset.add(actor)
    PROGRESSBAR.update(len(dataset))


class Graph:
    root: Actor
    depth: int
    graph: Dict[str, List[Tuple[Actor, List[Film]]]]
    nodes: List[Actor]
    
    def __init__(self, root:Actor, depth:int) -> None:
        self.root = root
        self.depth = depth
        self.graph = {root.id: []}
        self.nodes = [root]
    
    def get_children(self, id:str) -> List[Actor]:
        """
        Returns all the Actor objects the actor with the given ID has a direct connection with.
        """
        if id not in self.graph: return []
        return [record[0] for record in self.graph[id]]

    def add_node(self, actor:Actor, films:Set[Film]) -> None:
        """
        Inserts the given Actor into the Graph.
        """
        if actor.id not in self.graph:
            self.graph[actor.id] = []
            self.nodes.append(actor)
        for id in self.graph:
            if id != actor.id and actor not in self.get_children(id):
                other = [node for node in self.nodes if node.id == id][0]
                intersection = [film for film in films if film.id in actor.get_intersection(other)]
                self.graph[id].append((actor, intersection))
                self.graph[actor.id].append((other, intersection))

    def toJSON(self) -> str:
        """Converts the Graph into a JSON formatted string."""
        return json.dumps(self, cls=Encoder, sort_keys=True, indent=4)


class FilmografAPI:
    films:  Set[Film]
    actors: Set[Actor]

    def __init__(self):
        global PROGRESSBAR
        self.films  = set()
        self.actors = set()

        if path.isfile('FilmografAPI.json'):
            with open('FilmografAPI.json') as jsonfile:
                data = json.load(jsonfile)
                for actor in data['actors']:
                    self.actors.add(json.loads(json.dumps(actor), object_hook=Actor.fromJSON))
                for film in data['films']:
                    self.films.add(json.loads(json.dumps(film), object_hook=Film.fromJSON))
                return
        
        top_films = Cinemagoer().get_top250_movies()[0:LIMIT]
        PROGRESSBAR = ProgressBar(max_value=LIMIT)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for film in top_films:
                executor.submit(process_film, film.getID(), self.films)

        merged_cast = set([id for film in self.films for id in film.cast])
        PROGRESSBAR = ProgressBar(max_value=len(merged_cast))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for id in merged_cast:
                executor.submit(process_actor, id, self.films, self.actors)

        with open('FilmografAPI.json', 'w') as jsonfile:
            jsonfile.write(self.toJSON())

    def get_actor(self, id:str=None, name:str=None) -> Actor:
        """
        Returns an Actor object with matching name or ID, if one exists in the databank.\n
        If an ID is provided, name check is skipped.\n
        Returns None if no ID or name is given, or if there are no matching Actors in the databank.
        """
        filtered_list = []
        if   id:   filtered_list = [actor for actor in self.actors if actor.id == id]
        elif name: filtered_list = [actor for actor in self.actors if actor.name == name]
        if not filtered_list:
            return None
        return filtered_list[0]

    def get_film(self, id:str, title:str=None) -> Film:
        """
        Returns a Film object with matching title or id, if one exists in the databank.\n
        If an ID is provided, title check is skipped.
        Returns None if no ID or title is given, or if there are no matching Films in the databank.
        """
        filtered_list = []
        if   id:    filtered_list = [film for film in self.films if film.id == id]
        elif title: filtered_list = [film for film in self.films if film.title == title]
        if not filtered_list:
            return None
        return filtered_list[0]

    def toJSON(self) -> str:
        """Converts the databank to a JSON formatted string."""
        return json.dumps(self, cls=Encoder, sort_keys=True, indent=4)

    def build_graph(self, root:Actor, depth:int=-1) -> Graph:
        """
        Returns a Graph object centered around the given Actor to the given depth.
        If depth is zero, returns the entire Graph.
        """
        graph = Graph(root, depth)
        checked = set([root])
        buffer = list(set([actor for actor in self.actors if actor.has_credit_with(root)]).difference(checked))
        current_depth = 1
        while buffer:
            if len(buffer) == 1: print(buffer[0])
            extension = []
            bar = ProgressBar(max_value=len(buffer))
            i = 0
            for actor in buffer:                
                graph.add_node(actor, self.films)
                checked.add(actor)
                extension += [costar for costar in self.actors if costar.has_credit_with(buffer[0]) > 0]
                buffer.remove(actor)
                i += 1
                bar.update(i)
            buffer = list(set(extension).difference(checked))
            current_depth += 1
            if depth >= 0 and current_depth > depth:
                break
        return graph

db = FilmografAPI()

print(
    sorted(db.actors, key=lambda actor: len(actor.filmography), reverse=True)[:10]
)