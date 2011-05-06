import os

import cStringIO

from PIL import Image

from django.core.files.base import ContentFile
from django.conf import settings


def image_thumbnail(mediafile, options):
    default_options = {'quality' : 90}
    default_options.update(options)
    options = default_options.copy()
    
    original = mediafile.file
    filename = original.name
    
    try:
        basename, format = filename.rsplit('.', 1)
    except ValueError:
        basename, format = filename, 'jpg'
    processed_name = '%s_thumb_%sx%sq%s.%s'% (basename, options['width'], options['height'], options['quality'], format)
    
    original.seek(0)
    image = Image.open(original)
    
    # Convert to RGB if necessary
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
    
    image.thumbnail([options['width'], options['height']], Image.ANTIALIAS)
    memory_file = cStringIO.StringIO()
    image.save(memory_file, image.format, quality=options['quality'])
    
    content_file = ContentFile(memory_file.getvalue())
    memory_file.close()
    
    return {'content' : content_file, 'name' : processed_name}


def image_cropscale(mediafile, options):
    default_options = {'quality' : 90}
    default_options.update(options)
    options = default_options.copy()
    
    original = mediafile.file
    filename = original.name
    
    try:
        basename, format = filename.rsplit('.', 1)
    except ValueError:
        basename, format = filename, 'jpg'
    processed_name = '%s_crop_%sx%sq%s.%s'% (basename, options['width'], options['height'], options['quality'], format)
    
    original.seek(0)
    image = Image.open(original)
    format = image.format
    
    # Convert to RGB if necessary
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
    
    src_width, src_height = image.size
    src_ratio = float(src_width) / float(src_height)
    dst_width, dst_height = options['width'], options['height']
    dst_ratio = float(dst_width) / float(dst_height)
    
    if dst_ratio < src_ratio:
        crop_height = src_height
        crop_width = crop_height * dst_ratio
        x_offset = float(src_width - crop_width) / 2
        y_offset = 0
    else:
        crop_width = src_width
        crop_height = crop_width / dst_ratio
        x_offset = 0
        y_offset = float(src_height - crop_height) / 2
    x_offset, y_offset = int(x_offset), int(y_offset)

    image = image.crop((x_offset, y_offset, x_offset+int(crop_width), y_offset+int(crop_height)))
    image = image.resize((dst_width, dst_height), Image.ANTIALIAS)
    memory_file = cStringIO.StringIO()
    image.save(memory_file, format, quality=options['quality'])
    
    content_file = ContentFile(memory_file.getvalue())
    memory_file.close()
    
    return {'content' : content_file, 'name' : processed_name}