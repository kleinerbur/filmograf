from re import L
from imdb import Cinemagoer
from sys import argv

db = Cinemagoer()

name = argv[1]
maxdepth = int(argv[2])

graph = {}
for i in range(maxdepth):
    graph[i] = set()
    
checked = set()

def buildGraph(name, depth, maxdepth):
    if depth == maxdepth: return
    if name not in checked:
        
        checked.add(name)
        graph[depth].add(name)
        
        actor = db.get_person(db.search_person(name)[0].getID())
        costars = []
        try:
            costars = [db.get_movie(film.getID())['cast'] for film in actor['filmography']['actor']]
        except KeyError:
            costars = [db.get_movie(film.getID())['cast'] for film in actor['filmography']['actress']]
        
        for costar in costars:
            print(costar)
            buildGraph(costar.getName(), depth+1, maxdepth)


actor = db.get_person(db.search_person(name)[0].getID())
movie = actor['filmography']['actress'][15]
for costar in db.get_movie(movie.getID())['cast']:
    # try:
    print(costar['name'])
    # except KeyError:
        # None

# buildGraph(name, 0, maxdepth)
for row in graph:
    print(row)
    print()