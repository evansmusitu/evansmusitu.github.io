import sys
from pathlib import Path
from xml.etree import ElementTree
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from sitemap import make_sitemap

def test_public_template_excludes_404_and_conditional_pages():
 xml,inc=make_sitemap('https://example.invalid')
 assert len(inc)==34-1-5
 assert '/404/' not in inc and '/status/' not in inc and '/' in inc
 assert b'https://example.invalid/products/axiom/' in xml
 ElementTree.fromstring(xml)

def test_clear_only_individually_released_conditional_route():
 xml,inc=make_sitemap('https://example.invalid',cleared_routes=['/legal/privacy/'])
 assert len(inc)==29
 assert '/legal/privacy/' in inc and '/status/' not in inc

def test_reject_unapproved_origin_shape_and_extra_clearance():
 for s in ['http://example.invalid','https://example.invalid/sub','https://user:pass@example.invalid','https://example.invalid:8443','https://example.invalid/?x=1']:
  with pytest.raises(ValueError):make_sitemap(s)
 with pytest.raises(ValueError):make_sitemap('https://example.invalid',['/products/axiom/'])
