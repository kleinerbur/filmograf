import re
from django.http import JsonResponse
from neomodel import db

def compare_against_node(alias:str, keyword:str) -> str:
        return f'''toUpper({alias}.name)    =~ toUpper(".*{".*".join(keyword.split())}.*") OR 
                   toUpper({alias}.imdb_id) =~ toUpper(".*{".*".join(keyword.split())}.*") OR
                   toUpper({alias}.title)   =~ toUpper(".*{".*".join(keyword.split())}.*")'''

def nodeExists(request):
    if request.method == 'GET':
        keyword = request.GET.get("search", "")
        try:
            exists = db.cypher_query(
                f'''
                MATCH (node)
                WHERE {compare_against_node('node', keyword)}
                RETURN count(node) > 0
                '''
            )[0][0][0]
            return JsonResponse({"nodeExists": exists}, safe=False)
        except Exception as e:
            return JsonResponse({"error": f"{e}"}, safe=False)


def getNode(request):
    if request.method == 'GET':
        keyword = request.GET.get("search", "")
        try:
            node = db.cypher_query(
                f'''
                CALL {{
                    MATCH (node)
                    WHERE {compare_against_node('node', keyword)}
                    RETURN node LIMIT 1
                }}
                RETURN {{imdb_id: node.imdb_id, imdb_uri: node.imdb_uri, name: node.name, title: node.title}}
                '''
            )[0][0][0]
            return JsonResponse(node, safe=False)
        except Exception as e:
            return JsonResponse({"error": f"{e}"}, safe=False)


def getDistance(request):
    if request.method == 'GET':
        left  = request.GET.get("left", "")
        right = request.GET.get("right", "")
        try:
            distance = db.cypher_query(
                f'''
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
                '''
            )[0][0][0]
            return JsonResponse({"distance": distance}, safe=False)
        except IndexError:
            return JsonResponse({"distance": "-"}, safe=False)
        except Exception as e:
            return JsonResponse({"error": f"{e}"}, safe=False)


def getPath(request):
    if request.method == 'GET':
        left  = request.GET.get("left", "")
        right = request.GET.get("right", "")
        try:
            nodes = db.cypher_query(
                f'''
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
                RETURN [n in nodes(path)| {{id: n.imdb_id, uri:n.imdb_uri, label: COALESCE(n.name, "") + COALESCE(n.title, "")}}] as nodes
                '''
            )[0][0][0]
            edges = db.cypher_query(
                f'''
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
                RETURN [r in relationships(path)| {{from: startNode(r).imdb_id, to: endNode(r).imdb_id}}] as edges
                '''
            )[0][0][0]
            return JsonResponse({"path": {"nodes": nodes, "edges": edges}}, safe=False)
        except Exception as e:
            return JsonResponse({"error": f"{e}"}, safe=False)


def getGraph(request):
    if request.method == 'GET':
        root  = request.GET.get("root", "")
        depth = request.GET.get("depth", 0)
        try:
            nodes = db.cypher_query(
                f'''
                CALL {{
                    MATCH (root)
                    WHERE {compare_against_node('root', root)}
                    RETURN root LIMIT 1
                }}
                CALL apoc.path.spanningTree(root, {{ maxLevel: {depth} }})
                YIELD path
                UNWIND nodes(path) AS nodes
                WITH distinct nodes AS node
                RETURN {{group: node.group, image: node.image, id: toInteger(node.imdb_id), uri: node.imdb_uri, label: COALESCE(node.name, "") + COALESCE(node.title, "")}}
                '''
            )[0]
            nodes = [row[0] for row in nodes]
            edges = db.cypher_query(
                f'''
                CALL {{
                    MATCH (root)
                    WHERE {compare_against_node('root', root)}
                    RETURN root LIMIT 1
                }}
                CALL apoc.path.spanningTree(root, {{ maxLevel: {depth} }})
                YIELD path
                UNWIND relationships(path) AS relationships
                WITH distinct relationships AS r
                RETURN {{from: toInteger(startNode(r).imdb_id), to: toInteger(endNode(r).imdb_id), id: id(r)}}
                '''
            )[0]
            edges = [row[0] for row in edges]
            return JsonResponse({"graph": {"nodes": nodes, "edges": edges}}, safe=False)
        except Exception as e:
            return JsonResponse({"error": f"{e}"}, safe=False) 