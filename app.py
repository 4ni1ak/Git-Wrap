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

import threading
import uuid
import time

# Basit In-Memory Task Queue
tasks = {}

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')

def process_analysis(username, year, task_id):
    """Arka planda çalışan analiz işlemi"""
    with app.app_context():
        try:
            # GitHub API başlat
            api = GitHubAPI(token=GITHUB_TOKEN)
            
            # Token kontrolü
            if not GITHUB_TOKEN:
                app.logger.warning("No GitHub token provided.")
            
            # Kullanıcı kontrolü
            user = api.get_user(username)
            if not user:
                tasks[task_id] = {'status': 'error', 'message': 'Kullanıcı bulunamadı'}
                return

            # AKILLI CACHE KONTROLÜ
            latest_activity_date = None
            try:
                events = api.get_user_events(username, page=1, per_page=1)
                if events: latest_activity_date = events[0].get('created_at')
            except: pass

            cache_key = f"analysis_{username.lower()}_{year}"
            cached_result = cache.get(cache_key)
            
            # Cache Check
            if cached_result:
                cached_version = cached_result.get('data_version')
                if latest_activity_date and cached_version != latest_activity_date:
                    app.logger.info(f"🔄 Cache outdated for {username}.")
                else:
                    app.logger.info(f"⚡ Cache hit for {username}.")
                    cache.set(cache_key, cached_result, timeout=CACHE_TIMEOUT_3_DAYS)
                    tasks[task_id] = {'status': 'completed', 'data': cached_result}
                    return

            app.logger.info(f"🔍 Starting analysis for {username}...")
            
            repos = api.get_user_repos(username)
            if not repos:
                tasks[task_id] = {'status': 'error', 'message': 'Repository bulunamadı'}
                return
            
            analyzer = GitHubAnalyzer(year=year)
            result = analyzer.analyze_user_data(username, repos, api)
            
            # Aktivite kontrolü
            total_contribs = result['stats'].get('total_contributions', 0)
            if total_contribs == 0:
                tasks[task_id] = {'status': 'error', 'message': f'{year} yılında aktivite yok'}
                return
            
            # User Info Ekle
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
            
            # Cache Kaydet
            cache_data = result.copy()
            cache_data['from_cache'] = True
            cache.set(cache_key, cache_data, timeout=CACHE_TIMEOUT_3_DAYS)
            
            tasks[task_id] = {'status': 'completed', 'data': result}
            
        except Exception as e:
            app.logger.error(f"Analysis failed: {str(e)}")
            tasks[task_id] = {'status': 'error', 'message': str(e)}

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analiz işlemini başlatır (Asenkron)"""
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
        
        # Eğer işlem zaten devam ediyorsa veya bitmişse
        if task_id in tasks:
            status = tasks[task_id]['status']
            if status == 'completed':
                return jsonify(tasks[task_id]['data']), 200
            elif status == 'processing':
                return jsonify({'status': 'processing', 'task_id': task_id}), 202
        
        # Yeni işlem başlat
        tasks[task_id] = {'status': 'processing'}
        thread = threading.Thread(target=process_analysis, args=(username, year, task_id))
        thread.start()
        
        return jsonify({'status': 'processing', 'task_id': task_id}), 202
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<task_id>', methods=['GET'])
def check_status(task_id):
    """İşlem durumunu kontrol eder"""
    task = tasks.get(task_id)
    if not task:
        return jsonify({'status': 'not_found'}), 404
    
    if task['status'] == 'completed':
        return jsonify(task['data']), 200
    elif task['status'] == 'error':
        return jsonify({'error': task['message']}), 500
    else:
        return jsonify({'status': 'processing'}), 202

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