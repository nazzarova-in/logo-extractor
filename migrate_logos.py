import os
import django
import base64
from django.core.files.base import ContentFile


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logo_extractor.settings")
django.setup()

from logosfinder.models import Logo

def migrate_old_logos_to_files():
    logos = Logo.objects.filter(image__isnull=True).exclude(image_base64__isnull=True)
    count = 0
    for logo in logos:
        try:
            img_data = base64.b64decode(logo.image_base64)
            content_file = ContentFile(img_data, name=f'logo_{logo.website.id}.png')
            logo.image.save(content_file.name, content_file, save=True)
            count += 1
        except Exception as e:
            print(f"Failed for logo id {logo.id}: {e}")
    print(f"Updated {count} logos with image files")

if __name__ == "__main__":
    migrate_old_logos_to_files()
