def media_variation(cls, admin_cls):
    def get_variation(self, processor, options, update=False):
        
        variation, created = self.variations.get_or_create(processor=processor, options=options)
        if created or update:
            variation.process(options)
        return variation
    
    cls.add_to_class('get_variation', get_variation)

