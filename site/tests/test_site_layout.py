"""Website sources and build output must stay inside the site project."""
from pathlib import Path
import unittest

class SiteLayoutTest(unittest.TestCase):
    def test_generated_site_has_no_duplicate_order_file(self):
        site = Path(__file__).resolve().parents[1]
        self.assertTrue((site / 'article-order.json').is_file())
        if (site / 'public/index.html').is_file():
            self.assertFalse((site / 'public/article-order.json').exists())

    def test_website_sources_are_contained_in_site(self):
        root = next(parent for parent in Path(__file__).resolve().parents if (parent/".git").exists())
        for name in ['build.sh', 'requirements.txt', 'scripts/build_blog.py', 'scripts/deploy_tx.sh', 'scripts/blog.js', 'deploy/cxwiki.nginx.conf']:
            self.assertTrue((root/'site'/name).is_file(), name)
        self.assertFalse((root/'build.sh').exists())
        self.assertFalse((root/'deploy').exists())
        import build_blog
        self.assertEqual(build_blog.SITE, root/'site/public')

if __name__ == '__main__':
    unittest.main()
