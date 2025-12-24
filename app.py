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

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Kullanıcı GitHub verilerini analiz eder"""
    try:
        data = request.get_json()
        username_input = data.get('username', '').strip()
        year = int(data.get('year', 2025))
        
        if not username_input:
            return jsonify({'error': 'Kullanıcı adı gerekli'}), 400
        
        # URL'den kullanıcı adını çıkar
        username = extract_username(username_input)
        
        if not username:
            return jsonify({'error': 'Geçersiz kullanıcı adı veya GitHub URL'}), 400

        # GitHub API başlat
        api = GitHubAPI(token=GITHUB_TOKEN)
        
        # Token kontrolü
        if not GITHUB_TOKEN:
            print("WARNING: No GitHub token provided. Private contributions will not be included.")
        
        # Kullanıcı kontrolü
        try:
            user = api.get_user(username)
        except Exception as e:
            return jsonify({'error': str(e)}), 503

        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404

        # AKILLI CACHE KONTROLÜ (Smart Freshness Check)
        # Kullanıcının son aktivite zamanını (Event) versiyon olarak kullanacağız.
        latest_activity_date = None
        try:
            # Sadece son 1 aktiviteyi çek (Hızlı kontrol)
            events = api.get_user_events(username, page=1, per_page=1)
            if events and len(events) > 0:
                latest_activity_date = events[0].get('created_at')
        except:
            pass # Event çekilemezse (örn: private profil) versiyon kontrolünü atla

        # Cache anahtarı
        cache_key = f"analysis_{username.lower()}_{year}"
        cached_result = cache.get(cache_key)
        
        cache_hit = False
        if cached_result:
            cached_version = cached_result.get('data_version')
            
            # Eğer son aktivite tarihi varsa ve cache'teki ile aynıysa -> GÜNCEL
            # Eğer son aktivite tarihi yoksa (çekilemediyse) -> CACHE KULLAN (Varsayılan)
            if latest_activity_date and cached_version != latest_activity_date:
                print(f"🔄 Cache outdated for {username}. New activity detected ({latest_activity_date}). Refreshing...")
            else:
                print(f"⚡ Cache hit for {username} ({year}). Resetting 3-day timer.")
                # SÜREYİ UZAT: Veri kullanıldığı için 3 günlük süreyi baştan başlatıyoruz
                cache.set(cache_key, cached_result, timeout=CACHE_TIMEOUT_3_DAYS)
                return jsonify(cached_result), 200
        
        # cache_hit değişkeni kaldırıldı, doğrudan kontrol ediliyor
        print(f"🔍 Starting analysis for {username} ({year})...")
        
        # Repository'leri çek
        repos = api.get_user_repos(username)
        if not repos:
            return jsonify({'error': 'Repository bulunamadı'}), 404
        
        # Analiz yap
        analyzer = GitHubAnalyzer(year=year)
        result = analyzer.analyze_user_data(username, repos, api)
        
        # Aktivite kontrolü
        total_contribs = result['stats'].get('total_contributions', result['stats'].get('total_commits', 0))
        if total_contribs == 0:
            return jsonify({
                'error': f'{year} yılında hiç aktivite bulunamadı',
                'username': username,
                'year': year
            }), 404
        
        # Kullanıcı bilgilerini ekle
        result['user_info'] = {
            'name': user.get('name', username),
            'avatar_url': user.get('avatar_url', ''),
            'bio': user.get('bio', ''),
            'public_repos': user.get('public_repos', 0),
            'followers': user.get('followers', 0),
            'following': user.get('following', 0),
            'created_at': user.get('created_at', '')
        }
        
        # Token bilgisi ve Versiyon Ekle
        result['has_token'] = GITHUB_TOKEN is not None
        result['from_cache'] = False
        result['data_version'] = latest_activity_date # Versiyonu kaydet
        
        # Sonucu Cache'e kaydet (3 GÜN)
        cache_data = result.copy()
        cache_data['from_cache'] = True
        cache.set(cache_key, cache_data, timeout=CACHE_TIMEOUT_3_DAYS)
        
        return jsonify(result), 200
    
    except ValueError as e:
        return jsonify({'error': 'Geçersiz yıl değeri'}), 400
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Bir hata oluştu: {str(e)}'}), 500

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