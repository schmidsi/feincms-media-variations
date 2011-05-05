from django.core.files import File
from django.core.files.images import get_image_dimensions
from django.test import TestCase

from feincms.module.medialibrary.models import MediaFile

from extensions import media_variation


class ThumbnailTest(TestCase):
    def setUp(self):
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
