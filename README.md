# Film-o-graf

Film-o-graf is a three-tier web application that gives its users a more interactive approach 
to the connections between the actors behind the greatest films in the history of filmmaking.

The project is based on the **[Oracle of Bacon](https://oracleofbacon.org/)**. The creators of this
site labelled every actor with a number, the so-called *Bacon-number*, that represents their degree 
of separation from Kevin Bacon: if they were in a film together with Bacon, their Bacon-number is
one; if they don't have a film together with Bacon, but they have a film with an actor whose
Bacon-number is *n*, their Bacon-number is *n+1*.
[Read more about the history of the Oracle of Bacon here.](https://en.wikipedia.org/wiki/Six_Degrees_of_Kevin_Bacon#History)

The film-o-graf application uses a graph database powered by [Neo4j](https://neo4j.com/).
The backend was made using [Django](https://www.djangoproject.com/), while the frontend is powered by [React](https://reactjs.org/).
