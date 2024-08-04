import unittest

from nfl_fpca.scraping import scrape_player_ids


class TestScraping(unittest.TestCase):
    def test_pid_count(self):
        pid_set = {'BrowAJ00'}
        with open('test_pages/team.html', 'r') as page:
            self.assertEqual(len(scrape_player_ids(page, pid_set)), 2)


if __name__ == '__main__':
    unittest.main()
