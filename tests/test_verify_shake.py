import requests

r = requests.get('http://localhost:5000/')
html = r.text
assert 'class="calculator' in html, "No calculator class found"
assert '@keyframes shake' in html, "No shake keyframes"
assert 'shakeCalculator' in html, "No shakeCalculator function"
assert '.shake' in html or '.shaking' in html, "No shake CSS class"
assert 'text ===' in html, "No error check"

# Test the actual error flow
base = 'http://localhost:5000/calc'
requests.post(base, json={'action':'clear'})
requests.post(base, json={'action':'number','value':'5'})
requests.post(base, json={'action':'operator','op':'divide'})
requests.post(base, json={'action':'number','value':'0'})
r = requests.post(base, json={'action':'equals'})
assert r.json()['display'] == 'Error'

print("All checks pass! Shake is correctly wired.")
print("Open http://localhost:5000/ with Ctrl+F5 hard refresh")
print("Then type: 5 / 0 = and watch it shake!")
