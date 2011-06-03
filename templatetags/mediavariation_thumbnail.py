from django import template

from feincms.module.medialibrary.models import MediaFile
from feinheit.media_variations.models import MediaVariation

register = template.Library()


def tryint(v):
    try:
        return int(v)
    except ValueError:
        return 999999 # Arbitrarily big number

def get_options_from_arg(arg):
    # try to get quality
    if 'q' in arg:
        size, q = arg.split('q')
        q = tryint(q)
    else:
        q =  90
        size = arg
    
    # defining the size
    x, y = [tryint(x) for x in size.split('x')]
    
    return {
        'height' : y,
        'width' : x,
        'quality' : q
    }

@register.filter
def thumbnail(mediafile, arg='200x200q90'):
    if not (mediafile and 'x' in arg):
        return u'<!-- missing arguments in thumbnail -->'
    
    if not type(mediafile) == MediaFile:
        return u'<!-- need feincms mediafile to work -->'
    
    variation = mediafile.get_variation('image-thumbnail', get_options_from_arg(arg))
    return unicode(variation.file.url)


@register.filter
def cropscale(mediafile, arg='200x200q90'):
    if not (mediafile and 'x' in arg):
        return u'<!-- missing arguments in thumbnail -->'
    
    if not type(mediafile) == MediaFile:
        return u'<!-- need feincms mediafile to work -->'
    
    variation = mediafile.get_variation('image-cropscale', get_options_from_arg(arg))
    return unicode(variation.file.url)


@register.filter
def mediavariation(mediafile, preselection):
    if not preselection:
        try:
            preselection = MediaVariation.preselectors.items()[0][0]
        except IndexError:
            return u'<!-- no preselection given and no preselections configured -->'
    
    if not type(mediafile) == MediaFile:
        return u'<!-- need feincms mediafile to work -->'
    
    if not preselection in MediaVariation.preselectors:
        return u'<!-- preselection "%s" not defined -->' % preselection
    
    variation = mediafile.get_variation(preselection)
    return unicode(variation.file.url)
