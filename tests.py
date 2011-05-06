from django.core.files import File
from django.core.files.images import get_image_dimensions
from django.test import TestCase

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
        thumbnail = self.image.get_variation('image-thumbnail', {'height' : 34, 'width' : 40})
        self.assertEqual(get_image_dimensions(thumbnail.file), (40, 34))
        self.assertEqual(self.image.variations.all().count(), 1)
        # get_variation only creates a variation if it does not exists
        self.image.get_variation('image-thumbnail', {'width' : 40, 'height' : 34})
        self.assertEqual(self.image.variations.all().count(), 1)
        cropscale = self.image.get_variation('image-cropscale', {'height' : 20, 'width' : 20})
        self.assertEqual(get_image_dimensions(cropscale.file), (20, 20))
        self.assertEqual(self.image.variations.all().count(), 2)
    
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
