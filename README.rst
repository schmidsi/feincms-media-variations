========================
FeinCMS Media Variations
========================

Tools to extend the FeinCMS MediaFile with variations.


Idea
====

A MediaFile can have a variation. Simple example: an image has a thubnail. But there are other use
cases for MediaFile variations: 
- An audiofile has a snipped, or low quality version, or version in other encoding
- Same for a video. But a video can also have a preview image.
- A PDF can also have a preview image

FeinCMS Media Variations is the basic framework to support this


Functionality
=============

The feincms MediaFile is extended with a Variation Model. One MediaFile can have multiple variations.
A variation is computed through a processor, which can be controlled through some options.

If a variation of a MediaFile is requested, there will be first a lookup, if this variation already exists.
If not, the variation will be computed. If it already exists, the already computed variation will be given.
Once a variation is created, it can be changed by the user. F.e. if we have a cropscale of an image, the crop
is maybe bad (because it is computed). The user can now replace the cropscale with a nicer image. If
the same variation is requested again, the user replaced image will be given.

To simplify the process, there are preselections. a preselection is a variation processor bundled with
some options. F.e. if we need a 50px square of a user image several times, we can write a preselection
named 'small_square', which calls the processor 'thumbnail' with the options {'height': 50, 'width': 50}

optionally, one can activate autocreation, to automatically create preselections if a MediaFile is created.
by default, variations are created on the fly as they are requested.


Usage
=====


- add :mod:`feincms_media_variations` to your :setting:`INSTALLED_APPS`
- run  ``python manage.py syncdb`` because a new table will be created
- monkey-patch the MediaFile Class. best in  ``models.py`` of the base app (to be organized)::

    from feincms.module.medialibrary.models import MediaFile
    from feincms_media_variations.extensions import media_variation
    MediaFile.register_extension(media_variation)

- if you want to define some preselections, here is an example::

    from models import MediaVariation
    MediaVariation.register_preselection(
        ('cropscale50x50', _('50px Square Thumbnail'), 'image-cropscale', {'height' : 50, 'width' : 50}),
        ('thumbnail150x99999', _('Max 150px wide image'), 'image-thumbnail', {'height' : 150, 'width' : 99999}),
    )

- if you want to activate autocreation, write something like this::

    from feinheit.media_variations.extensions import auto_creation
    MediaFile.register_extension(auto_creation)
    MediaFile.register_variation_auto_creation('cropscale50x50', 'thumbnail150x99999')


TODO
====

- refactor code: f.e. redundant code in processors.py
- multiple processors per MediaVariation
- processors should check, if they can handle a mediafile type (cropscaling audiofiles should throw some error)
