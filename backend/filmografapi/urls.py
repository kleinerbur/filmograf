from django.urls import path
from .views import *

urlpatterns = [
    path('exists', nodeExists),
    path('distance', getDistance),
    path('path', getPath),
    path('graph', getGraph)
]