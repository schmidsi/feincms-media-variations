from django.conf import settings as django_settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import get_callable
from django.db import models
from django.utils.translation import ugettext_lazy as _

from feincms import settings
from feincms.contrib.fields import JSONField
from feincms.module.medialibrary.models import MediaFile

from processors import image_cropscale, image_thumbnail 


class MediaVariation(models.Model):
    default_storage_class = getattr(django_settings, 'DEFAULT_FILE_STORAGE',
                                    'django.core.files.storage.FileSystemStorage')
    default_storage = get_callable(default_storage_class)

    fs = default_storage(location=settings.FEINCMS_MEDIALIBRARY_ROOT,
                           base_url=settings.FEINCMS_MEDIALIBRARY_URL)
    
    file = models.FileField(_('file'), max_length=255, upload_to=settings.FEINCMS_MEDIALIBRARY_UPLOAD_TO, storage=fs, blank=True, null=True)
    mediafile = models.ForeignKey(MediaFile, related_name="variations")

    processor = models.CharField(_('processor'), max_length=30, choices=(), help_text=_('Choose your processor. A processor makes a MediaFileVariation based of the options.'))
    preselector = models.CharField(_('preselector'), max_length=50, choices=(), blank=True, null=True, help_text=_('Choose one of the prepared variation types.'))
    options = JSONField(_('options'), blank=True, null=True)
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    processors = []
    processors_dict = {}
    
    preselectors = {}
    
    @classmethod
    def register_processors(cls, *processors):
        cls.processors[0:0] = processors
        choices = [ t[0:2] for t in cls.processors ]
        processors_list = [ (t[0], t[2]) for t in cls.processors ]
        cls.processors_dict = dict(processors_list)
        cls._meta.get_field('processor').choices[:] = choices
    
    @classmethod
    def register_preselection(cls, *preselectors):
        for preselector in preselectors:
            cls.preselectors[preselector[0]] = (preselector[2], preselector[3])
            cls._meta.get_field('preselector').choices.append((preselector[0], preselector[1]))
    
    def process(self):
        if self.preselector:
            preselection = self.preselectors[self.preselector]
            self.processor = preselection[0]
            self.options = preselection[1]
            
        processed = self.processors_dict[self.processor](self.mediafile, self.options)
        self.file.save(processed['name'], processed['content'])
        
        return self.file
    
    def clean(self):
        if not self.preselector and not self.processor:
            raise ValidationError(_('Specify either a preselector or a processor'))
        
        if not self.file:
            self.process()
    
MediaVariation.register_processors(
        ('image-cropscale', _('Image cropscale'), image_cropscale),
        ('image-thumbnail', _('Image thumbnail'), image_thumbnail)
    )