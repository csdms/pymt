#! /usr/bin/env python


import unittest
from pymt.nsdict import NamespaceDict


#@unittest.skip('skipping')
class TestNamespaceDict(unittest.TestCase):
    def test_init_without_args(self):
        d = NamespaceDict()
        self.assertDictEqual({}, d)

    def test_init_with_dict(self):
        d = NamespaceDict({'/foo/bar': 'baz', '/foo/baz': 'bar'})
        self.assertDictEqual({'/foo/bar': 'baz', '/foo/baz': 'bar'}, d)

    def test_init_with_tuples(self):
        d = NamespaceDict([('/foo/bar', 'baz'), ('/foo/baz', 'bar')])
        self.assertDictEqual({'/foo/bar': 'baz', '/foo/baz': 'bar'}, d)

    def test_init_with_no_seps(self):
        d = NamespaceDict({'bar': 'baz', 'baz': 'bar'})
        self.assertDictEqual({'/bar': 'baz', '/baz': 'bar'}, d)

    def test_keys(self):
        d = NamespaceDict()
        self.assertSetEqual(set(['/']), d.keys())

        d = NamespaceDict({'/foo/bar': 'baz', '/foo/baz': 'bar'})
        self.assertSetEqual(set(['/', '/foo', '/foo/bar', '/foo/baz']),
                            d.keys())

    def test_len(self):
        d = NamespaceDict()
        self.assertEqual(1, len(d))

        d['/foo/bar'] = 'baz'
        self.assertEqual(3, len(d))

        d['/foo/baz'] = 'baz'
        self.assertEqual(4, len(d))

        d = NamespaceDict()
        d['/f/o/o/b/a/r'] = 'baz'
        self.assertEqual(7, len(d))

    def test_get_item(self):
        d = NamespaceDict([('/foo/bar', 'baz'), ('/foo/baz', 'bar')])

        self.assertEqual('baz', d['/foo/bar'])
        self.assertEqual('bar', d['/foo/baz'])

        with self.assertRaises(KeyError):
            d['bad_key']

    def test_get_func(self):
        d = NamespaceDict([('/foo/bar', 'baz'), ('/foo/baz', 'bar')])

        self.assertEqual('baz', d.get('/foo/bar'))
        self.assertEqual('bar', d.get('/foo/baz'))
        self.assertEqual('foobar', d.get('bad_key', 'foobar'))

        with self.assertRaises(KeyError):
            d.get('bad_key')

    def test_normalize_names_with_trailing_sep(self):
        d = NamespaceDict({'/foo/bar/': 'baz'})

        self.assertTrue('/foo/bar' in d)
        self.assertTrue('/foo/bar/' in d)
        self.assertSetEqual(set(['/foo/bar', '/foo', '/']), d.keys())

        self.assertEqual('baz', d['/foo/bar/'])

    def test_normalize_names_without_leading_sep(self):
        d = NamespaceDict({'foo/bar/': 'baz'})
        self.assertDictEqual({'/foo/bar': 'baz'}, d)
        self.assertEqual('baz', d['foo/bar'])

    def test_normalize_names_double_seps(self):
        d = NamespaceDict({'/foo//bar/': 'baz'})
        self.assertDictEqual({'/foo/bar': 'baz'}, d)
        self.assertEqual('baz', d['/foo//bar'])

    def test_init_with_sep_keyword(self):
        d = NamespaceDict(sep='.')
        d['.foo.bar'] = 'baz'
        self.assertDictEqual({'.foo.bar': 'baz'}, d)

        d = NamespaceDict({'foo.bar': 'baz'}, sep='.')
        self.assertDictEqual({'.foo.bar': 'baz'}, d)

    def test_get_item_that_is_a_dict(self):
        d = NamespaceDict({'/foo/bar': 'baz', '/foo/baz': 'bar'})

        self.assertEqual({'/bar': 'baz', '/baz': 'bar'}, d['/foo'])
        self.assertEqual({'/bar': 'baz', '/baz': 'bar'}, d['/foo/'])
        self.assertEqual({'/foo/bar': 'baz', '/foo/baz': 'bar'}, d['/'])

    def test_repr(self):
        d = NamespaceDict({'/foo/bar': 'baz', '/foo/baz': 'bar'})
        new_d = eval(repr(d))
        self.assertTrue(isinstance(new_d, NamespaceDict))
        self.assertDictEqual({'/foo/bar': 'baz', '/foo/baz': 'bar'}, new_d)

    def test_update(self):
        d = NamespaceDict({'/foo/bar': 'baz'})
        d.update({'/foo/baz': 'bar'})
        self.assertDictEqual({'/foo/bar': 'baz', '/foo/baz': 'bar'}, d)

        d.update({'/foo/bar/': 'bar'})
        self.assertDictEqual({'/foo/bar': 'bar', '/foo/baz': 'bar'}, d)

        d = NamespaceDict()
        d.update((('/foo/bar/', 'baz'), ))
        self.assertDictEqual({'/foo/bar': 'baz'}, d)
        
        d.update(NamespaceDict({'/foo/baz/': 'bar'}))
        self.assertDictEqual({'/foo/bar': 'baz', '/foo/baz': 'bar'}, d)

    def test_contains(self):
        d = NamespaceDict({'/foo/bar': 'baz'})

        self.assertTrue('/foo/bar' in d)
        self.assertTrue('/foo/bar/' in d)
        self.assertTrue('/foo/' in d)
        self.assertTrue('/foo' in d)
        self.assertTrue('/' in d)

    def test_has_key(self):
        d = NamespaceDict({'/foo/bar': 'baz'})

        self.assertTrue('/foo/bar' in d)
        self.assertTrue('/foo/bar/' in d)

    def test_pop_item(self):
        d = NamespaceDict({'/foo/bar': 'baz', '/foo/baz': 'bar'})
        val = d.pop('/foo/bar/')
        self.assertEqual('baz', val)
        self.assertDictEqual({'/foo/baz': 'bar'}, d)
        self.assertSetEqual(set(['/', '/foo', '/foo/baz']), d.keys())
        self.assertEqual(3, len(d))

        val = d.pop('/foo/baz')
        self.assertEqual('bar', val)
        self.assertDictEqual({}, d)
        self.assertEqual(1, len(d))

        val = d.pop('/foo', 'foobar')
        self.assertEqual('foobar', val)
        self.assertDictEqual({}, d)
        self.assertEqual(1, len(d))

    def test_pop_item_with_default(self):
        d = NamespaceDict({'/foo/bar': 'baz', '/foo/baz': 'bar'})
        popped_val = d.pop('/foo/baz/', 'foobar')
        self.assertEqual('bar', popped_val)
        self.assertDictEqual({'/foo/bar': 'baz'}, d)
        self.assertEqual(3, len(d))

        self.assertTrue('foobar', d.pop('/foo/baz/', 'foobar'))
        self.assertEqual(3, len(d))

    def test_pop_dict(self):
        d = NamespaceDict({'/foo/bar': 'baz'})
        self.assertSetEqual(set(['/', '/foo', '/foo/bar']), d.keys())
        popped_val = d.pop('/foo')
        self.assertSetEqual(set(['/', ]), d.keys())
        self.assertEqual(1, len(d))
        self.assertDictEqual({'/bar': 'baz'}, popped_val)
        self.assertIsInstance(popped_val, NamespaceDict)
        self.assertDictEqual({}, d)
        self.assertSetEqual(set(['/']), d.keys())

    def test_pop_everything(self):
        d = NamespaceDict({'/foo/bar': 'baz'})
        popped_val = d.pop('/')
        self.assertEqual(1, len(d))
        self.assertIsInstance(popped_val, NamespaceDict)
        self.assertDictEqual({'/foo/bar': 'baz'}, popped_val)
        self.assertDictEqual({}, d)
        self.assertSetEqual(set(['/']), d.keys())

    def test_deep_names(self):
        d = NamespaceDict()
        d['/f/o/o/b/a/r'] = 'baz'
        d['/f/o/o/b/a/z'] = 'bar'

        self.assertEqual(8, len(d))

        d['/b/a/z/b/a/r'] = 'foo'
        self.assertEqual(14, len(d))

        popped_val = d.pop('/f/o/o/')
        self.assertDictEqual({'/b/a/r': 'baz', '/b/a/z': 'bar'}, popped_val)
        self.assertEqual(5, len(popped_val))

        self.assertDictEqual({'/b/a/z/b/a/r': 'foo'}, d)
        self.assertEqual(7, len(d))

    def test_reset_value(self):
        d = NamespaceDict()
        d['/f/o/o'] = 'bar'
        self.assertDictEqual({'/f/o/o': 'bar'}, d)
        self.assertEqual(4, len(d))

        d['/f/o/o/b/a/r'] = 'baz'
        self.assertDictEqual({'/f/o/o/b/a/r': 'baz'}, d)
        self.assertEqual(7, len(d))

        d['/f'] = 'foobar'
        self.assertDictEqual({'/f': 'foobar'}, d)
        self.assertEqual(2, len(d))

class TestNamespaceDictPrivates(unittest.TestCase):
    def test_iter_paths(self):
        d = NamespaceDict()
        paths = [path for path in d._iter_paths('/')]
        self.assertListEqual(['/'], paths)

        paths = [path for path in d._iter_paths('/f/o/o/')]
        self.assertListEqual(['/', '/f', '/f/o', '/f/o/o', ], paths)

        paths = [path for path in d._iter_paths('/f/o/o')]
        self.assertListEqual(['/', '/f', '/f/o', '/f/o/o', ], paths)

    def test_paths(self):
        d = NamespaceDict()
        self.assertSetEqual(set(['/']), d._paths('/'))

        self.assertSetEqual(set(['/', '/f', '/f/o', '/f/o/o', ]),
                            d._paths('/f/o/o/'))

        self.assertSetEqual(set(['/', '/f', '/f/o', '/f/o/o', ]),
                            d._paths('/f/o/o'))


    def test_sub_paths(self):
        d = NamespaceDict()
        d['/f/o/o/b/a/r'] = 'baz'
        d['/f/o/o/b/a/z'] = 'bar'
        self.assertSetEqual(set(['', 'f', 'f/o', 'f/o/o', 'f/o/o/b',
                             'f/o/o/b/a', 'f/o/o/b/a/r', 'f/o/o/b/a/z',]),
                            set(d._sub_paths('/')))
        self.assertSetEqual(set(['', 'b', 'b/a', 'b/a/r', 'b/a/z', ]),
                            set(d._sub_paths('/f/o/o')))
        self.assertSetEqual(set([]), set(d._sub_paths('/foo')))

        d = NamespaceDict({'/foo/bar': 'baz', '/foo/baz': 'bar'})
        self.assertSetEqual(set(['', 'bar', 'baz']), set(d._sub_paths('/foo')))
        d = NamespaceDict({'/f/r': 'baz', '/f/z': 'bar'})
        self.assertSetEqual(set(['', 'f', 'f/r', 'f/z',]), set(d._sub_paths('/')))
        self.assertSetEqual(set(['', 'f', 'f/r', 'f/z',]), set(d._sub_paths('')))

    def test_split(self):
        d = NamespaceDict()
        self.assertListEqual(['foo', 'bar'], d._split('/foo/bar'))
        self.assertListEqual(['foo', 'bar', 'baz'], d._split('/foo/bar/baz/'))
        self.assertListEqual(['foo', 'bar'], d._split('foo//bar'))
        self.assertListEqual([], d._split('/'))

    def test_norm(self):
        d = NamespaceDict()
        self.assertEqual('/', d._norm('/'))
        self.assertEqual('/foo', d._norm('/foo'))
        self.assertEqual('/foo', d._norm('/foo/'))
        self.assertEqual('/foo/bar', d._norm('/foo//////bar//'))

    def test_join(self):
        d = NamespaceDict()
        self.assertEqual('/foo', d._join('', 'foo'))

    def test_leaves(self):
        d = NamespaceDict()
        self.assertSetEqual(set(), d._leaves())
        d['/f/o/o/r'] = 'bar'
        self.assertSetEqual(set(['/f/o/o/r']), d._leaves())

        d['/f/o/o/z'] = 'baz'
        self.assertSetEqual(set(['/f/o/o/r', '/f/o/o/z']), d._leaves())

    def test_references(self):
        d = NamespaceDict()
        self.assertDictEqual({'/': 1}, d._ref_count)
        d['/f/o/o/r'] = 'bar'
        self.assertDictEqual({'/': 2, '/f': 1, '/f/o': 1, '/f/o/o': 1,
                              '/f/o/o/r': 1}, d._ref_count)
        del d['/f/o/o/r']
        self.assertDictEqual({'/': 1}, d._ref_count)

        d['/f/o/o/r'] = 'bar'
        del d['/f/o']
        self.assertDictEqual({'/': 1}, d._ref_count)

        d['/f/o/o/r'] = 'bar'
        d['/f/o/o/z'] = 'baz'
        self.assertDictEqual({'/': 3, '/f': 2, '/f/o': 2, '/f/o/o': 2,
                              '/f/o/o/r': 1, '/f/o/o/z': 1}, d._ref_count)

        del d['/f/o']
        self.assertDictEqual({'/': 1}, d._ref_count)
