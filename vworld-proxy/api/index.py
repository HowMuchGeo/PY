from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote, urlencode
import requests

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def do_GET(self):
        decoded_raw_path = unquote(self.path)
        print(f"[Vercel Proxy] Original raw path: {decoded_raw_path}")

        parsed_path = urlparse(decoded_raw_path)
        query_dict = parse_qs(parsed_path.query)
        endpoint_path = parsed_path.path.rstrip('/')

        if 'path' in query_dict:
            extracted_path = query_dict.pop('path')[0]
            endpoint_path = f"/{extracted_path.lstrip('/')}"
        
        if endpoint_path.startswith('/api/index'):
            endpoint_path = ''

        clean_query_params = {k: v[0] for k, v in query_dict.items() if v}
        clean_query_string = urlencode(clean_query_params)

        target_url = f"https://api.vworld.kr{endpoint_path}"
        if clean_query_string:
            target_url += f"?{clean_query_string}"

        print(f"[Vercel Proxy] Final Target URL: {target_url}")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(
                target_url,
                headers=headers,
                timeout=10,
                allow_redirects=True
            )
            
            print(f"[Vercel Proxy] Vworld Response Status: {response.status_code}")

            self.send_response(response.status_code)
            self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json; charset=utf-8'))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.content)

        except Exception as e:
            print(f"[Vercel Proxy Error] {str(e)}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(f'{{"error": "{str(e)}"}}'.encode('utf-8'))
