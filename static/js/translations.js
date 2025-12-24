// Translations
const translations = {
    tr: {
        title: 'GitHub Wrapped',
        subtitle: '2025 yılındaki GitHub aktivitelerinizi keşfedin',
        inputPlaceholder: 'GitHub kullanıcı adı',
        analyzeBtn: 'Analiz Et',
        example: 'Örnek: 4ni1ak, torvalds',
        loading: 'Veriler analiz ediliyor...',
        privateIncluded: '✓ Private repo katkıları dahil',
        privateNotIncluded: '⚠️ Private repo katkıları dahil değil',
        resultsTitle: '2025 GitHub Özetiniz',
        resultsSubtitle: 'İşte tüm istatistikleriniz!',
        wrappedTitle: '🎉 2025 GitHub Özetim',
        hideAll: 'Tümünü Gizle',
        previewTitle: 'Görsel Önizleme',
        copyShare: 'Panoya Kopyala & Paylaş',
        download: 'İndir',
        close: 'Kapat',
        personas: {
            polyglot: { title: 'Polyglot', desc: 'Sınır tanımayan bir dil ustasısın! 🌍' },
            night_owl: { title: 'Gece Kuşu', desc: 'Geceleri kod yazmak senin süper gücün! 🦉' },
            weekend_warrior: { title: 'Hafta Sonu Savaşçısı', desc: 'Hafta sonlarını koda adıyorsun! ⚔️' },
            pr_machine: { title: 'PR Makinesi', desc: 'İşbirliği ve katkı senin göbek adın! 🤖' },
            early_bird: { title: 'Erkenci Kuş', desc: 'Güne kodla başlıyorsun! 🌅' },
            consistent_coder: { title: 'İstikrarlı Kodlayıcı', desc: 'Düzenli ve güvenilir bir geliştiricisin! 👨‍💻' },
            marathon_runner: { title: 'Maratoncu', desc: 'İnanılmaz bir commit serisine sahipsin! 🏃' },
            star_gazer: { title: 'Yıldız Avcısı', desc: 'Projelerinle herkesin ilgisini çekiyorsun! 🤩' },
            the_reviewer: { title: 'Gözlemci', desc: 'Kod kalitesini artırmak senin işin! 👀' },
            bug_hunter: { title: 'Böcek Avcısı', desc: 'Hiçbir hata senden kaçamaz! 🐛' }
        },
        showAll: 'Tümünü Göster',
        quizTitle: '🎯 Tahmin Et!',
        quizContinue: 'Devam Et →',
        quizCorrect: '✅ Doğru!',
        quizWrong: '❌ Yanlış!',
        q1: '2025 yılında kaç commit attığını tahmin et?',
        q1Explanation: 'Tam olarak {count} commit attınız! {emoji}',
        q1Emoji1: '🔥 İnanılmaz!',
        q1Emoji2: '💪 Harika!',
        q1Emoji3: '👍 Güzel çalışma!',
        q2: 'En çok hangi projeye commit attın?',
        q2Explanation: '{count} commit ile "{repo}" en aktif projeniz! 🏆',
        q3: "2025'te en çok hangi programlama dilini kullandın?",
        q3Explanation: '"{lang}" en çok kullandığınız dil! 🔤',
        shareTitle: '📤 Paylaş ve Destek Ol',
        shareX: "X'te Paylaş",
        shareLinkedIn: "LinkedIn'de Paylaş",
        copyLink: 'Linki Kopyala',
        copied: '✅ Kopyalandı!',
        supportText: 'Bu projeyi beğendiniz mi?',
        starGitHub: "GitHub'da Star Ver",
        otherProjects: 'Diğer Projelerim',
        newSearch: 'Yeni Arama',
        madeWith: 'Made with ❤️ by',
        xShareText: '🎉 Benim 2025 GitHub Wrapped sonuçlarım!\n\n💻 {commits} Commit\n📦 {repos} Proje\n🔥 {days} Aktif Gün\n⭐ {stars} Star\n\nSenin sonuçların nasıl? #GitHubWrapped',
        linkedinGenerating: '📸 LinkedIn görseli oluşturuluyor...',
        linkedinReady: '✅ Görsel hazır! İndirip LinkedIn\'de paylaşabilirsiniz.',
        linkedinPaste: '✅ Görsel kopyalandı! LinkedIn açılıyor, lütfen orada yapıştırın (Ctrl+V).',
        stats: {
            totalContribution: 'Toplam Katkı',
            projects: 'Proje',
            activeDays: 'Aktif Gün',
            longestStreak: 'En Uzun Seri',
            commit: 'Commit',
            pullRequest: 'Pull Request',
            merge: 'Merge',
            issue: 'Issue',
            review: 'Review',
            starsReceived: 'Aldığınız Star',
            forksReceived: 'Aldığınız Fork',
            reposCreated: 'Oluşturulan',
            reposForked: 'Fork Edilen',
            ownProjects: 'Kendi Projelerim',
            othersProjects: 'Diğer Projeler',
            totalCommits: 'Toplam Commit',
            totalPRs: 'Pull Request',
            totalMerges: 'Merge',
            totalIssues: 'Issue',
            totalReviews: 'Review',
            activeProjects: 'Aktif Proje',
            longestStreakDays: 'En Uzun Seri',
            createdRepos: 'Oluşturulan Repo'
        },
        sections: {
            heroStats: '📊 Ana İstatistikler',
            activity: '📈 Aktivite Dağılımı',
            topRepos: '🏆 En Aktif Projeler',
            starsForks: '⭐ Star & Fork',
            created: "🆕 2025'te Oluşturulan",
            org: '🏢 Organizasyon Katkıları',
            commits: '💬 Commit Mesajları',
            langs: '🔤 2025\'te Kullanılan Diller',
            monthly: '📅 Aylık Aktivite',
            split: '🎯 Katkı Dağılımı',
            summary: '📊 Tüm İstatistikler'
        },
        repoLabels: {
            mostCommits: 'En Çok Commit',
            mostPRs: 'En Çok PR',
            mostChanges: 'En Çok Değişiklik',
            longestContribution: 'En Uzun Katkı',
            mostStarred: 'En Çok Star',
            commits: 'commit',
            prs: 'PR',
            changes: 'değişiklik',
            days: 'gün',
            stars: 'star'
        }
    },
    en: {
        title: 'GitHub Wrapped',
        subtitle: 'Discover your GitHub activity in 2025',
        inputPlaceholder: 'GitHub username',
        analyzeBtn: 'Analyze',
        example: 'Example: 4ni1ak, torvalds',
        loading: 'Analyzing data...',
        privateIncluded: '✓ Private repo contributions included',
        privateNotIncluded: '⚠️ Private repo contributions not included',
        resultsTitle: 'Your 2025 GitHub Wrapped',
        resultsSubtitle: 'Here are all your statistics!',
        wrappedTitle: '🎉 2025 GitHub Wrapped',
        hideAll: 'Hide All',
        previewTitle: 'Image Preview',
        copyShare: 'Copy & Share',
        download: 'Download',
        close: 'Close',
        personas: {
            polyglot: { title: 'Polyglot', desc: 'A master of many languages! 🌍' },
            night_owl: { title: 'Night Owl', desc: 'Coding at night is your superpower! 🦉' },
            weekend_warrior: { title: 'Weekend Warrior', desc: 'Dedicating weekends to code! ⚔️' },
            pr_machine: { title: 'PR Machine', desc: 'Collaboration is your middle name! 🤖' },
            early_bird: { title: 'Early Bird', desc: 'Starting the day with code! 🌅' },
            consistent_coder: { title: 'Consistent Coder', desc: 'Reliable and steady developer! 👨‍💻' },
            marathon_runner: { title: 'Marathon Runner', desc: 'You have an incredible commit streak! 🏃' },
            star_gazer: { title: 'Star Gazer', desc: 'Your projects attract everyone\'s attention! 🤩' },
            the_reviewer: { title: 'The Reviewer', desc: 'Improving code quality is your job! 👀' },
            bug_hunter: { title: 'Bug Hunter', desc: 'No bug can escape from you! 🐛' }
        },
        showAll: 'Show All',
        quizTitle: '🎯 Guess!',
        quizContinue: 'Continue →',
        quizCorrect: '✅ Correct!',
        quizWrong: '❌ Wrong!',
        q1: 'Guess how many commits you made in 2025?',
        q1Explanation: 'Exactly {count} commits! {emoji}',
        q1Emoji1: '🔥 Incredible!',
        q1Emoji2: '💪 Great!',
        q1Emoji3: '👍 Good work!',
        q2: 'Which project did you commit to most?',
        q2Explanation: '{count} commits to "{repo}" - your most active project! 🏆',
        q3: 'Which programming language did you use most in 2025?',
        q3Explanation: '"{lang}" is your most used language! 🔤',
        shareTitle: '📤 Share and Support',
        shareX: 'Share on X',
        shareLinkedIn: 'Share on LinkedIn',
        copyLink: 'Copy Link',
        copied: '✅ Copied!',
        supportText: 'Did you like this project?',
        starGitHub: 'Star on GitHub',
        otherProjects: 'My Other Projects',
        newSearch: 'New Search',
        madeWith: 'Made with ❤️ by',
        xShareText: '🎉 My 2025 GitHub Wrapped results!\n\n💻 {commits} Commits\n📦 {repos} Projects\n🔥 {days} Active Days\n⭐ {stars} Stars\n\nWhat are your stats? #GitHubWrapped',
        linkedinGenerating: '📸 Generating LinkedIn image...',
        linkedinReady: '✅ Image ready! Download and share on LinkedIn.',
        linkedinPaste: '✅ Image copied! Opening LinkedIn, please paste it there (Ctrl+V).',
        stats: {
            totalContribution: 'Total Contributions',
            projects: 'Projects',
            activeDays: 'Active Days',
            longestStreak: 'Longest Streak',
            commit: 'Commits',
            pullRequest: 'Pull Requests',
            merge: 'Merges',
            issue: 'Issues',
            review: 'Reviews',
            starsReceived: 'Stars Received',
            forksReceived: 'Forks Received',
            reposCreated: 'Created',
            reposForked: 'Forked',
            ownProjects: 'My Projects',
            othersProjects: 'Other Projects',
            totalCommits: 'Total Commits',
            totalPRs: 'Pull Requests',
            totalMerges: 'Merges',
            totalIssues: 'Issues',
            totalReviews: 'Reviews',
            activeProjects: 'Active Projects',
            longestStreakDays: 'Longest Streak',
            createdRepos: 'Created Repos'
        },
        sections: {
            heroStats: '📊 Main Statistics',
            activity: '📈 Activity Breakdown',
            topRepos: '🏆 Most Active Projects',
            starsForks: '⭐ Stars & Forks',
            created: '🆕 Created in 2025',
            org: '🏢 Organization Contributions',
            commits: '💬 Commit Messages',
            langs: '🔤 Languages Used in 2025',
            monthly: '📅 Monthly Activity',
            split: '🎯 Contribution Split',
            summary: '📊 All Statistics'
        },
        repoLabels: {
            mostCommits: 'Most Commits',
            mostPRs: 'Most PRs',
            mostChanges: 'Most Changes',
            longestContribution: 'Longest Contribution',
            mostStarred: 'Most Starred',
            commits: 'commits',
            prs: 'PRs',
            changes: 'changes',
            days: 'days',
            stars: 'stars'
        }
    }
};

let currentLang = 'tr';

function toggleLanguage() {
    currentLang = currentLang === 'tr' ? 'en' : 'tr';
    document.getElementById('lang-icon').textContent = currentLang === 'tr' ? '🇬🇧' : '🇹🇷';
    document.getElementById('lang-text').textContent = currentLang === 'tr' ? 'EN' : 'TR';
    localStorage.setItem('lang', currentLang);
    updateLanguage();
}

function updateLanguage() {
    const t = translations[currentLang];
    
    // Update static texts
    const titleElement = document.querySelector('.title');
    if (titleElement) {
        const textNode = Array.from(titleElement.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
        if (textNode) textNode.textContent = ' ' + t.title;
    }
    
    const subtitleElement = document.querySelector('.subtitle');
    if (subtitleElement) subtitleElement.textContent = t.subtitle;
    
    const inputElement = document.getElementById('username-input');
    if (inputElement) inputElement.placeholder = t.inputPlaceholder;
    
    const btnTextElement = document.querySelector('.btn-text');
    if (btnTextElement) btnTextElement.textContent = t.analyzeBtn;
    
    const examplesElement = document.querySelector('.examples p');
    if (examplesElement) examplesElement.textContent = t.example;
    
    const loadingTextElement = document.querySelector('.loading-text');
    if (loadingTextElement) loadingTextElement.textContent = t.loading;
    
    // Update buttons
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    if (toggleBtns[0]) toggleBtns[0].textContent = t.hideAll;
    if (toggleBtns[1]) toggleBtns[1].textContent = t.showAll;
    
    const newSearchBtn = document.getElementById('new-search-btn');
    if (newSearchBtn) newSearchBtn.textContent = t.newSearch;
    
    // Update share buttons
    const shareButtons = document.querySelectorAll('.share-btn');
    shareButtons.forEach(btn => {
        if (btn.classList.contains('twitter')) {
            btn.innerHTML = `<span class="share-icon">✖️</span> ${t.shareX}`;
        } else if (btn.classList.contains('linkedin')) {
            btn.innerHTML = `<span class="share-icon">💼</span> ${t.shareLinkedIn}`;
        } else if (btn.classList.contains('copy')) {
            btn.innerHTML = `<span class="share-icon">🔗</span> ${t.copyLink}`;
        }
    });
    
    // Update support section
    const shareTitle = document.querySelector('.share-title');
    if (shareTitle) shareTitle.textContent = t.shareTitle;
    
    const supportText = document.querySelector('.support-text');
    if (supportText) supportText.textContent = t.supportText;
    
    const supportButtons = document.querySelectorAll('.support-btn');
    supportButtons.forEach(btn => {
        if (btn.classList.contains('github')) {
            btn.innerHTML = `<span>⭐</span> ${t.starGitHub}`;
        } else if (btn.classList.contains('projects')) {
            btn.innerHTML = `<span>💼</span> ${t.otherProjects}`;
        }
    });
    
    // Update section headers if results are showing
    if (typeof userData !== 'undefined' && userData) {
        const resultsTitleH1 = document.querySelector('.results-title h1');
        if (resultsTitleH1) resultsTitleH1.textContent = t.resultsTitle;
        
        const resultsTitleP = document.querySelector('.results-title p');
        if (resultsTitleP) resultsTitleP.textContent = t.resultsSubtitle;
        
        // Update section titles
        document.querySelectorAll('.section-header h3').forEach(header => {
            const text = header.textContent.trim();
            if (text.includes('Ana İstatistikler') || text.includes('Main Statistics')) {
                header.textContent = t.sections.heroStats;
            } else if (text.includes('Aktivite') || text.includes('Activity')) {
                header.textContent = t.sections.activity;
            } else if (text.includes('En Aktif') || text.includes('Most Active')) {
                header.textContent = t.sections.topRepos;
            } else if (text.includes('Star')) {
                header.textContent = t.sections.starsForks;
            } else if (text.includes('Oluşturulan') || text.includes('Created')) {
                header.textContent = t.sections.created;
            } else if (text.includes('Organizasyon') || text.includes('Organization')) {
                header.textContent = t.sections.org;
            } else if (text.includes('Commit Mesaj') || text.includes('Commit Messages')) {
                header.textContent = t.sections.commits;
            } else if (text.includes('Kullanılan Dil') || text.includes('Languages')) {
                header.textContent = t.sections.langs;
            } else if (text.includes('Aylık') || text.includes('Monthly')) {
                header.textContent = t.sections.monthly;
            } else if (text.includes('Katkı Dağılım') || text.includes('Contribution Split')) {
                header.textContent = t.sections.split;
            } else if (text.includes('Tüm İstatistik') || text.includes('All Statistics')) {
                header.textContent = t.sections.summary;
            }
        });
        
        // Update stat labels
        updateStatLabels(t);
    }
}

function updateStatLabels(t) {
    const statLabels = document.querySelectorAll('.stat-label');
    statLabels.forEach(label => {
        const text = label.textContent.trim();
        if (text.includes('Toplam Katkı') || text.includes('Total Contribution')) {
            label.textContent = t.stats.totalContribution;
        } else if (text.includes('Proje') || text.includes('Project')) {
            label.textContent = t.stats.projects;
        } else if (text.includes('Aktif Gün') || text.includes('Active Days')) {
            label.textContent = t.stats.activeDays;
        } else if (text.includes('En Uzun Seri') || text.includes('Longest Streak')) {
            label.textContent = t.stats.longestStreak;
        }
    });
    
    const activityLabels = document.querySelectorAll('.activity-label');
    activityLabels.forEach(label => {
        const text = label.textContent.trim();
        if (text === 'Commit' || text === 'Commits') {
            label.textContent = t.stats.commit;
        } else if (text === 'Pull Request' || text === 'Pull Requests') {
            label.textContent = t.stats.pullRequest;
        } else if (text === 'Merge' || text === 'Merges') {
            label.textContent = t.stats.merge;
        } else if (text === 'Issue' || text === 'Issues') {
            label.textContent = t.stats.issue;
        } else if (text === 'Review' || text === 'Reviews') {
            label.textContent = t.stats.review;
        }
    });
}

function toggleTheme() {
    document.body.classList.toggle('light-theme');
    const isLight = document.body.classList.contains('light-theme');
    document.getElementById('theme-icon').textContent = isLight ? '☀️' : '🌙';
    document.getElementById('theme-text').textContent = isLight ? 'Light' : 'Dark';
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
}

// Load saved preferences
window.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('lang');
    if (savedLang && savedLang !== currentLang) {
        currentLang = savedLang;
        document.getElementById('lang-icon').textContent = currentLang === 'tr' ? '🇬🇧' : '🇹🇷';
        document.getElementById('lang-text').textContent = currentLang === 'tr' ? 'EN' : 'TR';
    }
    
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        document.getElementById('theme-icon').textContent = '☀️';
        document.getElementById('theme-text').textContent = 'Light';
    }
    
    updateLanguage();
});