import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import requests, time

time.sleep(1)
base_url = 'http://localhost:5000'

def test_has_key_press_css():
    """HTML should have CSS for button press animation"""
    r = requests.get(f'{base_url}/')
    html = r.text
    assert 'active' in html or 'pressed' in html or 'highlight' in html or 'transform' in html, "No press animation CSS found"

def test_has_button_highlight_class():
    """CSS should define a 'pressed' or 'active' class for buttons"""
    r = requests.get(f'{base_url}/')
    html = r.text
    assert '.pressed' in html or ':active' in html, "No button highlight class found"

def test_keyboard_triggers_visual_feedback():
    """Keyboard handler should call a highlight function alongside each action"""
    r = requests.get(f'{base_url}/')
    html = r.text
    assert 'highlight' in html or 'flash' in html or 'pressed' in html, "Visual feedback function not found"

def test_highlight_uses_animation():
    """Highlight effect should use a CSS animation or transition"""
    r = requests.get(f'{base_url}/')
    html = r.text
    assert 'animation' in html or 'transition' in html, "No animation or transition for button press"

def test_highlight_temporary():
    """Highlight should be temporary (opacity/scale change that reverts)"""
    r = requests.get(f'{base_url}/')
    html = r.text
    # Look for setTimeout or animation-duration
    assert 'setTimeout' in html or 'animation-iteration' in html or 'animation-duration' in html, "No temporary highlight mechanism"

def test_keyboard_handler_finds_button_by_key():
    """Keyboard handler should find and highlight the right button element"""
    r = requests.get(f'{base_url}/')
    html = r.text
    # Should get button reference by text content or dataset
    assert 'querySelector' in html or 'getElementById' in html or 'textContent' in html or "innerText" in html, "No button lookup by key"

if __name__ == '__main__':
    tests = [name for name in dir() if name.startswith('test_')]
    passed = 0
    failed = 0
    for name in tests:
        try:
            globals()[name]()
            print(f"PASS: {name}")
            passed += 1
        except Exception as e:
            print(f"FAIL: {name} - {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)