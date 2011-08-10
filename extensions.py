from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from models import MediaVariation


def media_variation(cls, admin_cls):
    """ extension for FeinCMS MediaFile, which adds mainly the function ``get_variation``.
    insert also a tabular inline into the MediaFile Admin, to admin the variations """
    
    def get_variation(self, processor_or_preselection, options=None, update=False):
        """ returns the requested variation. there are 2 usecases:
        #. a processor and options are given
        #. a preselection is given
        if the requested variation already exists, return this. """
        
        if options:
            processor = processor_or_preselection
            variation, created = self.variations.get_or_create(processor=processor, options=options)
        else:
            preselection = processor_or_preselection
            variation, created = self.variations.get_or_create(preselector=preselection)
            if variation.options != MediaVariation.preselectors[preselection][1]:
                update = True
        
        if created or update:
            variation.process()
        return variation
    
    cls.add_to_class('get_variation', get_variation)
    
    class VariationInline(admin.TabularInline):
        model = MediaVariation
        extra = 0
        readonly_fields = ('processor', 'options')
    admin_cls.inlines.append(VariationInline)
    
    def process_variations(modeladmin, request, queryset):
        """ adminaction to reprocess all variations. use with care, because it will override user 
        replaced variation with the processed one """
        
        for mediafile in queryset:
            for variation in mediafile.variations.all():
                variation.process()
    process_variations.short_description = _('reprocess all variations')
    admin_cls.actions.append(process_variations)


def auto_creation(cls, admin_cls):
    """ extenstion for FeinCMS MediaFile to enable autocreation. autocreation creates automatically
    variations if a new mediafile is created (only via admin). """
    
    @classmethod
    def register_variation_auto_creation(cls, *auto_creation):
        cls.variation_auto_creation.extend(auto_creation)
    
    cls.add_to_class('variation_auto_creation', [])
    cls.add_to_class('register_variation_auto_creation', register_variation_auto_creation)
    
    super_save_model = admin_cls.save_model
    def save_model(self, request, obj, form, change):
        for auto_creation in obj.variation_auto_creation:
            obj.get_variation(auto_creation)
        super_save_model(self, request, obj, form, change)
    admin_cls.save_model = save_model