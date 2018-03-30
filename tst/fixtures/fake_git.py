from os.path import *
import tempfile, shutil, os, subprocess

class FakeGit:
    def __init__(self):
        self.path = tempfile.mkdtemp(prefix="fake_git")
        self.url = "file://" + self.path + "/gittology"
        source = os.path.dirname(os.path.realpath(__file__)) + "/test_repo.zip"
        response = subprocess.run(["unzip", "-q", source, "-d", self.path], stdout=subprocess.PIPE)

    def clean_up(self):
        shutil.rmtree(self.path)

