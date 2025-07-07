import os
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image

def resize_image_field(image_field, target_width, target_height, crop=False):
    if not image_field:
        return image_field

    img = Image.open(image_field)

    if crop:
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height

        if img_ratio > target_ratio:
            new_height = target_height
            new_width = int(new_height * img_ratio)
        else:
            new_width = target_width
            new_height = int(new_width / img_ratio)

        img = img.resize((new_width, new_height), Image.LANCZOS)

        left = (new_width - target_width) / 2
        top = (new_height - target_height) / 2
        right = (new_width + target_width) / 2
        bottom = (new_height + target_height) / 2

        img = img.crop((left, top, right, bottom))

    else:
        img.thumbnail((target_width, target_height), Image.LANCZOS)

    buffer = BytesIO()
    img_format = img.format if img.format else 'PNG'
    img.save(buffer, format=img_format)
    file_content = ContentFile(buffer.getvalue())

    # ✅ Save only the BASE filename to avoid path duplication
    filename = os.path.basename(image_field.name)
    image_field.save(filename, file_content, save=False)

    return image_field
