import unittest

from studio.beats import cut_points, plan_cuts
from studio.captions import Word, ass_time, build_ass, group_lines


class Captions(unittest.TestCase):
    def test_time_format(self):
        self.assertEqual(ass_time(3723.456), "1:02:03.46")

    def test_grouping_splits_on_gap_and_count(self):
        ws = [Word("a", 0, .2), Word("b", .2, .4), Word("c", 2.0, 2.2), Word("d", 2.2, 2.4)]
        self.assertEqual([[w.text for w in l] for l in group_lines(ws)], [["a", "b"], ["c", "d"]])
        many = [Word(str(i), i * .1, i * .1 + .1) for i in range(9)]
        self.assertEqual([len(l) for l in group_lines(many, max_words=4)], [4, 4, 1])

    def test_ass_has_karaoke_tags(self):
        out = build_ass([Word("hi", 0.0, 0.5), Word("there", 0.7, 1.2)])
        self.assertIn("Dialogue: 0,0:00:00.00,0:00:01.35", out)
        self.assertIn("{\\kf50}HI", out)
        self.assertIn("{\\k20}", out)  # silent gap before "there"
        self.assertIn("{\\kf50}THERE", out)


class Beats(unittest.TestCase):
    def test_cut_points_bounds(self):
        pts = cut_points([i * .5 for i in range(1, 20)], total=10.0, every=4)
        self.assertEqual(pts[0], 0.0); self.assertEqual(pts[-1], 10.0)
        self.assertEqual(pts, sorted(pts))

    def test_plan_is_contiguous_and_cycles(self):
        pts = [0, 2, 4, 6, 8]
        segs = plan_cuts(pts, [5.0, 3.0])
        self.assertEqual([s.clip for s in segs], [0, 1, 0, 1])
        self.assertEqual(sum(s.duration for s in segs), 8)
        self.assertEqual([s.timeline_start for s in segs], [0, 2, 4, 6])
        self.assertEqual(segs[2].src_start, 2.0)   # continues where clip 0 left off
        self.assertEqual(segs[3].src_start, 0.0)   # clip 1 (3s) wrapped, not overrun

    def test_empty_clips_rejected(self):
        with self.assertRaises(ValueError):
            plan_cuts([0, 1], [])


if __name__ == "__main__":
    unittest.main()
