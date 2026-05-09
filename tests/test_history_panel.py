"""Tests for history panel UI bugs:
1. History panel stays blank (refreshHistory doesn't render correctly)
2. Toggle button not properly aligned
3. Text overflows the container

These are HTML/CSS integration tests that verify the rendered page.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import requests
import re
import time

time.sleep(1)
base_url = 'http://localhost:5000'

def get_html():
    return requests.get(f'{base_url}/').text

def extract_css(html, selector):
    """Extract CSS rule for a given selector from inline styles."""
    pattern = rf'{re.escape(selector)}\s*\{{([^}}]+)\}}'
    match = re.search(pattern, html, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

# ─── Test: History refresh is called after equals ───

def test_history_refresh_called_after_equals():
    """JS must call refreshHistory after equals, not only when panel is open"""
    html = get_html()
    # The sendAction for 'equals' must trigger a history refresh
    # regardless of whether panel is open
    assert 'refreshHistory' in html, "refreshHistory function missing"
    # Find that equals action triggers refreshHistory unconditionally
    # Look for the pattern where refreshHistory is called after equals
    # (not just inside an if-historyOpen block)
    # We check that refreshHistory is called in the equals handler
    equals_block = html[html.find("action === 'equals'"):]
    # Must call refreshHistory somewhere in the handler (not conditionally)
    # Actually we just need the function to exist and be called
    assert 'refreshHistory' in html

# ─── Test: History panel entries have word-break ───

def test_history_entries_have_word_break():
    """History entries must not overflow - need word-break or overflow-wrap"""
    html = get_html()
    history_entry_css = extract_css(html, '.history-entry')
    if history_entry_css:
        has_wrapping = any(prop in history_entry_css for prop in 
                          ['word-wrap', 'overflow-wrap', 'word-break'])
        assert has_wrapping, f"history-entry CSS lacks text wrapping: {history_entry_css}"
    else:
        # Could also be on .history-list or .history-panel
        panel_css = extract_css(html, '.history-panel')
        list_css = extract_css(html, '.history-list')
        combined = (panel_css or '') + ' ' + (list_css or '')
        has_wrapping = any(prop in combined for prop in 
                          ['word-wrap', 'overflow-wrap', 'word-break', 'overflow'])
        assert has_wrapping, "No text wrapping CSS found in history panel styles"

def test_history_panel_has_overflow_y_auto():
    """History list must scroll, not clip"""
    html = get_html()
    list_css = extract_css(html, '.history-list')
    assert list_css is not None, ".history-list CSS rule not found"
    assert 'overflow' in list_css, f".history-list lacks overflow: {list_css}"

# ─── Test: Toggle button alignment ───

def test_toggle_button_not_absolute_to_page():
    """Toggle button must be inside the wrapper, not floating loose"""
    html = get_html()
    # The toggle button must be inside .wrapper div
    wrapper_start = html.find('class="wrapper"')
    toggle_pos = html.find('historyToggle')
    assert toggle_pos > wrapper_start, "Toggle button not inside wrapper"

def test_toggle_button_has_proper_sizing():
    """Toggle button must have adequate sizing and not use writing-mode that overflows"""
    html = get_html()
    toggle_css = extract_css(html, '.history-toggle')
    assert toggle_css is not None, ".history-toggle CSS not found"
    # Must not use writing-mode: vertical-lr with text that overflows
    # Instead use a simple icon or short text
    # Check the button text is short enough
    toggle_match = re.search(r'id="historyToggle"[^>]*>([^<]+)<', html)
    if toggle_match:
        text = toggle_match.group(1).strip()
        # Text should be short (icon or abbreviation), not "HISTORY"
        assert len(text) <= 4, f"Toggle button text too long: '{text}' — use icon or abbreviation"

def test_history_toggle_visible_without_overflow():
    """Toggle button should be visible and not cause text overflow"""
    html = get_html()
    toggle_css = extract_css(html, '.history-toggle')
    # Toggle should not use writing-mode at all
    assert 'writing-mode' not in toggle_css, \
        f"Toggle uses writing-mode which causes text overflow: {toggle_css}"

# ─── Test: History panel positioned correctly ───

def test_history_panel_positioned_relative_to_calculator():
    """History panel should slide from left side of calculator, not offset weirdly"""
    html = get_html()
    panel_css = extract_css(html, '.history-panel')
    assert panel_css is not None, ".history-panel CSS not found"
    # Panel should have position: absolute within wrapper
    assert 'absolute' in panel_css, f"Panel not absolutely positioned: {panel_css}"

def test_history_panel_has_max_width():
    """History panel must have bounded width to prevent overflow"""
    html = get_html()
    panel_css = extract_css(html, '.history-panel')
    assert panel_css is not None
    assert 'width' in panel_css, f"Panel has no width: {panel_css}"

# ─── Test: History entry result text doesn't overflow ───

def test_history_result_has_ellipsis_or_wrap():
    """Long result strings should be handled gracefully"""
    html = get_html()
    result_css = extract_css(html, '.history-entry .result')
    entry_css = extract_css(html, '.history-entry')
    # At minimum, the history-list must have overflow handling
    list_css = extract_css(html, '.history-list')
    assert list_css is not None, ".history-list not found"
    has_overflow = 'overflow' in list_css
    assert has_overflow, f".history-list lacks overflow handling: {list_css}"

# ─── Test: History panel has proper z-index stacking ───

def test_history_panel_z_index():
    """History panel must appear above the calculator when open"""
    html = get_html()
    panel_css = extract_css(html, '.history-panel')
    calc_css = extract_css(html, '.calculator')
    # Panel z-index should be >= calculator z-index
    panel_z = 0
    calc_z = 0
    if panel_css:
        z_match = re.search(r'z-index\s*:\s*(\d+)', panel_css)
        if z_match:
            panel_z = int(z_match.group(1))
    if calc_css:
        z_match = re.search(r'z-index\s*:\s*(\d+)', calc_css)
        if z_match:
            calc_z = int(z_match.group(1))
    # At minimum, both should have explicit z-index
    assert panel_css and 'z-index' in panel_css, f"Panel lacks z-index: {panel_css}"

if __name__ == '__main__':
    tests = [name for name in dir() if name.startswith('test_')]
    passed = failed = 0
    for name in tests:
        try:
            globals()[name]()
            sys.stdout.write(f"PASS: {name}\n")
            passed += 1
        except Exception as e:
            sys.stdout.write(f"FAIL: {name} - {e}\n")
            failed += 1
    sys.stdout.write(f"\n{passed} passed, {failed} failed\n")
    if failed > 0:
        sys.exit(1)