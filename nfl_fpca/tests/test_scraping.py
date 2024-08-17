import unittest

from ..scraping.team_scrapper import scrape_player_ids
from ..scraping.player_scrapper import scrape_player_page


class TestTeamScraping(unittest.TestCase):

    def test_empty(self):
        page = "<!DOCTYPE html><html><head></head><body></body></html>"
        pid_set = set()
        temp_set = scrape_player_ids(page, pid_set)

        self.assertEqual(len(temp_set), 0)

    def test_full(self):
        pid_set = {"BrowAJ00"}
        with open("nfl_fpca/tests/test_pages/team/team.html") as page:
            temp_set = scrape_player_ids(page, pid_set)

            self.assertEqual(len(temp_set), 2)
            self.assertNotIn("BrowAJ00", temp_set)
            self.assertIn("BarkSa00", temp_set)
            self.assertIn("BaunZa00", temp_set)


class TestPlayerScraping(unittest.TestCase):

    def setUp(self):
        with open("nfl_fpca/tests/test_pages/player/player_full.html") as full_page:
            self.player_full = scrape_player_page(full_page, 'TEST')

    def test_header(self):
        self.assertEqual(self.player_full.name, "A.J. Brown")
        self.assertEqual(self.player_full.position, "WR")
        self.assertEqual(self.player_full.height, 185)
        self.assertEqual(self.player_full.weight, 102)

    def test_career_stats(self):
        stats, time = self.player_full.get_stats_array('gp', 'gs', 'av')
        # Check stats
        self.assertEqual(stats['gp'], [10, 12, 16, 16])
        self.assertEqual(stats['gs'], [0, 10, 15, 16])
        self.assertEqual(stats['av'], [3, 6, 12, 11])
        self.assertEqual(time, [2019, 2021, 2022, 2023])
        # Check other info
        self.assertEqual(self.player_full.start_year, 2019)
        self.assertEqual(self.player_full.start_age, 23)
        self.assertEqual(self.player_full.last_year, 2023)

    def test_combine(self):
        self.assertEqual(self.player_full.dash, 4.76)
        self.assertEqual(self.player_full.bench, 24)
        self.assertEqual(self.player_full.broad, 0)
        self.assertEqual(self.player_full.shuttle, 4.47)
        self.assertEqual(self.player_full.cone, 7.08)
        self.assertEqual(self.player_full.vertical, 30.5)


if __name__ == '__main__':
    unittest.main()
