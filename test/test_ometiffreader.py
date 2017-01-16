# #%L
# OME-FILES Python library for image IO.
# Copyright (c) 2016 University of Dundee
# %%
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# #L%

import os
import uuid
import unittest

import ome_files


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(THIS_DIR, "data", "multi-channel-4D-series.ome.tif")
IMG_PATH_16 = os.path.join(THIS_DIR, "data", "P-TRE_10_R3D_D3D_Z30_C1.ome.tif")

# A-priori knowledge from the Java lib (showinf)
SERIES_COUNT = 1
IMAGE_COUNT = 105
SIZE_X = 439
SIZE_Y = 167
SIZE_Z = 5
SIZE_T = 7
SIZE_C = 3
BYTES_PER_PIXEL = 1
PIXEL_TYPE = "i1"  # int8
RGB_C_COUNT = 1
INTERLEAVED = False


class NotABool(object):
    def __nonzero__(self):
        raise NotImplementedError("truth value is undefined")


class TestOMETiffReader(unittest.TestCase):

    def assertPathEqual(self, p1, p2, msg=None):
        self.assertEqual(os.path.realpath(p1), os.path.realpath(p2), msg=msg)

    def setUp(self):
        self.reader = ome_files.OMETIFFReader()

    def test_image_count(self):
        self.assertRaises(ome_files.Error, self.reader.get_image_count)
        self.reader.set_id(IMG_PATH)
        self.assertEqual(self.reader.get_image_count(), IMAGE_COUNT)
        self.reader.close(file_only=True)
        self.assertEqual(self.reader.get_image_count(), IMAGE_COUNT)
        self.reader.close()
        self.assertRaises(ome_files.Error, self.reader.get_image_count)

    def test_series_count(self):
        self.assertRaises(ome_files.Error, self.reader.get_series_count)
        self.reader.set_id(IMG_PATH)
        self.assertEqual(self.reader.get_series_count(), SERIES_COUNT)
        self.reader.close()
        self.assertRaises(ome_files.Error, self.reader.get_series_count)

    def test_series(self):
        self.assertRaises(ome_files.Error, self.reader.set_series, 0)
        self.reader.set_id(IMG_PATH)
        self.assertRaises(TypeError, self.reader.set_series, 0.)
        self.reader.set_series(0)
        self.assertEqual(self.reader.get_series(), 0)
        self.reader.close()
        self.assertRaises(ome_files.Error, self.reader.set_series, 0)

    def test_dimensions(self):
        for dim in "xyztc":
            meth = getattr(self.reader, "get_size_%s" % dim)
            self.assertRaises(ome_files.Error, meth)
        self.reader.set_id(IMG_PATH)
        self.assertEqual(self.reader.get_size_x(), SIZE_X)
        self.assertEqual(self.reader.get_size_y(), SIZE_Y)
        self.assertEqual(self.reader.get_size_z(), SIZE_Z)
        self.assertEqual(self.reader.get_size_t(), SIZE_T)
        self.assertEqual(self.reader.get_size_c(), SIZE_C)
        self.reader.close()
        for dim in "xyztc":
            meth = getattr(self.reader, "get_size_%s" % dim)
            self.assertRaises(ome_files.Error, meth)

    def test_pixel_type(self):
        self.assertRaises(ome_files.Error, self.reader.get_pixel_type)
        self.reader.set_id(IMG_PATH)
        self.assertEqual(self.reader.get_pixel_type(), PIXEL_TYPE)
        self.reader.close()
        self.assertRaises(ome_files.Error, self.reader.get_pixel_type)

    def test_bad_id(self):
        filename = str(uuid.uuid4())
        self.assertRaises(ome_files.Error, self.reader.set_id, filename)
        self.assertRaises(TypeError, self.reader.set_id, 0)

    def test_bad_close(self):
        self.reader.set_id(IMG_PATH)
        self.assertRaises(TypeError, self.reader.close, NotABool())
        self.reader.close()

    def test_rgb_channel_count(self):
        self.assertRaises(ome_files.Error,
                          self.reader.get_rgb_channel_count, 0)
        self.reader.set_id(IMG_PATH)
        self.assertRaises(TypeError, self.reader.get_rgb_channel_count, 0.)
        self.assertEqual(self.reader.get_rgb_channel_count(0), RGB_C_COUNT)
        self.reader.close()
        self.assertRaises(ome_files.Error,
                          self.reader.get_rgb_channel_count, 0)

    def test_interleaved(self):
        self.assertRaises(ome_files.Error, self.reader.is_interleaved, 0)
        self.reader.set_id(IMG_PATH)
        self.assertRaises(TypeError, self.reader.is_interleaved, 0.)
        self.assertEqual(self.reader.is_interleaved(0), INTERLEAVED)
        self.reader.close()
        self.assertRaises(ome_files.Error, self.reader.is_interleaved, 0)

    def test_open_bytes(self):
        self.assertRaises(ome_files.Error, self.reader.open_bytes, 0)
        self.reader.set_id(IMG_PATH)
        self.assertRaises(TypeError, self.reader.open_bytes, 0.)
        raw = self.reader.open_bytes(0)
        self.assertEqual(len(raw), SIZE_X * SIZE_Y * BYTES_PER_PIXEL)
        self.reader.close()
        self.assertRaises(ome_files.Error, self.reader.open_bytes, 0)

    def test_open_bytes_multibyte(self):
        size_x = size_y = 512
        bytes_per_pixel = 2
        self.reader.set_id(IMG_PATH_16)
        raw = self.reader.open_bytes(0)
        self.assertEqual(len(raw), size_x * size_y * bytes_per_pixel)
        self.reader.close()

    def test_used_files(self):
        self.assertRaises(ome_files.Error, self.reader.get_used_files)
        self.reader.set_id(IMG_PATH)
        self.assertRaises(TypeError, self.reader.get_used_files, NotABool())
        fnames = self.reader.get_used_files()
        self.assertEqual(len(fnames), 1)
        self.assertPathEqual(fnames[0], IMG_PATH)
        self.assertEqual(len(self.reader.get_used_files(no_pixels=True)), 0)
        self.reader.close()
        self.assertRaises(ome_files.Error, self.reader.get_used_files)


def load_tests(loader, tests, pattern):
    test_cases = (TestOMETiffReader,)
    suite = unittest.TestSuite()
    for tc in test_cases:
        suite.addTests(loader.loadTestsFromTestCase(tc))
    return suite


if __name__ == '__main__':
    suite = load_tests(unittest.defaultTestLoader, None, None)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
