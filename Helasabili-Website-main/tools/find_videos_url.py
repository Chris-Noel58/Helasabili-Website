import os
root = os.path.join(os.getcwd(),'templates')
matches = []
for dirpath,dirs,files in os.walk(root):
    for f in files:
        if f.endswith('.html'):
            p = os.path.join(dirpath,f)
            try:
                s = open(p,encoding='utf-8').read()
            except Exception:
                continue
            if "{% url 'videos' %}" in s or '{% url "videos" %}' in s:
                matches.append(p)
            if "url 'videos'" in s or 'url "videos"' in s:
                matches.append(p)
print('\n'.join(sorted(set(matches))))
