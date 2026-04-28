from django.urls import path
from .views import SimulationRunView, SimulationStateView

urlpatterns = [
    path('run/', SimulationRunView.as_view(), name='simulation-run'),
    path('state/', SimulationStateView.as_view(), name='simulation-state'),
]
