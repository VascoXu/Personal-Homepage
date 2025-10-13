#!/usr/bin/env python3
"""
Static site generator for academic website.
Converts Markdown publication files and HTML templates into static HTML pages.
"""

import os
import re
import yaml
from pathlib import Path

# Directories
PUBLICATIONS_DIR = "publications"
TEMPLATES_DIR = "templates"
OUTPUT_DIR = "build"
STATIC_DIR = "static"

def parse_markdown(file_path):
    """Parse markdown file and extract frontmatter."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract YAML frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        frontmatter = yaml.safe_load(match.group(1))
        body = content[match.end():]
        return frontmatter, body
    return {}, content

def load_publications():
    """Load all publications from markdown files."""
    publications = []
    pub_dir = Path(PUBLICATIONS_DIR)

    if not pub_dir.exists():
        return publications

    for md_file in pub_dir.glob("*.md"):
        metadata, body = parse_markdown(md_file)
        metadata['body'] = body
        metadata['filename'] = md_file.stem
        publications.append(metadata)

    # Sort by order field
    publications.sort(key=lambda x: x.get('order', 999))
    return publications

def render_publication_html(pub):
    """Render a single publication as HTML."""
    # Escape empty URLs
    paper_link = f'<a href="{pub["paper_url"]}" target="_blank" class="text-pink-600 hover:text-gray-500 mr-2">[ <span class="hover:underline hover:underline-offset-4">paper</span> ]</a>' if pub.get("paper_url") else ''
    video_link = f'<a href="{pub["video_url"]}" target="_blank" class="text-pink-600 hover:text-gray-500 mr-2">[ <span class="hover:underline hover:underline-offset-4">video</span> ]</a>' if pub.get("video_url") else ''
    code_link = f'<a href="{pub["code_url"]}" target="_blank" class="text-pink-600 hover:text-gray-500 mr-2">[ <span class="hover:underline hover:underline-offset-4">code</span> ]</a>' if pub.get("code_url") else ''

    teaser_html = f'<img src="{pub["teaser"]}" class="object-contain mx-auto" alt="{pub["title"]} Teaser">' if pub.get("teaser") else ''

    # Format authors (markdown bold ** to HTML)
    authors = pub.get("authors", "").replace("**", "<span class='font-semibold'>").replace("**", "</span>")
    authors = re.sub(r'\*\*([^*]+)\*\*', r'<span class="font-semibold">\1</span>', pub.get("authors", ""))

    html = f'''
    <!-- Publication Entry -->
    <div class="flex flex-col md:flex-row bg-white mt-8">
      <!-- Teaser Image -->
      <div class="md:w-1/4 mt-1">
        {teaser_html}
      </div>

      <!-- Pub. Description -->
      <div class="md:w-2/3 md:pl-6">
        <h2 class="text-xl font-semibold text-gray-900 md:mt-0">{pub["title"]}</h2>
        <div class="uppercase tracking-wide text-sm mt-1"><span class="text-gray-600 font-bold">{pub["conference"]}:</span> <span class="text-red-800 font-medium">{pub["conference_full"]}</span></div>
        <p class="mt-2 text-gray-600">{authors}</p>
        <!-- Links -->
        <div class="mt-2">
          {paper_link}
          {video_link}
          {code_link}
        </div>
      </div>
    </div>
    '''
    return html

def render_featured_publication_html(pub):
    """Render a featured publication for the homepage."""
    authors = re.sub(r'\*\*([^*]+)\*\*', r'<span class="font-semibold">\1</span>', pub.get("authors", ""))

    paper_link = f'<a href="{pub["paper_url"]}" target="_blank" class="text-gray-600 underline underline-offset-4 hover:text-black hover:underline hover:decoration-pink-500">paper</a>' if pub.get("paper_url") else ''
    video_link = f'<a href="{pub["video_url"]}" target="_blank" class="text-gray-600 underline underline-offset-4 hover:text-black hover:underline hover:decoration-pink-500">video</a>' if pub.get("video_url") else ''
    code_link = f'<a href="{pub["code_url"]}" target="_blank" class="text-gray-600 underline underline-offset-4 hover:text-black hover:underline hover:decoration-pink-500">code</a>' if pub.get("code_url") else ''

    links = [link for link in [paper_link, video_link, code_link] if link]
    links_html = '<span class="text-gray-300">|</span>'.join(links)

    teaser_html = f'<img class="h-36 w-full object-cover" src="{pub["teaser"]}" alt="{pub["title"]} Teaser">' if pub.get("teaser") else ''

    html = f'''
      <!-- Featured Publication -->
      <div class="md:flex md:items-center">
        <div class="md:flex-shrink-0">
          {teaser_html}
        </div>
        <div class="p-8">
          <h2 class="text-xl font-semibold text-gray-900 md:mt-0">{pub["title"]}</h2>
          <div class="uppercase tracking-wide text-sm mt-1"><span class="text-gray-600 font-bold">{pub["conference"]}:</span> <span class="text-red-800 font-medium">{pub["conference_full"]}</span></div>
          <p class="mt-2 text-gray-600">{authors}</p>
          <div class="flex mt-2">
            <div class="p-1">
              <div class="flex space-x-2 justify-center md:justify-start">
                <span class="text-gray-600">[</span>
                {links_html}
                <span class="text-gray-600">]</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    '''
    return html

def generate_research_html(publications):
    """Generate research.html content."""
    regular_pubs = [p for p in publications if p.get('type') != 'thesis']
    theses = [p for p in publications if p.get('type') == 'thesis']

    pubs_html = []
    for pub in regular_pubs:
        pubs_html.append(render_publication_html(pub))

    thesis_html = []
    for thesis in theses:
        thesis_html.append(render_thesis_html(thesis))

    publications_section = '''
<div class="container mx-auto max-w-7xl mt-8 px-8 py-8">
  <h2 class="text-3xl font-light text-gray-900 mb-4">Publications</h2>
''' + '\n  <hr class="my-8 border-gray-200" />\n'.join(pubs_html) + '\n</div>'

    thesis_section = ''
    if thesis_html:
        thesis_section = '''
<div class="container mx-auto max-w-7xl mt-8 px-8 py-8">
  <h2 class="text-3xl font-light text-gray-900 mb-4">Theses</h2>
  <hr class="my-1 border-gray-200" />
''' + '\n'.join(thesis_html) + '\n</div>'

    return publications_section + thesis_section

def render_thesis_html(thesis):
    """Render thesis entry."""
    authors = re.sub(r'\*\*([^*]+)\*\*', r'<span class="font-semibold">\1</span>', thesis.get("authors", ""))

    paper_link = f'<a href="{thesis["paper_url"]}" target="_blank" class="text-pink-600 hover:text-gray-500 mr-2">[ <span class="hover:underline hover:underline-offset-4">paper</span> ]</a>' if thesis.get("paper_url") else ''

    html = f'''
  <!-- Thesis Entry -->
  <div class="flex flex-col md:flex-row bg-white mt-8">
    <div class="md:w-2/3">
      <h2 class="text-xl font-semibold text-gray-900 md:mt-0">{thesis["title"]}</h2>
      <div class="uppercase tracking-wide text-sm mt-1"><span class="text-gray-600 font-bold">{thesis["conference"]}</span> | <span class="text-red-800 font-medium">{thesis["conference_full"]}</span></div>
      <p class="mt-2 text-gray-600">{authors}</p>
      <div class="mt-2">
        {paper_link}
      </div>
    </div>
  </div>
    '''
    return html

def generate_highlights_html(publications):
    """Generate highlights section for homepage."""
    featured = [p for p in publications if p.get('featured', False)]

    pubs_html = []
    for pub in featured:
        pubs_html.append(render_featured_publication_html(pub))

    html = '''
<!-- Publications -->
<div class="container mx-auto max-w-7xl px-6 py-8">
  <div class="flex flex-col">
    <div class="mb-4">
      <div class="flex items-baseline space-x-4">
        <h2 class="text-2xl font-bold">Selected Publications</h2>
        <a href="research.html" class="text-indigo-600 hover:text-indigo-800 hover:underline hover:underline-offset-4 text-base">[ Full List ]</a>
      </div>
    </div>
    <hr class="my-1 border-gray-200" />
    <div class="bg-white overflow-hidden md:max-w-4xl">
''' + '\n'.join(pubs_html) + '''
    </div>
  </div>
</div>
'''
    return html

def build_static_site():
    """Main function to build the static site."""
    # Create output directory
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)

    # Load publications
    publications = load_publications()

    # Generate research page content
    research_content = generate_research_html(publications)

    # Generate highlights for homepage
    highlights_content = generate_highlights_html(publications)

    # Read base layout
    with open(f"{TEMPLATES_DIR}/layout.html", 'r', encoding='utf-8') as f:
        layout = f.read()

    # Generate index.html
    with open(f"{TEMPLATES_DIR}/index.html", 'r', encoding='utf-8') as f:
        index_template = f.read()

    # Extract body content from index template first
    body_match = re.search(r'{% block body %}(.*?){% endblock %}', index_template, re.DOTALL)
    body_content = ''
    if body_match:
        body_content = body_match.group(1)
        # Replace includes
        body_content = body_content.replace("{% include 'highlights.html' %}", highlights_content)

    # Replace Jinja2 syntax with actual content
    index_html = layout.replace('{% block title %}{% endblock %}', 'Vasco Xu')
    index_html = index_html.replace('{% block nav_home %}{% endblock %}', 'underline underline-offset-8 decoration-2 decoration-pink-500')
    index_html = index_html.replace('{% block nav_research %}{% endblock %}', 'text-gray-500')
    index_html = index_html.replace("{{url_for('static',filename='dist/css/tailwind.css')}}", 'static/dist/css/tailwind.css')
    # Handle body block with flexible whitespace matching
    index_html = re.sub(r'{%\s*block\s+body\s*%}.*?{%\s*endblock\s*%}', body_content, index_html, flags=re.DOTALL)

    # Remove the tailwind config script since we're using compiled CSS
    index_html = re.sub(r'<script>\s*tailwind\.config = \{.*?\}\s*</script>', '', index_html, flags=re.DOTALL)

    # Fix navigation links
    index_html = index_html.replace('href="/"', 'href="index.html"')
    index_html = index_html.replace('href="/research"', 'href="research.html"')

    # Write index.html
    with open(f"{OUTPUT_DIR}/index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)

    # Generate research.html
    research_html = layout.replace('{% block title %}{% endblock %}', 'Vasco Xu | Research')
    research_html = research_html.replace('{% block nav_home %}{% endblock %}', 'text-gray-500')
    research_html = research_html.replace('{% block nav_research %}{% endblock %}', 'underline underline-offset-8 decoration-2 decoration-pink-500')
    research_html = research_html.replace("{{url_for('static',filename='dist/css/tailwind.css')}}", 'static/dist/css/tailwind.css')
    # Handle body block with flexible whitespace matching
    research_html = re.sub(r'{%\s*block\s+body\s*%}.*?{%\s*endblock\s*%}', research_content, research_html, flags=re.DOTALL)
    research_html = research_html.replace('href="/"', 'href="index.html"')
    research_html = research_html.replace('href="/research"', 'href="research.html"')

    # Remove the tailwind config script since we're using compiled CSS
    research_html = re.sub(r'<script>\s*tailwind\.config = \{.*?\}\s*</script>', '', research_html, flags=re.DOTALL)

    # Write research.html
    with open(f"{OUTPUT_DIR}/research.html", 'w', encoding='utf-8') as f:
        f.write(research_html)

    # Copy static files (symlink or copy)
    static_output = output_path / "static"
    if static_output.exists():
        import shutil
        shutil.rmtree(static_output)

    import shutil
    shutil.copytree(STATIC_DIR, static_output)

    print(f"✓ Static site generated in '{OUTPUT_DIR}/' directory")
    print(f"✓ Generated {len(publications)} publications")
    print(f"  - index.html")
    print(f"  - research.html")

if __name__ == "__main__":
    build_static_site()
