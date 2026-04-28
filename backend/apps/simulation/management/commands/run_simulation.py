from django.core.management.base import BaseCommand
from apps.simulation.services import run_simulation_step

class Command(BaseCommand):
    help = 'Executes one step of the flood simulation'

    def handle(self, *args, **options):
        self.stdout.write("Running simulation step...")
        results = run_simulation_step()
        self.stdout.write(self.style.SUCCESS(f"Step completed. Updated {len(results)} cells."))
