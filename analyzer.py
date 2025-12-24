from datetime import datetime
from collections import defaultdict, Counter
import re

class GitHubAnalyzer:
    def __init__(self, year=2025):
        self.year = year
        self.start_date = f"{year}-01-01T00:00:00Z"
        self.end_date = f"{year}-12-31T23:59:59Z"
        
        # Persona analizi için sayaçlar
        self.night_commits = 0
        self.morning_commits = 0
        self.weekend_commits = 0
    
    def is_in_year(self, date_string):
        """Tarihin belirtilen yıl içinde olup olmadığını kontrol eder"""
        try:
            date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return date.year == self.year
        except:
            return False
    
    def analyze_user_data(self, username, repos, api):
        """Tüm kullanıcı verilerini analiz eder"""
        
        print(f"\n{'='*60}")
        print(f"🔍 Analyzing GitHub profile: @{username}")
        print(f"{'='*60}\n")
        
        # GraphQL ile contribution verilerini al
        contributions_data = api.get_contributions_collection(username, self.start_date, self.end_date)
        
        if not contributions_data:
            print("⚠️  Warning: Could not fetch GraphQL data, using REST API only")
            return self._analyze_with_rest_api(username, repos, api)
        
        # GraphQL'den gelen temel veriler
        total_commits_graphql = contributions_data.get('totalCommitContributions', 0)
        total_prs_graphql = contributions_data.get('totalPullRequestContributions', 0)
        total_issues_graphql = contributions_data.get('totalIssueContributions', 0)
        total_reviews_graphql = contributions_data.get('totalPullRequestReviewContributions', 0)
        calendar = contributions_data.get('contributionCalendar', {})
        total_contributions = calendar.get('totalContributions', 0)
        
        print(f"✓ Total contributions: {total_contributions}")
        print(f"✓ Commits: {total_commits_graphql} | PRs: {total_prs_graphql}")
        print(f"✓ Issues: {total_issues_graphql} | Reviews: {total_reviews_graphql}")
        
        # Aktif günler ve aylık dağılım
        active_days = set()
        monthly_commits = defaultdict(int)
        
        weeks = calendar.get('weeks', [])
        for week in weeks:
            for day in week.get('contributionDays', []):
                contrib_count = day.get('contributionCount', 0)
                if contrib_count > 0:
                    date_str = day.get('date', '')
                    try:
                        date = datetime.fromisoformat(date_str)
                        active_days.add(date.date())
                        month_name = date.strftime('%B')
                        monthly_commits[month_name] += contrib_count
                    except:
                        pass
        
        # Repository listesini GraphQL'den çıkar
        commit_repos = contributions_data.get('commitContributionsByRepository', [])
        pr_repos = contributions_data.get('pullRequestContributionsByRepository', [])
        
        # Repository bilgilerini topla
        repo_map = {}
        own_commits = 0
        others_commits = 0
        all_languages = defaultdict(int)
        
        print(f"\n📦 Processing {len(commit_repos)} repositories with commits...")
        
        for item in commit_repos:
            repo_info = item.get('repository', {})
            repo_name = repo_info.get('name', '')
            repo_owner = repo_info.get('owner', {}).get('login', '')
            commit_count = item.get('contributions', {}).get('totalCount', 0)
            
            if commit_count == 0:
                continue
            
            is_own_repo = repo_owner.lower() == username.lower()
            if is_own_repo:
                own_commits += commit_count
            else:
                others_commits += commit_count
            
            # Dil bilgisi
            primary_lang = repo_info.get('primaryLanguage')
            if primary_lang:
                lang_name = primary_lang.get('name', '')
                if lang_name:
                    # Commit sayısıyla ağırlıklandır
                    all_languages[lang_name] += commit_count * 1000
            
            repo_map[f"{repo_owner}/{repo_name}"] = {
                'name': repo_name,
                'owner': repo_owner,
                'commits': commit_count,
                'prs': 0,
                'additions': 0,
                'deletions': 0,
                'is_own': is_own_repo,
                'url': repo_info.get('url', ''),
                'is_private': repo_info.get('isPrivate', False),
                'stars': 0,
                'forks': 0,
                'contribution_days': 0
            }
        
        # PR'ları ekle
        for item in pr_repos:
            repo_info = item.get('repository', {})
            repo_name = repo_info.get('name', '')
            repo_owner = repo_info.get('owner', {}).get('login', '')
            pr_count = item.get('contributions', {}).get('totalCount', 0)
            repo_key = f"{repo_owner}/{repo_name}"
            
            if repo_key in repo_map:
                repo_map[repo_key]['prs'] = pr_count
            elif pr_count > 0:
                repo_map[repo_key] = {
                    'name': repo_name,
                    'owner': repo_owner,
                    'commits': 0,
                    'prs': pr_count,
                    'additions': 0,
                    'deletions': 0,
                    'is_own': repo_owner.lower() == username.lower(),
                    'url': repo_info.get('url', ''),
                    'is_private': repo_info.get('isPrivate', False),
                    'stars': 0,
                    'forks': 0,
                    'contribution_days': 0
                }
        
        # ÖNEMLİ: Şimdi her repo için DETAYLI commit bilgilerini çek
        print(f"\n💾 Fetching detailed commit data (additions/deletions)...")
        
        total_additions = 0
        total_deletions = 0
        commit_messages = []
        total_stars_received = 0
        total_forks_received = 0
        created_repos = []
        forked_repos = []
        total_merges = 0
        
        
        # En aktif repoları önce işlemek için sıralamayı koruyoruz.
        sorted_repos = sorted(
            repo_map.items(), 
            key=lambda x: x[1]['commits'] + x[1]['prs'], 
            reverse=True
        )
        
        # Tüm repoları işle (Limit kaldırıldı)
        repos_to_process = sorted_repos
        print(f"  ⚡ Processing ALL {len(repos_to_process)} repositories (This may take a while for large profiles)...")
        
        processed_count = 0
        for repo_key, repo_data in repos_to_process:
            processed_count += 1
            print(f"  📊 Processing {processed_count}/{len(repos_to_process)}: {repo_key}")
            
            repo_owner = repo_data['owner']
            repo_name = repo_data['name']
            
            # Owner veya name boşsa atla
            if not repo_owner or not repo_name:
                print(f"  ⚠️  Skipping invalid repo: {repo_key}")
                continue
            
            # Commit'leri detaylı çek
            commits = api.get_repo_commits(
                repo_owner,
                repo_name,
                since=self.start_date,
                until=self.end_date
            )
            
            if not commits:
                continue
            
            repo_additions = 0
            repo_deletions = 0
            repo_commit_dates = []
            repo_merges = 0
            
            for commit in commits:
                # Commit sahibini kontrol et
                commit_author = None
                if commit.get('author'):
                    commit_author = commit['author'].get('login', '').lower()
                
                commit_data = commit.get('commit', {})
                commit_date_str = commit_data.get('author', {}).get('date', '')
                
                if not self.is_in_year(commit_date_str):
                    continue
                
                # Sadece kullanıcının kendi commit'lerini say
                if commit_author and commit_author != username.lower():
                    continue
                
                # Merge commit mi kontrol et
                if len(commit.get('parents', [])) > 1:
                    repo_merges += 1
                    total_merges += 1
                
                # Tarih ve Saat bilgisi
                try:
                    commit_date = datetime.fromisoformat(commit_date_str.replace('Z', '+00:00'))
                    repo_commit_dates.append(commit_date)
                    
                    # Saat analizi
                    hour = commit_date.hour
                    # Gün analizi (0=Monday, 6=Sunday)
                    weekday = commit_date.weekday()
                    
                    if 22 <= hour or hour < 6:
                        self.night_commits += 1
                    elif 6 <= hour < 12:
                        self.morning_commits += 1
                        
                    if weekday >= 5:
                        self.weekend_commits += 1
                except:
                    pass
                
                # Commit mesajı
                message = commit_data.get('message', '').split('\n')[0].strip()
                if message and not message.lower().startswith('merge'):
                    commit_messages.append(message.lower())
                
                # ÖNEMLİ: Stats bilgisi (additions/deletions)
                stats = commit.get('stats', {})
                if stats:
                    additions = stats.get('additions', 0)
                    deletions = stats.get('deletions', 0)
                    
                    total_additions += additions
                    total_deletions += deletions
                    repo_additions += additions
                    repo_deletions += deletions
            
            # Repo'ya yıl içinde kaç farklı günde katkı sağlandı
            unique_commit_days = len(set(d.date() for d in repo_commit_dates))
            
            # Repository istatistiklerini güncelle
            repo_map[repo_key]['additions'] = repo_additions
            repo_map[repo_key]['deletions'] = repo_deletions
            repo_map[repo_key]['changes'] = repo_additions + repo_deletions
            repo_map[repo_key]['contribution_days'] = unique_commit_days
            repo_map[repo_key]['merges'] = repo_merges
        
        # Public repo'lar için ek bilgi (star, fork, dil, oluşturulma tarihi)
        print(f"\n⭐ Collecting repo metadata (stars, forks, languages)...")
        
        for repo in repos:
            repo_name = repo['name']
            repo_owner = repo['owner']['login']
            repo_key = f"{repo_owner}/{repo_name}"
            is_own_repo = repo_owner.lower() == username.lower()
            
            # Oluşturulma tarihi
            created_at = repo.get('created_at', '')
            if self.is_in_year(created_at):
                created_repos.append({
                    'name': repo_name,
                    'url': repo['html_url'],
                    'description': repo.get('description', '') or 'No description',
                    'stars': repo.get('stargazers_count', 0),
                    'forks': repo.get('forks_count', 0),
                    'language': repo.get('language', 'Unknown')
                })
            
            # Fork edilmiş mi?
            if repo.get('fork', False) and is_own_repo:
                forked_repos.append({
                    'name': repo_name,
                    'url': repo['html_url']
                })
            
            # Star ve fork sayıları
            stars = repo.get('stargazers_count', 0)
            forks = repo.get('forks_count', 0)
            
            if is_own_repo:
                total_stars_received += stars
                total_forks_received += forks
                
                if repo_key in repo_map:
                    repo_map[repo_key]['stars'] = stars
                    repo_map[repo_key]['forks'] = forks
            
            # Dil analizi - SADECE bu repo'da 2025'te katkı varsa
            # Yani repo_map'te varsa (zaten sadece 2025'te commit atılan repo'lar repo_map'te)
            if repo_key in repo_map:
                languages = api.get_repo_languages(repo_owner, repo_name)
                if languages:
                    # Commit sayısıyla ağırlıklandırılmış byte sayısı
                    commit_weight = repo_map[repo_key]['commits']
                    for lang, bytes_count in languages.items():
                        # Hem byte hem commit sayısını dikkate al
                        all_languages[lang] += bytes_count * (1 + commit_weight * 0.1)
        
        print(f"\n✅ Analysis complete!")
        print(f"  📝 Total additions: {total_additions:,}")
        print(f"  🗑️  Total deletions: {total_deletions:,}")
        print(f"  🔀 Total merges: {total_merges}")
        print(f"{'='*60}\n")
        
        # İstatistik hesaplamaları
        top_repos = self._calculate_top_repos(repo_map)
        commit_analysis = self._analyze_commit_messages(commit_messages)
        language_stats = self._calculate_language_distribution(all_languages)
        longest_streak = self._calculate_longest_streak(active_days)
        org_contributions = self._calculate_org_contributions(repo_map, username)
        
        # Aylık dağılım
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        monthly_distribution = {month: monthly_commits.get(month, 0) for month in month_order}
        
        # En aktif ay
        most_active_month = max(monthly_distribution.items(), key=lambda x: x[1]) if monthly_distribution else (None, 0)
        
        # Persona Analizi
        persona = self._determine_persona(
            total_commits=total_commits_graphql,
            total_prs=total_prs_graphql,
            total_issues=total_issues_graphql,
            total_reviews=total_reviews_graphql,
            longest_streak=longest_streak,
            stars_received=total_stars_received,
            languages=language_stats,
            weekend_ratio=self.weekend_commits / max(1, processed_count) if processed_count > 0 else 0, # Yaklaşık
            night_ratio=self.night_commits / max(1, self.night_commits + self.morning_commits + 1) # Basit oran
        )
        
        # Sonuç
        result = {
            'username': username,
            'year': self.year,
            'stats': {
                'total_commits': total_commits_graphql,
                'total_contributions': total_contributions,
                'total_repos': len([r for r in repo_map.values() if r['commits'] > 0 or r['prs'] > 0]),
                'contributed_projects': len(repo_map),
                'own_project_commits': own_commits,
                'others_project_commits': others_commits,
                'total_additions': total_additions,
                'total_deletions': total_deletions,
                'net_changes': total_additions - total_deletions,
                'active_days': len(active_days),
                'longest_streak': longest_streak,
                'total_prs': total_prs_graphql,
                'total_issues': total_issues_graphql,
                'total_reviews': total_reviews_graphql,
                'total_merges': total_merges,
                'stars_received': total_stars_received,
                'forks_received': total_forks_received,
                'repos_created': len(created_repos),
                'repos_forked': len(forked_repos),
                'most_active_month': most_active_month[0] if most_active_month[1] > 0 else None
            },
            'persona': persona,
            'top_repos': top_repos,
            'created_repos': sorted(created_repos, key=lambda x: x['stars'], reverse=True)[:5],
            'forked_repos': forked_repos[:5],
            'commit_analysis': {
                'most_common_messages': commit_analysis,
                'monthly_distribution': monthly_distribution
            },
            'languages': language_stats,
            'org_contributions': org_contributions,
            'repo_names': [stats['name'] for stats in repo_map.values()], # Quiz için repo isimleri
            'has_private_contributions': any(r.get('is_private', False) for r in repo_map.values())
        }
        
        return result
    
    def _determine_persona(self, total_commits, total_prs, total_issues, total_reviews, longest_streak, stars_received, languages, weekend_ratio, night_ratio):
        """Kullanıcı istatistiklerine göre persona belirler"""
        
        # 1. The Marathon Runner (Maratoncu) - Uzun commit serisi
        if longest_streak > 30:
            return {'id': 'marathon_runner', 'icon': '🏃'}

        # 2. The Star Gazer (Yıldız Avcısı) - Çok fazla star almış
        if stars_received > 100:
            return {'id': 'star_gazer', 'icon': '🤩'}

        # 3. Polyglot (Çok Dilli)
        if len(languages) >= 6:
            return {'id': 'polyglot', 'icon': '🌍'}
            
        # 4. The Reviewer (Gözlemci) - Çok code review
        if total_reviews > 20 and total_reviews > total_prs:
            return {'id': 'the_reviewer', 'icon': '👀'}

        # 5. The Bug Hunter (Böcek Avcısı) - Çok issue
        if total_issues > 20 and total_issues > total_prs:
            return {'id': 'bug_hunter', 'icon': '🐛'}

        # 6. Night Owl (Gece Kuşu) - Eğer commitlerin çoğu gece ise
        if self.night_commits > self.morning_commits * 1.5:
            return {'id': 'night_owl', 'icon': '🦉'}
            
        # 7. Weekend Warrior (Hafta Sonu Savaşçısı)
        if self.weekend_commits > 0 and self.weekend_commits > (total_commits * 0.3):
            return {'id': 'weekend_warrior', 'icon': '⚔️'}
            
        # 8. PR Machine (PR Makinesi)
        if total_prs > total_commits * 0.2 and total_prs > 20:
            return {'id': 'pr_machine', 'icon': '🤖'}
            
        # 9. Early Bird (Erkenci Kuş)
        if self.morning_commits > self.night_commits * 2:
            return {'id': 'early_bird', 'icon': '🌅'}
            
        # Default
        return {'id': 'consistent_coder', 'icon': '👨‍💻'}

    def _calculate_org_contributions(self, repo_map, username):
        """Organizasyon/diğer kullanıcı katkılarını hesaplar"""
        org_stats = defaultdict(lambda: {'commits': 0, 'prs': 0, 'repos': []})
        
        for repo_key, stats in repo_map.items():
            owner = stats.get('owner', '')
            if owner.lower() != username.lower():
                org_stats[owner]['commits'] += stats['commits']
                org_stats[owner]['prs'] += stats['prs']
                org_stats[owner]['repos'].append(stats['name'])
        
        sorted_orgs = sorted(org_stats.items(), key=lambda x: x[1]['commits'] + x[1]['prs'], reverse=True)[:5]
        
        return [
            {
                'name': org,
                'commits': data['commits'],
                'prs': data['prs'],
                'repos': len(data['repos']),
                'repo_names': data['repos'][:3]
            }
            for org, data in sorted_orgs if data['commits'] + data['prs'] > 0
        ]
    
    def _calculate_top_repos(self, repo_map):
        """En iyi repository'leri hesaplar"""
        if not repo_map:
            return {}
        
        repos_list = list(repo_map.values())
        
        most_commits = max(repos_list, key=lambda x: x['commits'])
        most_prs = max(repos_list, key=lambda x: x['prs'])
        most_changes = max(repos_list, key=lambda x: x.get('changes', 0))
        longest_contribution = max(repos_list, key=lambda x: x.get('contribution_days', 0))
        
        result = {
            'most_commits': {
                'name': most_commits['name'],
                'count': most_commits['commits'],
                'url': most_commits['url'],
                'is_private': most_commits.get('is_private', False)
            },
            'most_prs': {
                'name': most_prs['name'],
                'count': most_prs['prs'],
                'url': most_prs['url'],
                'is_private': most_prs.get('is_private', False)
            },
            'most_changes': {
                'name': most_changes['name'],
                'changes': most_changes.get('changes', 0),
                'additions': most_changes.get('additions', 0),
                'deletions': most_changes.get('deletions', 0),
                'url': most_changes['url'],
                'is_private': most_changes.get('is_private', False)
            },
            'longest_contribution': {
                'name': longest_contribution['name'],
                'days': longest_contribution.get('contribution_days', 0),
                'commits': longest_contribution['commits'],
                'url': longest_contribution['url'],
                'is_private': longest_contribution.get('is_private', False)
            }
        }
        
        # En çok star alan
        own_repos = [r for r in repos_list if r['is_own'] and r.get('stars', 0) > 0]
        if own_repos:
            most_starred = max(own_repos, key=lambda x: x.get('stars', 0))
            result['most_starred'] = {
                'name': most_starred['name'],
                'stars': most_starred.get('stars', 0),
                'forks': most_starred.get('forks', 0),
                'url': most_starred['url']
            }
        
        return result
    
    def _analyze_commit_messages(self, messages):
        """Commit mesajlarını analiz eder"""
        if not messages:
            return []
        
        counter = Counter(messages)
        most_common = counter.most_common(5)
        
        return [{'message': msg, 'count': count} for msg, count in most_common]
    
    def _calculate_language_distribution(self, languages):
        """Dil dağılımını yüzde olarak hesaplar"""
        if not languages:
            return {}
        
        total_bytes = sum(languages.values())
        distribution = {}
        
        for lang, bytes_count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:8]:
            percentage = (bytes_count / total_bytes) * 100
            distribution[lang] = round(percentage, 1)
        
        return distribution
    
    def _calculate_longest_streak(self, active_days):
        """En uzun ardışık gün serisini hesaplar"""
        if not active_days:
            return 0
        
        sorted_days = sorted(active_days)
        longest = 1
        current = 1
        
        for i in range(1, len(sorted_days)):
            diff = (sorted_days[i] - sorted_days[i-1]).days
            if diff == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        
        return longest
    
    def _analyze_with_rest_api(self, username, repos, api):
        """REST API fallback"""
        # Basitleştirilmiş fallback implementasyonu
        return {
            'username': username,
            'year': self.year,
            'stats': {
                'total_commits': 0,
                'total_contributions': 0,
                'total_additions': 0,
                'total_deletions': 0,
                'net_changes': 0
            },
            'top_repos': {},
            'commit_analysis': {'most_common_messages': [], 'monthly_distribution': {}},
            'languages': {},
            'org_contributions': []
        }