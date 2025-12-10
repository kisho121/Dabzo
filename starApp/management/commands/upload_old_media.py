from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps
import cloudinary.uploader
import os
from django.db.models import ImageField


class Command(BaseCommand):
    help = "Upload existing local media files to Cloudinary and update DB paths"

    def handle(self, *args, **kwargs):
        media_root = str(settings.MEDIA_ROOT)
        self.stdout.write(f"MEDIA_ROOT path: {media_root}")

        if not os.path.isdir(media_root):
            self.stdout.write(self.style.ERROR("MEDIA_ROOT does not exist"))
            return

        self.stdout.write(self.style.SUCCESS("Uploading old images..."))

        uploaded_files = {}

        for model in apps.get_models():
            for field in model._meta.fields:
                if not isinstance(field, ImageField):
                    continue

                queryset = model.objects.exclude(**{field.name: ""}).exclude(**{field.name: None})

                for obj in queryset:
                    img_field = getattr(obj, field.name)
                    if not img_field:
                        continue

                    local_path = os.path.join(media_root, str(img_field))

                    if local_path in uploaded_files:
                        setattr(obj, field.name, uploaded_files[local_path])
                        obj.save()
                        self.stdout.write(self.style.SUCCESS(f"Skipped (already uploaded): {local_path}"))
                        continue

                    if os.path.exists(local_path):
                        try:
                            upload = cloudinary.uploader.upload(local_path, folder="spotstar")
                            cloud_url = upload.get("secure_url")

                            setattr(obj, field.name, cloud_url)
                            obj.save()

                            uploaded_files[local_path] = cloud_url

                            self.stdout.write(self.style.SUCCESS(f"Uploaded: {local_path}"))

                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"Error uploading {local_path}: {str(e)}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"File not found: {local_path}"))

        self.stdout.write(self.style.SUCCESS("All images uploaded successfully!"))
