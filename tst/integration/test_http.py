from .flask_test_case import FlaskTestCase

import unittest

failing_commit = "a72c20ff"
success_commit = "992d00dc0"
success_branch = "success"
failing_pr_branch = "pr/1/merge"

class IntegrationTestHttp(FlaskTestCase):
    def setUp(self):
        super(IntegrationTestHttp, self).setUp()
        self.url = "emfcamp/Mk4-Apps"

    def test_references(self):
        data = self.get_json("/refs?repo=%s" % self.url)
        self.assertTrue("master" in data['refs'])
        self.assertTrue("success" in data['refs'])

    def test_prs(self):
        data = self.get_json("/prs?repo=%s" % self.url)
        self.assertTrue(len(data) > 0)

    def test_refs_checkout_with_error(self):
        data = self.get("/library?repo=%s&ref=%s" % (self.url, failing_commit))
        self.assertIn("invalid syntax (main.py, line 11)", data)

    def test_check_checkout_with_error(self):
        data = self.get("/check?repo=%s&ref=%s" % (self.url, failing_commit))
        self.assertIn("invalid syntax (main.py, line 11)", data)

    def test_check_succeed(self):
        data = self.get("/check?repo=%s&ref=%s" % (self.url, success_commit))
        self.assertIn("PASS", data)

    def test_checkout_with_different_branch(self):
        data = self.get_json("/library?repo=%s&ref=%s" % (self.url, success_branch))
        self.assertIn("Some minor change", data['resources']['app_library']['description']);

    def test_github_merge_commit(self):
        data = self.get("/check?repo=%s&ref=%s" % (self.url, failing_pr_branch))
        self.assertIn("invalid syntax (main.py, line 11)", data)

    def test_categories(self):
        data = self.get_json("/apps?repo=%s&ref=%s" % (self.url, "992d00dc0"))
        print(data)
        self.assertEqual(set(data['System']), set(['settings', 'launcher', 'app_library']))

    def test_install(self):
        data = self.get_json("/install?repo=%s&ref=%s&apps=launcher,app_library" % (self.url, success_commit))
        self.assertDictEqual(data, {'app_library/main.py': 'f57620a4d1', 'boot.py': 'ff8bc259a2', 'launcher/main.py': '2b1477ee36', 'lib/buttons.py': '3fc83d019a', 'lib/dialogs.py': '149678101a', 'lib/wifi.py': 'abe69b0fb1'})

    def test_bootstrap(self):
        data = self.get_json("/bootstrap?repo=%s&ref=%s" % (self.url, success_commit))
        self.assertIn("boot.py", data)
        self.assertIn("lib/wifi.py", data)

    #def test_flash(self):
    #    data = self.get_json("/flash?repo=%s&ref=%s" % (self.url, success_commit))
    #    self.assertIn("boot.py", data)
    #    self.assertIn("bootstrap/main.py", data)

    def test_download(self):
        data = self.get("/download?repo=%s&ref=%s&path=lib/buttons.py" % (self.url, success_commit))
        self.assertIn("Convenience methods for dealing with the TiLDA buttons", data)

    def test_app_info(self):
        data = self.get_json("/app?repo=%s&ref=%s&app=launcher" % (self.url, success_commit))
        print(data)
        self.assertEqual(data['description'], 'Launcher for apps currently installed')


if __name__ == '__main__':
    unittest.main()
