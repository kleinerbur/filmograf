from imdb import Cinemagoer
from sys import argv

db = Cinemagoer()
checked = set()

right_data = None
right_filmography = set()

def findLink(left, right, depth=0):

    global right_data, right_filmography

    left_data = db.get_person(db.search_person(left)[0].getID())
    if right_data is None:
        right_data = db.get_person(db.search_person(right)[0].getID())

    if left_data.getID() != right_data.getID():
        depth +=1

        left_filmography = set()
        try:
            left_filmography = set(left_data['filmography']['actor'])
        except KeyError:
            left_filmography = set(left_data['filmography']['actress'])

        if right_filmography == set():
            try:
                right_filmography = set(right_data['filmography']['actor'])
            except KeyError:
                right_filmography = set(right_data['filmography']['actress'])

        intersection = left_filmography & right_filmography
        print(f"{len(intersection)} <- |{left} ∩ {right}|")

        if len(intersection) > 0:
            return depth
        
        else:
            
    
    return depth

print(findLink(argv[1], argv[2]))