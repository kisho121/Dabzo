from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps
import cloudinary.uploader
import os

class Command(BaseCommand):
    help = "Upload existing local media files to Cloudinary and update DB paths"

    def handle(self, *args, **kwargs):
        media_root = settings.MEDIA_ROOT

        if not os.path.isdir(media_root):
            self.stdout.write(self.style.ERROR("MEDIA_ROOT does not exist"))
            return

        self.stdout.write(self.style.SUCCESS("Uploading old images..."))

        # Loop through all models
        for model in apps.get_models():
            for field in model._meta.fields:
                if field.get_internal_type() == 'ImageField':
                    queryset = model.objects.exclude(**{field.name: ""})
                    for obj in queryset:
                        img = getattr(obj, field.name)
                        path = os.path.join(media_root, str(img))

                        if os.path.exists(path):
                            # Upload to cloudinary
                            result = cloudinary.uploader.upload(path)

                            # Update the field with cloudinary URL
                            setattr(obj, field.name, result['secure_url'])
                            obj.save()

                            self.stdout.write(self.style.SUCCESS(f"Uploaded: {path}"))

        self.stdout.write(self.style.SUCCESS("All old images uploaded successfully!"))
