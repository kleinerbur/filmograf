from django.urls import path
from .views import *

urlpatterns = [
    path('exists', nodeExists),
    path('node', getNode),
    path('distance', getDistance),
    path('path', getPath),
    path('graph', getGraph)
]