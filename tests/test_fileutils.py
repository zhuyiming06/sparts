# Copyright (c) 2014, Facebook, Inc.  All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from sparts.tests.base import BaseSpartsTestCase
from sparts import fileutils

import os.path
import shutil

class NamedTemporaryDirTests(BaseSpartsTestCase):
    def testPathHelpers(self):
        with fileutils.NamedTemporaryDirectory() as d:
            # Make sure a file, `foo`, doesn't exist yet.
            self.assertNotExists(os.path.join(d.name, 'foo'))

            # Write it, make sure it's there, and verify the contents
            d.writefile('foo', 'bar')
            self.assertExists(os.path.join(d.name, 'foo'))
            self.assertEquals(d.readfile('foo'), 'bar')

            # Symlink it, and make sure that is correct as well
            d.symlink('spam', d.join('foo'))
            self.assertExists(os.path.join(d.name, 'spam'))
            self.assertEquals(d.readfile('spam'), 'bar')

            # Makedirs
            d.makedirs('adir')
            self.assertTrue(os.path.exists(d.join('adir')))
            self.assertTrue(os.path.isdir(d.join('adir')))

            # Save the tempdir path
            tmpdir_path = d.name
            self.assertExists(d.name)

        # Verify things have gotten cleaned up
        self.assertNotExists(tmpdir_path)

    def testKeepAfterClose(self):
        """Verify various auto-cleanup methods."""
        with fileutils.NamedTemporaryDirectory() as d:
            tmpdir_path = d.name
            self.assertExists(d.name)
            d.keep()

        # We called `.keep()`, so it should still be around.
        self.assertExists(tmpdir_path)

        # Remove manually and verify
        shutil.rmtree(tmpdir_path)
        self.assertNotExists(tmpdir_path)

        # TODO: Verify `.close()`, `__del__()`

    def testMisc(self):
        with fileutils.NamedTemporaryDirectory() as d:
            # Verify __repr__()
            self.assertIn(d.name, repr(d))
