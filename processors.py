import os

import cStringIO, ImageFilter

from PIL import Image

from django.conf import settings


def get_processed_name(filename, suffix):
    try:
        basename, format = filename.rsplit('.', 1)
    except ValueError:
        basename, format = filename, 'jpg'
    return '%s_%s.%s'% (basename, suffix, format)


def image_thumbnail(file, filename, options):
    default_options = {'quality' : 90}
    default_options.update(options)
    options = default_options
    original = file
    
    original.seek(0)
    image = Image.open(original)
    
    # Convert to RGB if necessary
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
    
    image.thumbnail([options['width'], options['height']], Image.ANTIALIAS)
    memory_file = cStringIO.StringIO()
    image.save(memory_file, image.format, quality=options['quality'])
    
    processed_name = get_processed_name(filename, 'thumb_%sx%sq%s' % (options['width'], options['height'], options['quality']))
    return {'memfile' : memory_file, 'name' : processed_name}


def image_cropscale(mediafile, options):
    default_options = {'quality' : 90}
    default_options.update(options)
    options = default_options
    original = mediafile.file

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
    
    processed_name = get_processed_name(original, 'crop_%sx%sq%s' % (options['width'], options['height'], options['quality']))
    return {'content' : content_file, 'name' : processed_name}


def image_blur(mediafile, options):
    default_options = {'quality' : 90}
    default_options.update(options)
    options = default_options
    original = mediafile.file
    memory_file = cStringIO.StringIO()
    image = Image.open(original)
    format = image.format
    
    image = image.filter(ImageFilter.BLUR)
    image.save(memory_file, format, quality=options['quality'])
    content_file = ContentFile(memory_file.getvalue())
    memory_file.close()
    
    processed_name = get_processed_name(original, 'blur_q%s' % options['quality'])
    return {'content' : content_file, 'name' : processed_name}
