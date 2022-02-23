from imdb import Cinemagoer
from sys import argv

def find_depth(left_name, right_name):
    db = Cinemagoer()

    print(f"Collecting data on {right_name}...")
    right_person = db.get_person(db.search_person(right_name)[0].getID())

    try:
        right_filmography = set(right_person['filmography']['actor'])
    except KeyError:
        right_filmography = set(right_person['filmography']['actress'])
  
    checked = set()
    queue = [left_name]
    actors = {}
    extension = []
    depth = 1

    while 1:
        for name in queue:
            if name in checked:
                continue
            checked.add(name)

            print(f'Collecting data on {name}...')
            actor = db.get_person(db.search_person(name)[0].getID())
            try:
                actor_filmography = set(actor['filmography']['actor'])
            except KeyError:
                actor_filmography = set(actor['filmography']['actress'])

            actors[name] = actor_filmography

            print(f"Checking {actor['name']}'s filmography against {right_name}'s... (current depth: {depth})")

            if len(actor_filmography & right_filmography) > 0:
                return depth
            
        for name in actors:
            for movie in actors[name]:
                print(f"Adding {name}'s costars from {movie['title']} to the queue extension...")
                movie_data = db.get_movie(movie.getID())
                for costar in movie_data['cast']:
                    try:
                        if costar['name'] not in checked: 
                            extension.append(costar['name'])
                    except KeyError:
                        continue

        queue = extension
        extension = []
        depth += 1

        print()

print(f"Distance between {argv[1]} and {argv[2]}: {find_depth(argv[1], argv[2])}")