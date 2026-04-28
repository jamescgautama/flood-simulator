from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.simulation.services import run_simulation_step
from apps.geography.models import GridCell

class SimulationRunView(APIView):
    def post(self, request, *args, **kwargs):
        rain_str = request.query_params.get('rain')
        height_str = request.query_params.get('height')

        try:
            rain = float(rain_str) if rain_str is not None else None
            height = float(height_str) if height_str is not None else None
        except ValueError:
            return Response({"error": "Invalid data type. Must be floats."}, status=status.HTTP_400_BAD_REQUEST)

        sim = run_simulation_step(rain_mm=rain, height_mm=height)

        return Response({
            "status": "success",
            "source": sim["source"],
            "parameters_used": {
                "rain_mm": sim["rain_mm"],
                "height_mm": sim["height_mm"],
            },
            "results": sim["results"],
        })

class SimulationStateView(APIView):
    def get(self, request, *args, **kwargs):
        cells = GridCell.objects.all().values('grid_id', 'elevation', 'distance_to_river')
        state = {cell['grid_id']: cell for cell in cells}
        return Response(state)
