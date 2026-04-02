import csv
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "comicstore.settings")
django.setup()

from crud.models import Comic  

archivo_csv = 'comics.csv'

with open(archivo_csv, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        comic, created = Comic.objects.update_or_create(
            id=row['id'],
            defaults={
                'title': row['title'],
                'description': row.get('description', '').strip(),
                'price': row['price'],
                'img_path': row['img_path'],
            }
        )
        if created:
            print(f'Comic creado: {comic.title}')
        else:
            print(f'Comic actualizado: {comic.title}')