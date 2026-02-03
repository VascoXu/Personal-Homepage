#!/usr/bin/env python3
"""
Static site generator for academic website.
Converts Markdown publication files and HTML templates into static HTML pages.
"""

import re
import shutil
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
    authors = re.sub(r'\*\*([^*]+)\*\*', r'<span class="font-medium">\1</span>', pub.get("authors", ""))

    html = f'''
    <!-- Publication Entry -->
    <div class="flex flex-col md:flex-row md:items-center bg-white mt-8">
      <!-- Teaser Image -->
      <div class="md:w-1/4 mt-1">
        {teaser_html}
      </div>

      <!-- Pub. Description -->
      <div class="md:w-2/3 md:pl-6">
        <h2 class="text-lg font-semibold text-gray-900 md:mt-0">{pub["title"]}</h2>
        <div class="mt-2 text-gray-600 font-light">{authors}</div>
        <div class="uppercase text-base mt-1 text-gray-600 font-bold">{pub["conference"]}{f' <span class="text-red-800 font-medium">{pub["special_notes"]}</span>' if pub.get("special_notes") else ''}</div>
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

def generate_highlights_html(publications):
    """Generate highlights section for homepage."""
    featured = [p for p in publications if p.get('featured', False)]

    pubs_html = []
    for pub in featured:
        pubs_html.append(render_publication_html(pub))

    html = '''
<!-- Publications -->
<div class="container mx-auto max-w-7xl px-6 py-8">
  <div class="flex flex-col">
    <div class="mb-4">
      <h2 class="text-2xl font-bold">Selected Publications</h2>
    </div>
    <hr class="my-1 border-gray-200" />
    <div class="bg-white overflow-hidden">
''' + '\n  <hr class="my-8 border-gray-200" />\n'.join(pubs_html) + '''
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
    index_html = index_html.replace("{{url_for('static',filename='dist/css/tailwind.css')}}", 'static/dist/css/tailwind.css')
    # Handle body block with flexible whitespace matching
    index_html = re.sub(r'{%\s*block\s+body\s*%}.*?{%\s*endblock\s*%}', body_content, index_html, flags=re.DOTALL)

    # Remove the tailwind config script since we're using compiled CSS
    index_html = re.sub(r'<script>\s*tailwind\.config = \{.*?\}\s*</script>', '', index_html, flags=re.DOTALL)

    # Remove Research nav links
    index_html = re.sub(r'<a href="/research"[^>]*>RESEARCH</a>', '', index_html)

    # Fix navigation links
    index_html = index_html.replace('href="/"', 'href="index.html"')

    # Write index.html
    with open(f"{OUTPUT_DIR}/index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)

    # Copy static files
    static_output = output_path / "static"
    if static_output.exists():
        shutil.rmtree(static_output)
    shutil.copytree(STATIC_DIR, static_output)

    print(f"✓ Static site generated in '{OUTPUT_DIR}/' directory")
    print(f"✓ Generated {len(publications)} publications")
    print(f"  - index.html")

if __name__ == "__main__":
    build_static_site()
