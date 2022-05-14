import unittest
import interface
from os import path

class TestDatabaseBuilder(unittest.TestCase):
    def test_pull_film_data(self):
        builder = interface.DatabaseBuilder()
        builder.actors = set()
        builder.films  = set()
        
        builder.pull_film_data('0120689')
        self.assertEqual(len(builder.films), 1)

        film = list(builder.films)[0]
        self.assertEqual(film.id, '0120689')
        self.assertEqual(film.title, 'The Green Mile')
        self.assertEqual(film.image, 'https://m.media-amazon.com/images/M/MV5BMTUxMzQyNjA5MF5BMl5BanBnXkFtZTYwOTU2NTY3._V1_SY150_CR0,0,101,150_.jpg')
        self.assertEqual(film.poster, 'https://m.media-amazon.com/images/M/MV5BMTUxMzQyNjA5MF5BMl5BanBnXkFtZTYwOTU2NTY3.jpg')
        self.assertGreater(len(film.cast), 0)


    def test_pull_actor_data(self):
        builder = interface.DatabaseBuilder()
        builder.actors = set()
        builder.films  = set()
        
        builder.pull_actor_data('0000158')
        self.assertEqual(len(builder.actors), 1)

        actor1 = list(builder.actors)[0]
        self.assertEqual(actor1.id, '0000158')
        self.assertEqual(actor1.name, 'Tom Hanks')
        self.assertEqual(actor1.image, 'https://m.media-amazon.com/images/M/MV5BMTQ2MjMwNDA3Nl5BMl5BanBnXkFtZTcwMTA2NDY3NQ@@._V1_UY98_CR0,0,67,98_AL_.jpg')
        self.assertEqual(actor1.poster, 'https://m.media-amazon.com/images/M/MV5BMTQ2MjMwNDA3Nl5BMl5BanBnXkFtZTcwMTA2NDY3NQ@@.jpg')

        builder.pull_actor_data('11319515')
        self.assertEqual(len(builder.actors), 2)

        actor2 = [actor for actor in builder.actors if actor != actor1][0]
        self.assertEqual(actor2.image, 'https://cdn-icons-png.flaticon.com/128/1077/1077114.png')
        self.assertEqual(actor2.poster, 'https://t4.ftcdn.net/jpg/00/64/67/63/360_F_64676383_LdbmhiNM6Ypzb3FM4PPuFP9rHe7ri8Ju.jpg')

    def test_load_snapshot(self):
        builder = interface.DatabaseBuilder()
        builder.actors = set()
        builder.films  = set()

        if not path.isfile('snapshot.json'):
            builder.pull_film_data('0120689')
            self.assertEqual(len(builder.films), 1)
            
            builder.pull_actor_data('0000158')
            builder.pull_actor_data('11319515')
            self.assertEqual(len(builder.actors), 2)

            with open('snapshot.json', 'w') as jsonfile:
                jsonfile.write(self.toJSON())
            
            builder.actors = set()
            builder.films  = set()

        self.assertEqual(len(builder.films), 0)
        self.assertEqual(len(builder.actors), 0)
        
        builder.load_snapshot('snapshot.json')

        self.assertGreater(len(builder.films), 0)
        self.assertGreater(len(builder.actors), 0)
        
        
if __name__ == '__main__':
    unittest.main() 