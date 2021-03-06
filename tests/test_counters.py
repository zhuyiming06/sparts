# Copyright (c) 2014, Facebook, Inc.  All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from sparts.tests.base import BaseSpartsTestCase
from sparts import counters

import time

class CounterTests(BaseSpartsTestCase):
    def testSum(self):
        """Test `counters.Sum()"""
        c = counters.Sum()
        self.assertEquals(c(), 0.0)
        c.increment()
        self.assertEquals(c(), 1.0)
        c.incrementBy(10)
        self.assertEquals(c(), 11.0)
        c.add(10)
        self.assertEquals(c(), 21.0)

        # Test some other types
        self.assertEquals(int(c), 21)
        self.assertEquals(float(c), 21.0)
        self.assertEquals(str(c), '21.0')

        # Test reset API
        c.reset(0.5)
        self.assertEquals(float(c), 0.5)

    def testCount(self):
        """Test `counters.Count()"""
        c = counters.Count()
        self.assertEquals(c(), 0)
        c.add(100)
        self.assertEquals(c(), 1)

    def testMax(self):
        """Test `counters.Max()"""
        c = counters.Max()
        self.assertIs(c(), None)
        c.add(-10)
        self.assertEquals(c(), -10)
        c.add(-20)
        self.assertEquals(c(), -10)
        c.add(20)
        self.assertEquals(c(), 20)

    def testMin(self):
        """Test `counters.Min()"""
        c = counters.Min()
        self.assertIs(c(), None)
        c.add(-10)
        self.assertEquals(c(), -10)
        c.add(20)
        self.assertEquals(c(), -10)
        c.add(-20)
        self.assertEquals(c(), -20)

    def testAverage(self):
        """Test `counters.Average()"""
        c = counters.Average()
        self.assertEquals(c(), None)
        c.add(10)
        c.add(20)
        self.assertEquals(c(), 15.0)


    def testSampleNames(self):
        """Test `counters.Samples() getCounters API, etc"""
        c = counters.samples(name='foo',
            types=[counters.SampleType.COUNT], windows=[100])
        c.add(1)
        self.assertEquals(c.getCounter('foo.count.100'), 1)

        c = counters.samples(
            types=[counters.SampleType.COUNT], windows=[100])
        c.add(1)
        self.assertEquals(c.getCounter('count.100'), 1)

    def testSamples(self):
        c = counters.samples(
            types=[counters.SampleType.COUNT, counters.SampleType.SUM],
            windows=[100, 1000])

        now = time.time()
        c._now = self.mock.Mock()

        # At t=0, add two values of 10.0
        c._now.return_value = now
        c.add(10.0)
        c.add(10.0)

        self.assertEquals(c.getCounter('count.100'), 2)
        self.assertEquals(c.getCounter('count.1000'), 2)
        self.assertEquals(c.getCounter('sum.100'), 20.0)
        self.assertEquals(c.getCounter('sum.1000'), 20.0)

        # Make sure there are only four counters
        self.assertEquals(len(c.getCounters()), 4)

        # At t=10, add one values of 10.0
        c._now.return_value = now + 10
        c.add(10.0)

        self.assertEquals(c.getCounter('count.100'), 3)
        self.assertEquals(c.getCounter('count.1000'), 3)
        self.assertEquals(c.getCounter('sum.100'), 30.0)
        self.assertEquals(c.getCounter('sum.1000'), 30.0)

        # At t=101, 2 values should have fallen out of the 100 window
        c._now.return_value = now + 101

        self.assertEquals(c.getCounter('count.100'), 1)
        self.assertEquals(c.getCounter('count.1000'), 3)
        self.assertEquals(c.getCounter('sum.100'), 10.0)
        self.assertEquals(c.getCounter('sum.1000'), 30.0)

        # At t=1001, all values should be gone from the 100 window,
        # but one value should remain in the 1000 window
        c._now.return_value = now + 1001

        self.assertEquals(c.getCounter('count.100'), 0)
        self.assertEquals(c.getCounter('count.1000'), 1)
        self.assertEquals(c.getCounter('sum.100'), 0.0)
        self.assertEquals(c.getCounter('sum.1000'), 10.0)

        # At t=1011, all values should be gone from all windows.
        c._now.return_value = now + 1011

        self.assertEquals(c.getCounter('count.100'), 0)
        self.assertEquals(c.getCounter('count.1000'), 0, str((now, c.samples)))
        self.assertEquals(c.getCounter('sum.100'), 0.0)
        self.assertEquals(c.getCounter('sum.1000'), 0.0)

