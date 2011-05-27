from django.core.files import File
from django.core.files.images import get_image_dimensions
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from feincms.module.medialibrary.models import MediaFile


class ThumbnailTest(TestCase):
    def setUp(self):
        from extensions import media_variation
        MediaFile.register_extension(media_variation)
        mediafile = MediaFile(file=File(open('feinheit/media_variations/fixtures/elephant_test_image.jpeg')))
        mediafile.save()
        self.image = mediafile
    
    def test_setup(self):
        self.assertEqual(self.image.type, 'image')
        self.assertEqual(get_image_dimensions(self.image.file), (404, 346))
        
    def test_processing(self):
        self.assertEqual(self.image.variations.all().count(), 0)
        thumbnail = self.image.variations.get_by_options('image-thumbnail', {'height' : 34, 'width' : 40})
        self.assertEqual(get_image_dimensions(thumbnail.file), (40, 34))
        self.assertEqual(self.image.variations.all().count(), 1)
        # variations.get_by_options only creates a variation if it does not exists
        self.image.variations.get_by_options('image-thumbnail', {'width' : 40, 'height' : 34})
        self.assertEqual(self.image.variations.all().count(), 1)
        cropscale = self.image.variations.get_by_options('image-cropscale', {'height' : 20, 'width' : 20})
        self.assertEqual(get_image_dimensions(cropscale.file), (20, 20))
        self.assertEqual(self.image.variations.all().count(), 2)
        #blur = self.image.variations.get_by_options('image-blur', {})
        #self.assertEqual(get_image_dimensions(blur.file), (404, 346))
        #self.assertEqual(self.image.variations.all().count(), 3)
    
    def test_templatetags(self):
        from templatetags.mediavariation_thumbnail import thumbnail, cropscale
        
        thumbnail(self.image)
        thumbnail_url = thumbnail(self.image, '24x40q50')
        self.assertEqual(type(thumbnail_url), unicode)
        self.assertTrue('24x40q50' in thumbnail_url)
        
        cropscale(self.image)
        cropscale_url = cropscale(self.image, '24x40q50')
        self.assertEqual(type(cropscale_url), unicode)
        self.assertTrue('24x40q50' in cropscale_url)
        
        ## this test crashes, because in the test enviroment, thumbnail_url has a ../ prefix. in 
        ## realworld, it hasnt
        #response = self.client.get('/' + thumbnail_url)
        #self.assertEqual(response.status_code, 200)
        
    def test_preselection(self):
        from models import MediaVariation
        MediaVariation.register_preselection(
            ('cropscale50x50', _('50px Square Thumbnail'), 'image-cropscale', {'height' : 50, 'width' : 50}),
            ('thumbnail150x99999', _('Max 150px wide image'), 'image-thumbnail', {'height' : 150, 'width' : 99999}),
        )
        processed = self.image.variations.get_by_preselection('cropscale50x50')
        self.assertEqual(get_image_dimensions(processed.file), (50, 50))
        self.assertEqual(processed.processor, 'image-cropscale')
        self.assertEqual(processed.options, {'height' : 50, 'width' : 50})
        
        from templatetags.mediavariation_thumbnail import mediavariation
        variation_url = mediavariation(self.image, 'cropscale50x50')
        self.assertEqual(type(variation_url), unicode)
        self.assertTrue('50x50' in variation_url)
    
    def test_autocreation(self):
        from models import MediaVariation
        MediaVariation.register_preselection(
            ('cropscale50x50', _('50px Square Thumbnail'), 'image-cropscale', {'height' : 50, 'width' : 50}),
            ('thumbnail150x99999', _('Max 150px wide image'), 'image-thumbnail', {'height' : 150, 'width' : 99999}),
        )
        from extensions import auto_creation
        MediaFile.register_extension(auto_creation)
        MediaFile.register_variation_auto_creation('cropscale50x50', 'thumbnail150x99999')
        self.assertEqual(MediaFile.variation_auto_creation, ['cropscale50x50', 'thumbnail150x99999'])
        processed = self.image.variations.get_by_preselection('cropscale50x50')
        self.assertEqual(get_image_dimensions(processed.file), (50, 50))
    
    #def multiprocessors_test(self):
        #thumbnail = self.image.variations.get_by_options(('image-thumbnail', {'height' : 34, 'width' : 40}), 
        #                                     ('image-blur'))
        #self.assertEqual(get_image_dimensions(thumbnail.file), (40, 34))
        #self.assertEqual(self.image.variations.all().count(), 1)
