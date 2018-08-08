import requests, re
from app.util import memcached

repo_pattern = re.compile("([-_\\w]+)\\/([-_.\\w]+)")

class Github:
    def __init__(self, repo, mc=memcached.shared):
        if not re.match(repo_pattern, repo):
            raise Exception("Invalid repo, please use 'owner/repo_name'")
        self.repo = repo
        self.mc = mc

    def get_prs(self):
        key = "github_prs::" + self.repo
        prs = self.mc.get(key)
        if prs:
            return prs

        params = {"state": "open", "sort": "update", "direction": "desc"}
        response = requests.get('https://api.github.com/repos/%s/pulls' % self.repo, params=params)
        response.raise_for_status()
        response = response.json()

        prs = []
        for pr in response:
            title = pr["title"]
            short_title = (title[:20] + '..') if len(title) > 20 else title
            prs.append({
                "number": pr["number"],
                "title": short_title,
                "repo": self.repo,
                "ref": "pr/%s/merge" % pr["number"],
                "user": pr["user"]["login"]
            })
            if len(prs) > 20:
                break

        self.mc.set(key, prs, time=60)
        return prs


