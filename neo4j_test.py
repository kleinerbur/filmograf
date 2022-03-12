from neo4j import GraphDatabase
from imdb  import Cinemagoer

imdb = Cinemagoer()

class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create driver:", e)
    
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
    
    def query(self, query, params=None, db=None):
        assert self.__driver is not None, "Driver is not initialized!"
        session, response = None, None
        try:
            if db is not None:
                session = self.__driver.session(database=db)
            else: session = self.__driver.session()
            response = list(session.run(query, params))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response



n4j = Neo4jConnection("neo4j://localhost:7687", "neo4j", "password")
n4j.query()