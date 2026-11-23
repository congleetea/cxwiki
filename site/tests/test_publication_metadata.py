from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_blog as blog

class PublicationMetadataTest(unittest.TestCase):
    def page(self, **meta):
        return blog.Page(Path('/tmp/source.md'), blog.SITE/'example.html', meta, 'Example', 'concept', '')

    def test_publication_month_precedes_institution(self):
        markup = blog.card(self.page(published='2025-11-11', institution='NVIDIA'), blog.SITE/'index.html')
        self.assertIn('2025年11月', markup)
        self.assertLess(markup.index('2025年11月'), markup.index('NVIDIA'))
        self.assertIn('datetime="2025-11"', markup)

    def test_updated_date_is_not_used_as_publication_date(self):
        markup = blog.card(self.page(last_updated='2026-11-23', institution='NVIDIA'), blog.SITE/'index.html')
        self.assertNotIn('2026年11月', markup)

    def test_organization_placeholders_are_omitted(self):
        for institution in ['', '综述', '多机构', '多机构 · 概念教程']:
            with self.subTest(institution=institution):
                markup = blog.card(self.page(institution=institution), blog.SITE/'index.html')
                self.assertNotIn('card-institution', markup)

    def test_month_precision_without_institution(self):
        markup = blog.card(self.page(published='2026-11'), blog.SITE/'index.html')
        self.assertIn('2026年11月', markup)
        self.assertNotIn(' · </div>', markup)

if __name__ == '__main__':
    unittest.main()
