from django.conf import settings as django_settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.urlresolvers import get_callable
from django.db import models
from django.utils.translation import ugettext_lazy as _

from feincms import settings
from feincms.contrib.fields import JSONField
from feincms.module.medialibrary.models import MediaFile

from processors import image_cropscale, image_thumbnail, image_blur


class VariationManager(models.Manager):
    use_for_related_fields = True
    
    def reprocess(self):
        variations = super(VariationManager, self).get_query_set()
        for variation in variations:
            variation.process()
        return variations
    
    
    def get_or_create(self, *args, **kwargs):
        variation, created = super(VariationManager, self).get_or_create(*args, **kwargs)
        if created:
            variation.process()
        return variation, created
    
    def get_by_preselection(self, preselector, update=False):
        variation, created = self.get_or_create(preselector=preselector)
        if created and update:
            variation.process()
        return variation
    
    def get_by_options(self, update=False, options=None, *args):
        if not options:
            if type(args[0]) == str:
                options = [args[0], args[1]]
            if type(args[0]) in (list, tuple):
                options = args[0]
        if type(options) == tuple:
            options = list(options)
        
        variation, created = self.get_or_create(options=options)
        if created and update:
            variation.process()
        return variation


class MediaVariation(models.Model):
    default_storage_class = getattr(django_settings, 'DEFAULT_FILE_STORAGE',
                                    'django.core.files.storage.FileSystemStorage')
    default_storage = get_callable(default_storage_class)

    fs = default_storage(location=settings.FEINCMS_MEDIALIBRARY_ROOT,
                           base_url=settings.FEINCMS_MEDIALIBRARY_URL)
    
    file = models.FileField(_('file'), max_length=255, upload_to=settings.FEINCMS_MEDIALIBRARY_UPLOAD_TO, storage=fs, blank=True, null=True)
    mediafile = models.ForeignKey(MediaFile, related_name="variations")

    preselector = models.CharField(_('preselector'), max_length=50, choices=(), blank=True, null=True, help_text=_('Choose one of the prepared variation types.'))
    options = JSONField(_('options'), blank=True, null=True)
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    objects = VariationManager()
    
    processors = []
    processors_dict = {}
    
    preselectors = {}
    
    @classmethod
    def register_processors(cls, *processors):
        cls.processors[0:0] = processors
        processors_list = [ (t[0], t[2]) for t in cls.processors ]
        cls.processors_dict = dict(processors_list)
    
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
        
        import pdb;pdb.set_trace()

        
        memfile = self.mediafile.file
        filename = memfile.name
        for command in self.options:
            memfile, name = self.processors_dict[command[0]](memfile, filename, command[1])
        
        content_file = ContentFile(memfile.getvalue())
        memfile.close()
        self.file.save(name, content_file)
        
        return self.file
    
    def clean(self):
        if not self.preselector and not self.processor:
            raise ValidationError(_('Specify either a preselector or a processor'))
        
        if not self.file:
            self.process()
    
MediaVariation.register_processors(
        ('image-cropscale', _('Image cropscale'), image_cropscale),
        ('image-thumbnail', _('Image thumbnail'), image_thumbnail),
        ('image-blur', _('Image blur'), image_blur)
    )