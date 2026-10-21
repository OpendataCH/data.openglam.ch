import os
import re
import yaml
import requests
import pathlib

def detect_soft_error(response):
    content_type = response.headers.get('Content-Type', '').lower()
    if 'text/html' not in content_type:
        return None
    
    text = response.text[:10000]
    
    # Check <title> tag for error / 404 / 403 indicators
    title_match = re.search(r'<title[^>]*>(.*?)</title>', text, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = ' '.join(title_match.group(1).split())
        if re.search(r'\b(404|403|410)\b', title, re.IGNORECASE) and re.search(r'(error|fehler|erreur|errore|not found|nicht gefunden)', title, re.IGNORECASE):
            return f"Soft error in title: {title}"
        if re.search(r'\b(seite nicht gefunden|page not found|page introuvable|page non trouv[eé]e|pagina non trovata)\b', title, re.IGNORECASE):
            return f"Soft 404 in title: {title}"
            
    # Check body for opendata.swiss / CKAN error indicators
    if 'opendata.swiss' in response.url:
        if any(phrase in text for phrase in [
            'Seite nicht gefunden',
            'Page not found',
            'Page non trouvée',
            'Pagina non trovata',
            'Die Seite, die Sie aufgerufen haben, scheint nicht verfügbar zu sein'
        ]):
            return "opendata.swiss dataset not found"
            
    return None

def check_links(datasets_dir):
    broken_links = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Recursively find all .md files in the datasets directory
    path = pathlib.Path(datasets_dir)
    for md_file in path.rglob('*.md'):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # YAML front matter is between --- delimiters
            parts = content.split('---')
            if len(parts) < 3:
                continue
            
            try:
                data = yaml.safe_load(parts[1])
                if not data or 'resources' not in data:
                    continue
                
                resources = data['resources']
                if not isinstance(resources, list):
                    continue
                
                for resource in resources:
                    url = resource.get('url')
                    if url and (url.startswith('http://') or url.startswith('https://')):
                        print(f"Checking {url} in {md_file}...")
                        try:
                            # Use a timeout and follow redirects
                            # Handle GBIF links directly via their public API to avoid Cloudflare bot protection blocks
                            gbif_match = re.search(r'gbif\.org/dataset/([a-f0-9\-]+)', url)
                            zenodo_match = re.search(r'zenodo\.org/records?/(\d+)', url)
                            opendata_swiss_match = re.search(r'opendata\.swiss/(?:(?:en|de|fr|it)/)?dataset/([^/?#]+)', url)
                            if gbif_match:
                                dataset_uuid = gbif_match.group(1)
                                api_url = f"https://api.gbif.org/v1/dataset/{dataset_uuid}"
                                response = requests.get(api_url, headers=headers, timeout=10)
                            elif zenodo_match:
                                record_id = zenodo_match.group(1)
                                api_url = f"https://zenodo.org/api/records/{record_id}"
                                api_headers = {'User-Agent': 'JKANLinkChecker/1.0'}
                                response = requests.get(api_url, headers=api_headers, timeout=10)
                            elif 'zenodo.org' in url:
                                api_headers = {'User-Agent': 'JKANLinkChecker/1.0'}
                                response = requests.get(url, headers=api_headers, timeout=10, allow_redirects=True)
                            elif opendata_swiss_match:
                                dataset_slug = opendata_swiss_match.group(1)
                                api_url = f"https://opendata.swiss/api/3/action/package_show?id={dataset_slug}"
                                response = requests.get(api_url, headers=headers, timeout=10)
                            else:
                                # Using HEAD request first to be polite, but fetch GET if needed for HTML / soft 404 detection
                                response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
                                
                                # If HEAD fails or content is HTML, use GET to check response body / status
                                content_type = response.headers.get('Content-Type', '').lower()
                                if response.status_code >= 400 or 'text/html' in content_type or 'opendata.swiss' in url:
                                    response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
                            
                            if response.status_code >= 400:
                                broken_links.append({
                                    'file': str(md_file),
                                    'url': url,
                                    'status_code': response.status_code
                                })
                                print(f"  [BROKEN] Status: {response.status_code}")
                            else:
                                if opendata_swiss_match:
                                    try:
                                        data = response.json()
                                        if not data.get('success'):
                                            broken_links.append({
                                                'file': str(md_file),
                                                'url': url,
                                                'status_code': f"{response.status_code} (API error: {data.get('error')})"
                                            })
                                            print(f"  [BROKEN] Status: {response.status_code} (API error: {data.get('error')})")
                                            continue
                                    except Exception:
                                        pass
                                soft_error = detect_soft_error(response)
                                if soft_error:
                                    broken_links.append({
                                        'file': str(md_file),
                                        'url': url,
                                        'status_code': f"{response.status_code} ({soft_error})"
                                    })
                                    print(f"  [BROKEN] Status: {response.status_code} ({soft_error})")
                        except requests.RequestException as e:
                            broken_links.append({
                                'file': str(md_file),
                                'url': url,
                                'error': str(e)
                            })
                            print(f"  [ERROR] {e}")
            except yaml.YAMLError as exc:
                print(f"Error parsing YAML in {md_file}: {exc}")

    return broken_links

if __name__ == "__main__":
    script_dir = pathlib.Path(__file__).parent.resolve()
    datasets_folder = script_dir / '../_datasets'
    if not datasets_folder.exists():
        datasets_folder = pathlib.Path('_datasets')
    print(f"Starting link check in {datasets_folder}...")
    broken = check_links(datasets_folder)
    
    print("\n" + "="*50)
    if broken:
        print(f"Found {len(broken)} broken link(s):")
        for link in broken:
            status = link.get('status_code') or link.get('error')
            print(f"- File: {link['file']}")
            print(f"  URL:  {link['url']}")
            print(f"  Info: {status}")
            print("-" * 20)
    else:
        print("No broken links found!")
    print("="*50)
