from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from models import MediaVariation


def media_variation(cls, admin_cls):
    def get_variation(self, processor, options, update=False):
        
        variation, created = self.variations.get_or_create(processor=processor, options=options)
        if created or update:
            variation.process()
        return variation
    
    cls.add_to_class('get_variation', get_variation)
    
    class VariationInline(admin.TabularInline):
        model = MediaVariation
        extra = 0
    admin_cls.inlines.append(VariationInline)
    
    def process_variations(modeladmin, request, queryset):
        for mediafile in queryset:
            for variation in mediafile.variations.all():
                variation.process()
    process_variations.short_description = _('reprocess all variations')
    admin_cls.actions.append(process_variations)

