This part of the application is in charge of pulling data from IMDb and uploading it to
the neo4j database in the correct format.

The interface first pulls the data of the given amount (**FILM_LIMIT**) of films (it is currently limited to the top 250 highest rated movies on IMDb) in parallel, then does the same with the actors in their casts (up to the given **CAST_LIMIT**, which is 25 by default).

After the data gathering is finished, a JSON snapshot is saved. If a snapshot is present 
when this script is ran, the snapshot gets loaded instead of pulling the data again.
This can be overriden with the `--force` flag.

When populating the database, the actors are uploaded first on multiple threads. When 
all actors have been uploaded, the films are uploaded concurrently, and a relationship 
is created between the film and each actor of its cast. The relationship is labeled 
with the role the actor plays in the film, if their role has a name.

There is a chance of isolated nodes appearing in the database after populating is finished, 
this is due to possible connection errors between the server. The amount of failed uploads 
is marginal, the isolated nodes are removed from the database.

The interface can also forward queries to the database. To do this, use the `--query` flag.

Pipenv is required to run the interface:
`pipenv run python3 interface.py --help`