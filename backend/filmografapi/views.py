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
            path = db.cypher_query(
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
                WITH collect(path) as paths
                CALL apoc.convert.toTree(paths) YIELD value
                RETURN value
                '''
            )[0][0][0]
            return JsonResponse({"path": path}, safe=False)
        except Exception as e:
            return JsonResponse({"error": f"{e}"}, safe=False)


def getGraph(request):
    if request.method == 'GET':
        root  = request.GET.get("root", "")
        depth = request.GET.get("depth", 0)
        try:
            graph = db.cypher_query(
                f'''
                MATCH (root)
                WHERE {compare_against_node('root', root)}
                CALL apoc.path.spanningTree(root, {{ maxLevel: {depth} }})
                YIELD path
                WITH collect(path) as paths
                CALL apoc.convert.toTree(paths) YIELD value
                RETURN value
                '''
            )[0][0][0]
            return JsonResponse({"graph": graph}, safe=False)
        except Exception as e:
            return JsonResponse({"error": f"{e}"}, safe=False) 