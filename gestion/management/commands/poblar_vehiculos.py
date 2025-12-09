from django.core.management.base import BaseCommand
from gestion.models import Vehiculo

class Command(BaseCommand):
    help = 'Pobla la base de datos con marcas y modelos de vehículos comunes'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando población de marcas y modelos...')
        
        # Datos de marcas y modelos populares
        marcas_modelos = {
            'Toyota': ['Corolla', 'Camry', 'RAV4', 'Hilux', 'Land Cruiser', 'Yaris', 'Prius', '4Runner'],
            'Honda': ['Civic', 'Accord', 'CR-V', 'Pilot', 'Fit', 'HR-V', 'Odyssey'],
            'Ford': ['F-150', 'Mustang', 'Explorer', 'Escape', 'Ranger', 'Bronco', 'Edge'],
            'Chevrolet': ['Silverado', 'Malibu', 'Equinox', 'Traverse', 'Tahoe', 'Camaro', 'Colorado'],
            'Nissan': ['Altima', 'Sentra', 'Rogue', 'Pathfinder', 'Frontier', 'Versa', 'Murano'],
            'Hyundai': ['Elantra', 'Sonata', 'Tucson', 'Santa Fe', 'Accent', 'Kona', 'Palisade'],
            'Kia': ['Forte', 'Optima', 'Sportage', 'Sorento', 'Soul', 'Telluride', 'Seltos'],
            'Mazda': ['Mazda3', 'Mazda6', 'CX-5', 'CX-9', 'MX-5', 'CX-30'],
            'Volkswagen': ['Jetta', 'Passat', 'Tiguan', 'Atlas', 'Golf', 'Beetle', 'Arteon'],
            'BMW': ['Serie 3', 'Serie 5', 'X3', 'X5', 'Serie 7', 'X1', 'Serie 4'],
            'Mercedes-Benz': ['Clase C', 'Clase E', 'GLC', 'GLE', 'Clase A', 'Clase S', 'GLA'],
            'Audi': ['A4', 'A6', 'Q5', 'Q7', 'A3', 'Q3', 'A8'],
            'Jeep': ['Wrangler', 'Cherokee', 'Grand Cherokee', 'Compass', 'Renegade', 'Gladiator'],
            'Subaru': ['Outback', 'Forester', 'Crosstrek', 'Impreza', 'Legacy', 'Ascent'],
            'Mitsubishi': ['Outlander', 'Eclipse Cross', 'Pajero', 'L200', 'Mirage', 'ASX'],
            'Suzuki': ['Swift', 'Vitara', 'Jimny', 'S-Cross', 'Baleno', 'Ignis'],
            'Renault': ['Sandero', 'Logan', 'Duster', 'Kwid', 'Captur', 'Koleos'],
            'Peugeot': ['208', '308', '2008', '3008', '5008', 'Partner'],
            'Citroën': ['C3', 'C4', 'C5', 'Berlingo', 'C3 Aircross', 'C4 Cactus'],
            'Fiat': ['Uno', 'Mobi', 'Argo', 'Toro', 'Cronos', 'Ducato'],
        }

        self.stdout.write('\nMarcas y modelos disponibles:')
        self.stdout.write('=' * 60)
        
        for marca, modelos in marcas_modelos.items():
            self.stdout.write(f'\n{marca}:')
            for modelo in modelos:
                self.stdout.write(f'  • {modelo}')
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'\n✓ Total: {len(marcas_modelos)} marcas'))
        total_modelos = sum(len(modelos) for modelos in marcas_modelos.values())
        self.stdout.write(self.style.SUCCESS(f'✓ Total: {total_modelos} modelos'))
        
        self.stdout.write('\n' + self.style.WARNING('NOTA: Estos datos están disponibles para usar al crear vehículos.'))
        self.stdout.write(self.style.WARNING('Las marcas y modelos son campos de texto libre en el modelo actual.'))
        self.stdout.write(self.style.WARNING('Para autocompletar en el frontend, usa estos valores de referencia.'))
