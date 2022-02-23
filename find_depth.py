from imdb import Cinemagoer
from sys import argv
from imdb import Person, Movie
from multiprocessing import cpu_count
import concurrent.futures

def find_person(name: str, database: Cinemagoer) -> Person:
    print(f'Collecting data on {name}...')
    matches = database.search_person(name)
    if len(matches):
        id = matches[0].getID()
        return database.get_person(id)
    return None


def get_filmography(actor: Person) -> (Movie):
    if 'actor' in actor['filmography']:
        return set(actor['filmography']['actor'])
    elif 'actress' in actor['filmography']:
        return set(actor['filmography']['actress'])
    elif 'self' in actor['filmography']:
        return set(actor['filmography']['self'])
    else:
        return ()


def process_movie(movie: Movie, database: Cinemagoer, queue: list, checked: set):
    movie_data = database.get_movie(movie.getID())
    for costar in movie_data['cast']:
        try:
            if costar.getID() not in checked: 
                print(f"-> Adding {costar['name']}...")
                queue.append(costar)
        except KeyError:
            return

def populate_queue(data: dict, db: Cinemagoer, queue: list, checked: set):
    print('Populating queue with next level of costars...')
    for id in data:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for movie in data[id]:
                futures.append(executor.submit(process_movie, movie, db, queue, checked))
            for future in concurrent.futures.as_completed(futures):
                continue


def get_intersection(costar: Person, database: Cinemagoer, right_films: set, films_of: dict, checked: set) -> set:
    if costar.getID() in checked:
        return ()
    checked.add(costar.getID())

    print(f"Collecting data on {costar['name']}...")
    actor = database.get_person(costar.getID())
    actor_films = get_filmography(actor)
    films_of[costar.getID()] = actor_films

    return (costar.getID(), actor_films & right_films)


def find_depth(left_name, right_name):
    depth = -1        # return value
    db = Cinemagoer() # database

    # getting initial data about two actors
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        futures.append(executor.submit(find_person, left_name, db))
        futures.append(executor.submit(find_person, right_name, db))
        left = futures[0].result()
        right = futures[1].result()
        if left['name'] != left_name: left, right = right, left

    if left is None: print(f'Failed to find an actor with the name {left_name}.'); return depth
    if right is None: print(f'Failed to find an actor with the name {right_name}.'); return depth

    depth += 1 # 0

    # check if actors are the same
    if left.getID() == right.getID():
        return depth

    depth += 1 # 1

    # compare filmographies
    left_films = get_filmography(left)
    right_films = get_filmography(right)
    if len(left_films & right_films) > 0:
        print (f"MATCH FOUND: {[movie['title'] for movie in (left_films & right_films)]}")
        return depth

    depth += 1 # 2

    # switch starting point (left) and destination (right)
    # if right has fewer on-screen credits
    if len(left_films) > len(right_films):
        left_name, right_name = right_name, left_name
        left, right = right, left
        left_films, right_films = right_films, left_films

    films_of  = {left.getID(): left_films} # dictionary: actor's ID -> filmography
    checked   = set(left.getID())          # list of actor already checked
    queue     = [] # list of actors to check

    populate_queue(films_of, db, queue, checked)

    while queue:

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for costar in queue:
                futures.append(executor.submit(get_intersection, costar, db, right_films, films_of, checked))
            
            print([future.result() for future in futures if len(future.result()[1]) > 0])
            
            if len([future.result()[1] for future in futures if len(future.result()[1]) > 0]) > 0:
                return depth

        """
        # for costar in queue:
        #     if costar.getID() in checked:
        #         continue
        #     checked.add(costar.getID())

        #     actor = db.get_person(costar.getID())
        #     actor_films = get_filmography(actor)
        #     films_of[costar.getID()] = actor_films

        #     print(f"Checking {actor['name']}'s filmography against {right_name}'s... (current depth: {depth})")
        #     if len(actor_films & right_films) > 0:
        #         print (f"MATCH FOUND: {[movie['title'] for movie in (actor_films & right_films)]}")
        #         return depth
        """

        populate_queue(films_of, db, queue, checked)
        depth += 1

        print()

print(f"Distance between {argv[1]} and {argv[2]}: {find_depth(argv[1], argv[2])}")