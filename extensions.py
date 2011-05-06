from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from models import MediaVariation


def media_variation(cls, admin_cls):
    def get_variation(self, processor_or_preselection, options=None, update=False):
        if options:
            processor = processor_or_preselection
            variation, created = self.variations.get_or_create(processor=processor, options=options)
        else:
            preselection = processor_or_preselection
            variation, created = self.variations.get_or_create(preselector=preselection)
        
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
        for mediafile in queryset:
            for variation in mediafile.variations.all():
                variation.process()
    process_variations.short_description = _('reprocess all variations')
    admin_cls.actions.append(process_variations)


def auto_creation(cls, admin_cls):
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