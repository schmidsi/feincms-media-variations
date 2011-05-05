import os

from PIL import Image

from django.core.files import File
from django.conf import settings


def image_thumbnail(mediafile, options):
    default_options = {'quality' : 90}
    default_options.update(options)
    options = default_options.copy()
    
    filename = mediafile.file.name
    
    try:
        basename, format = filename.rsplit('.', 1)
    except ValueError:
        basename, format = filename, 'jpg'
    processed_name = '%s_thumb_%sx%sq%s.%s'% (basename, options['width'], options['height'], options['quality'], format)
    processed_path = os.path.join(settings.MEDIA_ROOT, processed_name).encode('utf-8')
    orig_path = os.path.join(settings.MEDIA_ROOT, filename).encode('utf-8')
    
    image = Image.open(orig_path)
    image.thumbnail([options['width'], options['height']], Image.ANTIALIAS)
    image.save(processed_path, image.format, quality=options['quality'])
    
    return File(open(processed_path))


def image_cropscale(mediafile, options):
    default_options = {'quality' : 90}
    default_options.update(options)
    options = default_options.copy()
    
    filename = mediafile.file.name
    
    try:
        basename, format = filename.rsplit('.', 1)
    except ValueError:
        basename, format = filename, 'jpg'
    processed_name = '%s_crop_%sx%sq%s.%s'% (basename, options['width'], options['height'], options['quality'], format)
    processed_path = os.path.join(settings.MEDIA_ROOT, processed_name).encode('utf-8')
    orig_path = os.path.join(settings.MEDIA_ROOT, filename).encode('utf-8')
    
    image = Image.open(orig_path)
    
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
    
    image.save(processed_path, image.format, quality=options['quality'])
    
    return File(open(processed_path))
