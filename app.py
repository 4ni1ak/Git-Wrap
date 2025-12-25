from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_caching import Cache
from github_api import GitHubAPI
from analyzer import GitHubAnalyzer
import os
import re

app = Flask(__name__)
CORS(app)

# Redis Cache Konfigürasyonu
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = os.environ.get('REDIS_PORT', 6379)

cache_config = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 3600,  # 1 saat
    "CACHE_REDIS_HOST": redis_host,
    "CACHE_REDIS_PORT": redis_port
}

app.config.from_mapping(cache_config)
cache = Cache(app)

# Cache süreleri
CACHE_TIMEOUT_3_DAYS = 3 * 24 * 60 * 60  # 259,200 saniye (3 gün)

# GitHub token (opsiyonel, rate limit için)
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', None)

import logging

# Logger konfigürasyonu (Gunicorn ile uyumlu olması için)
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_caching import Cache
from github_api import GitHubAPI
from analyzer import GitHubAnalyzer
import os
import re
import logging
import threading
import uuid
import time

app = Flask(__name__)
CORS(app)

# Redis Konfigürasyonu
redis_host = os.environ.get('REDIS_HOST', 'redis')
redis_port = os.environ.get('REDIS_PORT', 6379)

# Flask-Caching
cache_config = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 3600,
    "CACHE_REDIS_HOST": redis_host,
    "CACHE_REDIS_PORT": redis_port
}
app.config.from_mapping(cache_config)
cache = Cache(app)

# Cache süreleri
CACHE_TIMEOUT_3_DAYS = 3 * 24 * 60 * 60

# GitHub token
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', None)

# Logger konfigürasyonu
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

@app.route('/')
def index():
    return render_template('index.html')

def process_analysis(username, year, task_id):
    """Arka planda çalışan analiz işlemi (Threading)"""
    with app.app_context():
        task_key = f"task_{task_id}"
        try:
            # GitHub API başlat
            api = GitHubAPI(token=GITHUB_TOKEN)
            
            # Token kontrolü
            if not GITHUB_TOKEN:
                app.logger.warning("No GitHub token provided.")
            
            # Kullanıcı kontrolü
            user = api.get_user(username)
            if not user:
                cache.set(task_key, {'status': 'error', 'message': 'Kullanıcı bulunamadı'}, timeout=3600)
                return

            # Cache Kontrolü
            latest_activity_date = None
            try:
                events = api.get_user_events(username, page=1, per_page=1)
                if events: latest_activity_date = events[0].get('created_at')
            except: pass

            cache_key = f"analysis_{username.lower()}_{year}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                cached_version = cached_result.get('data_version')
                if latest_activity_date and cached_version != latest_activity_date:
                    app.logger.info(f"🔄 Cache outdated for {username}.")
                else:
                    app.logger.info(f"⚡ Cache hit for {username}.")
                    cache.set(cache_key, cached_result, timeout=CACHE_TIMEOUT_3_DAYS)
                    cache.set(task_key, {'status': 'completed', 'data': cached_result}, timeout=3600)
                    return

            app.logger.info(f"🔍 Starting analysis for {username}...")
            
            repos = api.get_user_repos(username)
            if not repos:
                cache.set(task_key, {'status': 'error', 'message': 'Repository bulunamadı'}, timeout=3600)
                return
            
            analyzer = GitHubAnalyzer(year=year)
            result = analyzer.analyze_user_data(username, repos, api)
            
            total_contribs = result['stats'].get('total_contributions', 0)
            if total_contribs == 0:
                cache.set(task_key, {'status': 'error', 'message': f'{year} yılında aktivite yok'}, timeout=3600)
                return
            
            result['user_info'] = {
                'name': user.get('name', username),
                'avatar_url': user.get('avatar_url', ''),
                'bio': user.get('bio', ''),
                'public_repos': user.get('public_repos', 0),
                'followers': user.get('followers', 0),
                'following': user.get('following', 0),
                'created_at': user.get('created_at', '')
            }
            result['has_token'] = GITHUB_TOKEN is not None
            result['from_cache'] = False
            result['data_version'] = latest_activity_date
            
            # Cache'e kaydet
            cache_data = result.copy()
            cache_data['from_cache'] = True
            cache.set(cache_key, cache_data, timeout=CACHE_TIMEOUT_3_DAYS)
            
            # Task Durumunu Güncelle
            cache.set(task_key, {'status': 'completed', 'data': result}, timeout=3600)
            
        except Exception as e:
            app.logger.error(f"Analysis failed: {str(e)}")
            cache.set(task_key, {'status': 'error', 'message': str(e)}, timeout=3600)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analiz işlemini başlatır (Threading + Redis)"""
    try:
        data = request.get_json()
        username_input = data.get('username', '').strip()
        year = int(data.get('year', 2025))
        
        if not username_input:
            return jsonify({'error': 'Kullanıcı adı gerekli'}), 400
        
        username = extract_username(username_input)
        if not username:
            return jsonify({'error': 'Geçersiz kullanıcı adı'}), 400

        task_id = f"{username}_{year}"
        task_key = f"task_{task_id}"
        
        # Mevcut durumu Redis'ten kontrol et
        existing_task = cache.get(task_key)
        
        if existing_task:
            status = existing_task.get('status')
            if status == 'completed':
                return jsonify(existing_task['data']), 200
            elif status == 'processing':
                return jsonify({'status': 'processing', 'task_id': task_id}), 202
        
        # Yeni işlem başlat ve durumu Redis'e yaz
        cache.set(task_key, {'status': 'processing'}, timeout=3600)
        
        thread = threading.Thread(target=process_analysis, args=(username, year, task_id))
        thread.start()
        
        return jsonify({'status': 'processing', 'task_id': task_id}), 202
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<task_id>', methods=['GET'])
def check_status(task_id):
    """İşlem durumunu Redis üzerinden kontrol eder"""
    task_key = f"task_{task_id}"
    task = cache.get(task_key)
    
    if not task:
        return jsonify({'status': 'not_found'}), 404
    
    if task['status'] == 'completed':
        return jsonify(task['data']), 200
    elif task['status'] == 'error':
        return jsonify({'error': task.get('message', 'Bilinmeyen hata')}), 500
    else:
        return jsonify({'status': 'processing'}), 202

def extract_username(input_string):
    patterns = [r'github\.com/([a-zA-Z0-9_-]+)', r'^([a-zA-Z0-9_-]+)$']
    for pattern in patterns:
        match = re.search(pattern, input_string)
        if match: return match.group(1)
    return None

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3020))
    app.run(host='0.0.0.0', port=port)

@app.route('/api/rate-limit', methods=['GET'])
def rate_limit():
    """Rate limit durumunu kontrol eder"""
    try:
        api = GitHubAPI(token=GITHUB_TOKEN)
        limit_info = api.get_rate_limit()
        
        if limit_info:
            core = limit_info.get('resources', {}).get('core', {})
            graphql = limit_info.get('resources', {}).get('graphql', {})
            return jsonify({
                'core': {
                    'limit': core.get('limit', 0),
                    'remaining': core.get('remaining', 0),
                    'reset': core.get('reset', 0)
                },
                'graphql': {
                    'limit': graphql.get('limit', 0),
                    'remaining': graphql.get('remaining', 0),
                    'reset': graphql.get('reset', 0)
                },
                'has_token': GITHUB_TOKEN is not None
            }), 200
        
        return jsonify({'error': 'Rate limit bilgisi alınamadı'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_username(input_string):
    """GitHub URL veya kullanıcı adından username çıkarır"""
    # URL pattern'leri
    patterns = [
        r'github\.com/([a-zA-Z0-9_-]+)',  # https://github.com/username
        r'^([a-zA-Z0-9_-]+)$'  # sadece username
    ]
    
    for pattern in patterns:
        match = re.search(pattern, input_string)
        if match:
            return match.group(1)
    
    return None

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint bulunamadı'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Sunucu hatası'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3020))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)