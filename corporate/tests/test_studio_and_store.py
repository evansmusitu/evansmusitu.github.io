from pathlib import Path
import json
import pytest
from scripts.build import add_protected_studio_player, protected_studio_media_ready

ROOT=Path(__file__).resolve().parents[1]
STORE='https://chatgpt.com/plugins/plugin_asdk_app_6ae058ee6cec81919329ae43b76a4c86'

def test_direct_chatgpt_destination_with_access_context():
    pages=json.loads((ROOT/'content/pages.json').read_text())
    for route in ('/', '/products/axiom/'):
        assert STORE in pages[route]['main']
        assert 'rel="noopener noreferrer"' in pages[route]['main']
    assert 'has not been independently confirmed' in pages['/products/axiom/']['main']

def test_staging_media_is_opt_in(monkeypatch):
    monkeypatch.delenv('MUSITU_PROTECTED_STAGING_MEDIA',raising=False)
    assert protected_studio_media_ready() is False
    monkeypatch.setenv('MUSITU_PROTECTED_STAGING_MEDIA','2')
    with pytest.raises(ValueError):
        protected_studio_media_ready()

def test_video_gate_to_real_video_player():
    pages=json.loads((ROOT/'content/pages.json').read_text())
    for route in ('/products/foundry/studio/', '/experiences/lab/'):
        source=pages[route]['main']
        assert 'video-clearance-gate' in source
        result=add_protected_studio_player(source)
        assert 'video-clearance-gate' not in result
        assert 'studio-demo-82s.mp4' in result
        assert 'studio-poster.png' in result
        assert 'controls' in result and 'preload="metadata"' in result
