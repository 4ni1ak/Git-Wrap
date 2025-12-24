import requests
from datetime import datetime
import time

class GitHubAPI:
    def __init__(self, token=None):
        self.base_url = "https://api.github.com"
        self.graphql_url = "https://api.github.com/graphql"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, url, params=None):
        """API isteği yapar, rate limit kontrolü yapar ve bağlantı hatalarını tekrar dener"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=10)
                
                # Rate limit kontrolü
                remaining = response.headers.get('X-RateLimit-Remaining')
                if remaining and int(remaining) < 10:
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    wait_time = max(0, reset_time - time.time())
                    if wait_time > 0:
                        print(f"Rate limit approaching, waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                
                response.raise_for_status()
                return response.json()
                
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                print(f"⚠️  Connection warning (Attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print(f"❌ API Connection Error after {max_retries} attempts.")
                    raise Exception("GitHub sunucularına bağlanılamıyor. Lütfen internet bağlantınızı kontrol edip tekrar deneyin.")
            except requests.exceptions.RequestException as e:
                print(f"API Error: {str(e)}")
                return None
        return None
    
    def _make_graphql_request(self, query):
        """GraphQL API isteği yapar"""
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    self.graphql_url,
                    json={"query": query},
                    timeout=15
                )
                response.raise_for_status()
                return response.json()
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                print(f"⚠️  GraphQL Connection warning (Attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    # GraphQL hatası kritik olmayabilir, REST fallback var.
                    # Bu yüzden Exception fırlatmak yerine None dönüyoruz, ama logluyoruz.
                    print(f"❌ GraphQL Error after {max_retries} attempts.")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"GraphQL API Error: {str(e)}")
                return None
        return None
    
    def get_user(self, username):
        """Kullanıcı bilgilerini çeker"""
        url = f"{self.base_url}/users/{username}"
        return self._make_request(url)
    
    def get_user_repos(self, username):
        """Kullanıcının tüm public repository'lerini çeker"""
        repos = []
        page = 1
        per_page = 100
        
        while True:
            url = f"{self.base_url}/users/{username}/repos"
            params = {
                "per_page": per_page,
                "page": page,
                "sort": "updated",
                "direction": "desc"
            }
            
            data = self._make_request(url, params)
            if not data:
                break
            
            repos.extend(data)
            
            if len(data) < per_page:
                break
            
            page += 1
        
        return repos
    
    def get_repo_commits(self, owner, repo, since=None, until=None):
        """Repository'nin commit'lerini çeker"""
        commits = []
        page = 1
        per_page = 100
        
        while True:
            url = f"{self.base_url}/repos/{owner}/{repo}/commits"
            params = {
                "per_page": per_page,
                "page": page
            }
            
            if since:
                params["since"] = since
            if until:
                params["until"] = until
            
            data = self._make_request(url, params)
            if not data:
                break
            
            commits.extend(data)
            
            if len(data) < per_page:
                break
            
            page += 1
        
        return commits
    
    def get_repo_stats(self, owner, repo):
        """Repository istatistiklerini çeker"""
        url = f"{self.base_url}/repos/{owner}/{repo}/stats/contributors"
        return self._make_request(url)
    
    def get_repo_pulls(self, owner, repo, state="all"):
        """Repository pull request'lerini çeker"""
        pulls = []
        page = 1
        per_page = 100
        
        while True:
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
            params = {
                "state": state,
                "per_page": per_page,
                "page": page
            }
            
            data = self._make_request(url, params)
            if not data:
                break
            
            pulls.extend(data)
            
            if len(data) < per_page:
                break
            
            page += 1
        
        return pulls
    
    def get_repo_branches(self, owner, repo):
        """Repository branch'lerini çeker"""
        url = f"{self.base_url}/repos/{owner}/{repo}/branches"
        return self._make_request(url)
    
    def get_repo_languages(self, owner, repo):
        """Repository dillerini çeker"""
        url = f"{self.base_url}/repos/{owner}/{repo}/languages"
        return self._make_request(url)
    
    def get_user_events(self, username, page=1, per_page=100):
        """Kullanıcının event'lerini çeker"""
        url = f"{self.base_url}/users/{username}/events"
        params = {"per_page": per_page, "page": page}
        return self._make_request(url, params)
    
    def get_contributions_collection(self, username, from_date, to_date):
        """
        GraphQL kullanarak kullanıcının contribution verilerini çeker
        Bu private repo contribution'ları da içerir
        """
        query = f"""
        {{
          user(login: "{username}") {{
            contributionsCollection(from: "{from_date}", to: "{to_date}") {{
              contributionCalendar {{
                totalContributions
                weeks {{
                  contributionDays {{
                    contributionCount
                    date
                  }}
                }}
              }}
              commitContributionsByRepository {{
                contributions {{
                  totalCount
                }}
                repository {{
                  name
                  owner {{
                    login
                  }}
                  nameWithOwner
                  url
                  isPrivate
                  primaryLanguage {{
                    name
                  }}
                }}
              }}
              pullRequestContributionsByRepository {{
                contributions {{
                  totalCount
                }}
                repository {{
                  name
                  nameWithOwner
                  url
                  isPrivate
                }}
              }}
              totalCommitContributions
              totalPullRequestContributions
              totalIssueContributions
              totalPullRequestReviewContributions
            }}
          }}
        }}
        """
        
        result = self._make_graphql_request(query)
        if result and 'data' in result and result['data'] and result['data'].get('user'):
            return result['data']['user']['contributionsCollection']
        return None
    
    def get_rate_limit(self):
        """Kalan rate limit'i kontrol eder"""
        url = f"{self.base_url}/rate_limit"
        return self._make_request(url)
    
    def get_user_starred(self, username):
        """Kullanıcının star verdiği repository'leri çeker"""
        starred = []
        page = 1
        per_page = 100
        
        while page <= 3:  # Maksimum 300 starred repo (rate limit için)
            url = f"{self.base_url}/users/{username}/starred"
            params = {
                "per_page": per_page,
                "page": page
            }
            
            data = self._make_request(url, params)
            if not data:
                break
            
            starred.extend(data)
            
            if len(data) < per_page:
                break
            
            page += 1
        
        return starred