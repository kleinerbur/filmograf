from django.http import JsonResponse, HttpRequest
from neomodel import db
from typing import Dict

def compare_against_node(alias:str, keyword:str) -> str:
    """
    Macro that returns a string that compares a node's name/title/imdb ID against a given keyword.
    Whitespace is ignored.
    """
    return f'''toUpper({alias}.name)           =~ toUpper(".*{".*".join(keyword.split())}.*") OR 
               toUpper({alias}.title)          =~ toUpper(".*{".*".join(keyword.split())}.*") OR
               toUpper({alias}.imdb_id)        =~ toUpper(".*{".*".join(keyword.split())}.*") OR
               "nm" + toUpper({alias}.imdb_id) =~ toUpper(".*{".*".join(keyword.split())}.*") OR
               "tt" + toUpper({alias}.imdb_id) =~ toUpper(".*{".*".join(keyword.split())}.*") OR
               {alias}.imdb_uri + "/*"         =~ ".*{keyword}.*"'''


def nodeExists(request:HttpRequest) -> JsonResponse:
    """
    Checks if a node exists that matches the given keyword.
    Returns a JSON response containing a boolean value with the key 'nodeExists'.
    """
    if request.method == 'GET':
        keyword = request.GET.get("search", "")
        try:
            exists = db.cypher_query(f'''
                MATCH (node)
                WHERE {compare_against_node('node', keyword)}
                RETURN count(node) > 0
                ''')[0][0][0]
            return JsonResponse({"nodeExists": exists})
        except IndexError:
            return JsonResponse({"nodeExists": False})
        except Exception as e:
            return JsonResponse({"error": f"{e}"})


def getNode(keyword:str) -> Dict:
    """
    Returns the first node that matches the given keyword, if there's any.
    Otherwise returns None.

    The following values define a node: id, label, group, image, poster, uri

    NOTE: Existence is validated on the frontend side.
    """
    try:
        node = db.cypher_query(f'''
            CALL {{
                MATCH (node)
                WHERE {compare_against_node('node', keyword)}
                RETURN node LIMIT 1
            }}
            RETURN {{
                id: toInteger(node.imdb_id), 
                label: COALESCE(node.name, "") + COALESCE(node.title, ""),
                group: node.group, 
                image: node.image, 
                poster: node.poster, 
                uri: node.imdb_uri
            }}''')[0][0][0]
        return node
    except:
        return None


def getDistance(request:HttpRequest) -> JsonResponse:
    """
    Calculates the shortest distance between two nodes that match the given keywords.
    Returns a JSON response containing a numerical value (>=0) with the key 'distance'.
    If there is no connection between the two nodes, the returned value is '-'.

    NOTE: The calculated distance is halved because only every second node is an actor
    (the Bacon-number does not count the connecting movies)
    """
    if request.method == 'GET':
        left  = request.GET.get("left", "")
        right = request.GET.get("right", "")
        if getNode(left) == getNode(right):
            distance = 0
        else:
            try:
                distance = db.cypher_query(f'''
                    CALL {{
                        MATCH (left)
                        WHERE {compare_against_node('left', left)}
                        RETURN left LIMIT 1
                    }}
                    CALL {{
                        MATCH (right)
                        WHERE {compare_against_node('right', right)}
                        RETURN right LIMIT 1
                    }}
                    MATCH path=shortestPath((left)-[*]-(right))
                    RETURN length(path)
                    ''')[0][0][0]
            except IndexError:
                return JsonResponse({"distance": "-"})
            except Exception as e:
                return JsonResponse({"error": f"{e}"})
        return JsonResponse({"distance": distance/2})


def getPath(request:HttpRequest) -> JsonResponse:
    """
    Calculates the shortest path between two nodes that match the given keywords.
    Returns a JSON response containing a list of nodes under the key 'nodes'
    and a list of relationships under the key 'edges'.

    The following values define a node: id, label, group, image, poster, uri
    The following values define an edge: id, from (id of start node), to (id of destination), label
    """
    if request.method == 'GET':
        left  = request.GET.get("left", "")
        right = request.GET.get("right", "")
        if getNode(left) == getNode(right):
            nodes = [getNode(left)]
            edges = []
        else:
            try:
                nodes = db.cypher_query(f'''
                    CALL {{
                        MATCH (left)
                        WHERE {compare_against_node('left', left)}
                        RETURN left LIMIT 1
                    }}
                    CALL {{
                        MATCH (right)
                        WHERE {compare_against_node('right', right)}
                        RETURN right LIMIT 1
                    }}
                    MATCH path=shortestPath((left)-[*]-(right))
                    RETURN [node in nodes(path) | {{
                        id:     toInteger(node.imdb_id),
                        label:  COALESCE(node.name, "") + COALESCE(node.title, ""),
                        group:  node.group, 
                        image:  node.image,
                        poster: node.poster,
                        uri:    node.imdb_uri
                    }}] as nodes''')[0][0][0]
                edges = db.cypher_query(f'''
                    CALL {{
                        MATCH (left)
                        WHERE {compare_against_node('left', left)}
                        RETURN left LIMIT 1
                    }}
                    CALL {{
                        MATCH (right)
                        WHERE {compare_against_node('right', right)}
                        RETURN right LIMIT 1
                    }}
                    MATCH path=shortestPath((left)-[*]-(right))
                    RETURN [edge in relationships(path) | {{
                        id:    id(edge),
                        from:  toInteger(startNode(edge).imdb_id),
                        to:    toInteger(endNode(edge).imdb_id),
                        label: edge.role
                    }}] as edges''')[0][0][0]
            except IndexError:
                return JsonResponse({"nodes": [{"hidden": True}], "edges": []})
            except Exception as e:
                return JsonResponse({"error": f"{e}"})
        return JsonResponse({"nodes": nodes, "edges": edges})


def getGraph(request:HttpRequest) -> JsonResponse:
    """
    Creates a graph centered around a node that matches the given keyword to the given depth.
    Returns a JSON response containing a list of nodes under the key 'nodes'
    and a list of relationships under the key 'edges'.

    The following values define a node: id, label, group, image, poster, uri
    The following values define an edge: id, from (id of start node), to (id of destination), label
    """
    if request.method == 'GET':
        root  = request.GET.get("root", "")
        depth = request.GET.get("depth", 0)
        try:
            if '-' in depth:
                depth = 0
            else:
                depth = int(depth) * 2
            nodes = [row[0] for row in db.cypher_query(f'''
                CALL {{
                    MATCH (root)
                    WHERE {compare_against_node('root', root)}
                    RETURN root LIMIT 1
                }}
                CALL apoc.path.spanningTree(root, {{ maxLevel: {depth} }})
                YIELD path
                UNWIND nodes(path) AS nodes
                WITH distinct nodes AS node
                RETURN {{
                    group: node.group,
                    image: node.image,
                    poster: node.poster,
                    id: toInteger(node.imdb_id),
                    uri: node.imdb_uri,
                    label: COALESCE(node.name, "") + COALESCE(node.title, "")
                }}''')[0]]
            edges = [row[0] for row in db.cypher_query(f'''
                CALL {{
                    MATCH (root)
                    WHERE {compare_against_node('root', root)}
                    RETURN root LIMIT 1
                }}
                CALL apoc.path.spanningTree(root, {{ maxLevel: {depth} }})
                YIELD path
                UNWIND relationships(path) AS relationships
                WITH distinct relationships AS r
                RETURN {{
                    id:    id(r),
                    from:  toInteger(startNode(r).imdb_id),
                    to:    toInteger(endNode(r).imdb_id),
                    label: r.role
                }}''')[0]]
            return JsonResponse({"nodes": nodes, "edges": edges})
        except IndexError:
            return JsonResponse({"nodes": [{"hidden": True}], "edges": []})
        except Exception as e:
            return JsonResponse({"error": f"{e}"}) 