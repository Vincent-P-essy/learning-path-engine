import unittest
from path_engine import plan

class PathTests(unittest.TestCase):
    def setUp(self):
        self.c = {'base': {'hours': 1}, 'left': {'hours': 2, 'requires': ['base']}, 'right': {'hours': 3, 'requires': ['base']}, 'goal': {'hours': 4, 'requires': ['right', 'left']}}
    def test_shared_prerequisite_once(self):
        self.assertEqual([x['skill'] for x in plan(self.c, 'goal')], ['base', 'left', 'right', 'goal'])
    def test_completed_skill_removed(self):
        self.assertNotIn('base', [x['skill'] for x in plan(self.c, 'goal', ['base'])])
    def test_unknown_target(self):
        with self.assertRaises(ValueError): plan(self.c, 'missing')
    def test_unknown_prerequisite(self):
        self.c['base']['requires'] = ['missing']
        with self.assertRaises(ValueError): plan(self.c, 'goal')
    def test_cycle_even_if_completed(self):
        self.c['base']['requires'] = ['goal']
        with self.assertRaises(ValueError): plan(self.c, 'goal', self.c.keys())
    def test_invalid_effort(self):
        self.c['base']['hours'] = -1
        with self.assertRaises(ValueError): plan(self.c, 'goal')
