// DOM Elements
const inputSection = document.getElementById('input-section');
const loadingSection = document.getElementById('loading-section');
const resultsSection = document.getElementById('results-section');
const usernameInput = document.getElementById('username-input');
const analyzeBtn = document.getElementById('analyze-btn');
const errorMessage = document.getElementById('error-message');
const newSearchBtn = document.getElementById('new-search-btn');

// Global state
let userData = null;
let currentQuizIndex = 0;
let quizQuestions = [];
let currentImageBlob = null;

// Event Listeners
analyzeBtn.addEventListener('click', handleAnalyze);
newSearchBtn.addEventListener('click', () => {
    inputSection.style.display = 'block';
    resultsSection.style.display = 'none';
    usernameInput.value = '';
    usernameInput.focus();
});
usernameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleAnalyze();
});

// Modal Event Listeners
document.getElementById('preview-modal').addEventListener('click', (e) => {
    if (e.target.id === 'preview-modal') closeModal();
});

async function handleAnalyze() {
    const username = usernameInput.value.trim();
    if (!username) {
        showError('Lütfen kullanıcı adı girin');
        return;
    }
    hideError();
    showLoading();
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, year: 2025 })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Hata oluştu');
        
        userData = data;
        displayResults(data);
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

function showLoading() {
    inputSection.style.display = 'none';
    loadingSection.style.display = 'block';
    resultsSection.style.display = 'none';
    analyzeBtn.disabled = true;
    document.querySelector('.btn-text').style.display = 'none';
    document.querySelector('.btn-loader').style.display = 'inline-block';
}

function hideLoading() {
    loadingSection.style.display = 'none';
    analyzeBtn.disabled = false;
    document.querySelector('.btn-text').style.display = 'inline';
    document.querySelector('.btn-loader').style.display = 'none';
}

function showError(msg) {
    errorMessage.textContent = msg;
    errorMessage.style.display = 'block';
    inputSection.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}

function displayResults(data) {
    hideLoading();
    inputSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    // User Info
    document.getElementById('user-avatar').src = data.user_info.avatar_url;
    document.getElementById('user-name').textContent = data.user_info.name || data.username;
    document.getElementById('user-username').textContent = '@' + data.username;
    
    // Private notice
    const notice = document.getElementById('private-notice');
    if (data.has_private_contributions && data.has_token) {
        notice.style.display = 'block';
        notice.querySelector('.notice-text').textContent = '✓ Private repo katkıları dahil';
    } else if (!data.has_token) {
        notice.style.display = 'block';
        notice.querySelector('.notice-text').textContent = '⚠️ Private repo katkıları dahil değil';
    }
    
    // Results title
    document.querySelector('.results-title').style.display = 'block';
    document.querySelector('.visibility-controls').style.display = 'flex';
    
    // Hide all sections initially
    document.querySelectorAll('.collapsible-section').forEach(section => {
        section.style.display = 'none';
    });
    
    // ÖNCE Quiz'i göster
    generateQuiz(data);
    document.getElementById('quiz-section').style.display = 'block';
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function completeQuiz() {
    // Quiz tamamlandı, şimdi tüm istatistikleri göster
    document.getElementById('quiz-section').style.display = 'none';
    
    const data = userData;
    
    // Show all sections
    document.querySelectorAll('.collapsible-section').forEach(section => {
        section.style.display = 'block';
    });
    
    // Hero Stats
    animateNumber('total-commits', data.stats.total_contributions || data.stats.total_commits);
    animateNumber('total-repos', data.stats.total_repos);
    animateNumber('active-days', data.stats.active_days);
    animateNumber('longest-streak', data.stats.longest_streak);
    
    // Activity
    animateNumber('activity-commits', data.stats.total_commits);
    animateNumber('activity-prs', data.stats.total_prs || 0);
    animateNumber('activity-merges', data.stats.total_merges || 0);
    animateNumber('activity-issues', data.stats.total_issues || 0);
    animateNumber('activity-reviews', data.stats.total_reviews || 0);
    
    // Top Repos
    displayTopRepos(data.top_repos);
    
    // Stars & Forks
    animateNumber('stars-received', data.stats.total_merges || 0);
    animateNumber('forks-received', data.stats.forks_received || 0);
    animateNumber('repos-created', data.stats.repos_created || 0);
    animateNumber('repos-forked', data.stats.repos_forked || 0);
    
    // Created Repos
    displayCreatedRepos(data.created_repos || []);
    
    // Org Contributions
    displayOrgContributions(data.org_contributions || []);
    
    // Commit Messages
    displayCommitMessages(data.commit_analysis.most_common_messages);
    
    // Languages
    displayLanguages(data.languages);
    
    // Monthly Chart
    displayMonthlyChart(data.commit_analysis.monthly_distribution);
    
    // Contribution Split
    animateNumber('own-commits', data.stats.own_project_commits);
    animateNumber('others-commits', data.stats.others_project_commits);
    
    // Summary Stats
    displaySummaryStats(data.stats);

    // Persona Display
    if (data.persona) {
        displayPersona(data.persona);
    }
    
    // Scroll to hero stats
    setTimeout(() => {
        document.getElementById('sect-hero').scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 300);
}

function displayPersona(persona) {
    const t = translations[currentLang];
    const personaData = t.personas[persona.id] || t.personas['consistent_coder'];
    
    document.getElementById('persona-icon').textContent = persona.icon;
    document.getElementById('persona-title').textContent = personaData.title;
    document.getElementById('persona-desc').textContent = personaData.desc;
    document.getElementById('persona-section').style.display = 'block';
}

function generateQuiz(data) {
    const stats = data.stats;
    const topRepos = data.top_repos;
    const languages = data.languages;
    const t = translations[currentLang];
    
    quizQuestions = [];
    
    // Soru 1
    const actualCommits = stats.total_commits;
    const range = Math.max(50, Math.floor(actualCommits * 0.3));
    const options1 = [
        actualCommits,
        actualCommits - range,
        actualCommits + range,
        Math.floor(actualCommits * 0.5)
    ].map(n => Math.max(0, n));
    
    const emoji = actualCommits > 500 ? t.q1Emoji1 : actualCommits > 200 ? t.q1Emoji2 : t.q1Emoji3;
    
    quizQuestions.push({
        question: t.q1,
        options: shuffleArray(options1.map(n => n.toString())),
        correct: actualCommits.toString(),
        explanation: t.q1Explanation.replace('{count}', actualCommits.toLocaleString()).replace('{emoji}', emoji)
    });
    
    // Soru 2
    if (topRepos.most_commits && topRepos.most_commits.count > 0) {
        const correctRepo = topRepos.most_commits.name;
        const repoOptions = [correctRepo];
        if (topRepos.most_prs && topRepos.most_prs.name !== correctRepo) repoOptions.push(topRepos.most_prs.name);
        if (topRepos.longest_contribution && topRepos.longest_contribution.name !== correctRepo && repoOptions.length < 3) repoOptions.push(topRepos.longest_contribution.name);
        while (repoOptions.length < 4) repoOptions.push(`Repo-${repoOptions.length}`);
        
        quizQuestions.push({
            question: t.q2,
            options: shuffleArray(repoOptions),
            correct: correctRepo,
            explanation: t.q2Explanation.replace('{count}', topRepos.most_commits.count.toLocaleString()).replace('{repo}', correctRepo)
        });
    }
    
    // Soru 3
    if (languages && Object.keys(languages).length > 0) {
        const topLang = Object.keys(languages)[0];
        const langOptions = Object.keys(languages).slice(0, 3);
        const commonLangs = ['JavaScript', 'Python', 'Java', 'TypeScript', 'Go', 'C++', 'Ruby', 'PHP'];
        for (const lang of commonLangs) {
            if (langOptions.length >= 4) break;
            if (!langOptions.includes(lang)) langOptions.push(lang);
        }
        
        quizQuestions.push({
            question: t.q3,
            options: shuffleArray(langOptions.slice(0, 4)),
            correct: topLang,
            explanation: t.q3Explanation.replace('{lang}', topLang)
        });
    }
    
    currentQuizIndex = 0;
    showQuizQuestion();
}

function showQuizQuestion() {
    const quiz = quizQuestions[currentQuizIndex];
    const t = translations[currentLang];
    
    document.getElementById('quiz-current').textContent = currentQuizIndex + 1;
    document.querySelector('.quiz-title').textContent = t.quizTitle;
    document.getElementById('quiz-question').textContent = quiz.question;
    document.getElementById('quiz-result').style.display = 'none';
    document.getElementById('quiz-next-btn').style.display = 'none';
    document.getElementById('quiz-next-btn').textContent = t.quizContinue;
    
    const optionsContainer = document.getElementById('quiz-options');
    optionsContainer.innerHTML = '';
    
    quiz.options.forEach(option => {
        const btn = document.createElement('div');
        btn.className = 'quiz-option';
        btn.textContent = option;
        btn.onclick = () => selectQuizOption(option, quiz.correct);
        optionsContainer.appendChild(btn);
    });
}

function selectQuizOption(selected, correct) {
    const t = translations[currentLang];
    const options = document.querySelectorAll('.quiz-option');
    const isCorrect = selected === correct;
    
    options.forEach(opt => {
        opt.classList.add('disabled');
        opt.onclick = null;
        if (opt.textContent === correct) {
            opt.classList.add('correct');
        } else if (opt.textContent === selected && !isCorrect) {
            opt.classList.add('wrong');
        }
    });
    
    const quiz = quizQuestions[currentQuizIndex];
    const resultDiv = document.getElementById('quiz-result');
    resultDiv.innerHTML = `
        <h3>${isCorrect ? t.quizCorrect : t.quizWrong}</h3>
        <p>${quiz.explanation}</p>
    `;
    resultDiv.style.display = 'block';
    document.getElementById('quiz-next-btn').style.display = 'block';
}

function nextQuizQuestion() {
    currentQuizIndex++;
    if (currentQuizIndex < quizQuestions.length) {
        showQuizQuestion();
    } else {
        completeQuiz();
    }
}

function shuffleArray(array) {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

function shareOnTwitter() {
    const stats = userData.stats;
    const t = translations[currentLang];
    const text = t.xShareText
        .replace('{commits}', stats.total_commits.toLocaleString())
        .replace('{repos}', stats.total_repos)
        .replace('{days}', stats.active_days)
        .replace('{stars}', stats.stars_received || 0);
    window.open(`https://x.com/intent/tweet?text=${encodeURIComponent(text)}`, '_blank');
}

async function shareOnLinkedIn() {
    const btn = event.target.closest('.share-btn');
    const originalContent = btn.innerHTML;
    const t = translations[currentLang];
    
    btn.innerHTML = `<span class="loader" style="width: 16px; height: 16px; border-width: 2px;"></span> ${t.linkedinGenerating}`;
    btn.style.pointerEvents = 'none';
    
    try {
        const blob = await generateImageBlob();
        showPreviewModal(blob);
    } catch (error) {
        console.error('Error generating image:', error);
        alert('Error generating image. Please try again.');
    } finally {
        btn.innerHTML = originalContent;
        btn.style.pointerEvents = 'auto';
    }
}

function showPreviewModal(blob) {
    currentImageBlob = blob;
    const url = URL.createObjectURL(blob);
    document.getElementById('preview-image').src = url;
    
    const t = translations[currentLang];
    document.getElementById('modal-title').textContent = t.previewTitle;
    document.getElementById('modal-download-btn').textContent = t.download;
    document.getElementById('modal-share-btn').textContent = t.copyShare;
    
    document.getElementById('modal-download-btn').onclick = () => {
        const fileName = `github-wrapped-2025-${userData.username}.png`;
        downloadImage(currentImageBlob, fileName);
    };
    
    document.getElementById('modal-share-btn').onclick = handleModalShare;
    
    document.getElementById('preview-modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('preview-modal').style.display = 'none';
    const previewImg = document.getElementById('preview-image');
    if (previewImg.src && previewImg.src.startsWith('blob:')) {
        URL.revokeObjectURL(previewImg.src);
    }
}

async function handleModalShare() {
    if (!currentImageBlob) return;
    const t = translations[currentLang];
    const btn = document.getElementById('modal-share-btn');
    const originalText = btn.textContent;
    
    btn.textContent = '...';
    btn.disabled = true;

    try {
        await navigator.clipboard.write([
            new ClipboardItem({
                'image/png': currentImageBlob
            })
        ]);
        
        showToast(t.linkedinPaste, '✅');
        setTimeout(() => {
            window.open('https://www.linkedin.com/feed/?shareActive=true', '_blank');
            closeModal();
        }, 1500);
        
    } catch (err) {
        console.error('Clipboard failed', err);
        const fileName = `github-wrapped-2025-${userData.username}.png`;
        downloadImage(currentImageBlob, fileName);
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

function generateImageBlob() {
    return new Promise(async (resolve, reject) => {
        try {
            const canvas = await drawCanvas();
            canvas.toBlob((blob) => {
                if (blob) resolve(blob);
                else reject(new Error('Canvas to Blob failed'));
            }, 'image/png');
        } catch (e) {
            reject(e);
        }
    });
}

async function drawCanvas() {
    const t = translations[currentLang];
    const stats = userData.stats;
    const userInfo = userData.user_info;
    const persona = userData.persona;
    
    const canvas = document.createElement('canvas');
    canvas.width = 1200;
    canvas.height = 1500;
    const ctx = canvas.getContext('2d');
    
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, '#8B5CF6');
    gradient.addColorStop(1, '#3B82F6');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    const avatar = new Image();
    avatar.crossOrigin = 'anonymous';
    await new Promise((resolve, reject) => {
        avatar.onload = resolve;
        avatar.onerror = reject;
        avatar.src = userInfo.avatar_url;
    });
    
    const centerX = canvas.width / 2;
    const avatarY = 250;
    
    ctx.save();
    ctx.beginPath();
    ctx.arc(centerX, avatarY, 120, 0, Math.PI * 2);
    ctx.closePath();
    ctx.clip();
    ctx.drawImage(avatar, centerX - 120, avatarY - 120, 240, 240);
    ctx.restore();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 8;
    ctx.beginPath();
    ctx.arc(centerX, avatarY, 120, 0, Math.PI * 2);
    ctx.stroke();
    
    ctx.textAlign = 'center';
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 64px -apple-system, sans-serif';
    ctx.fillText(userInfo.name || userData.username, centerX, avatarY + 200);
    ctx.font = '40px -apple-system, sans-serif';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.fillText(`@${userData.username}`, centerX, avatarY + 260);
    
    ctx.font = 'bold 72px -apple-system, sans-serif';
    ctx.fillStyle = '#ffffff';
    ctx.fillText(t.wrappedTitle, centerX, 100);
    
    if (persona) {
        const personaData = t.personas[persona.id] || t.personas['consistent_coder'];
        const personaText = `${persona.icon} ${personaData.title}`;
        
        ctx.font = 'bold 52px -apple-system, sans-serif';
        const textMetrics = ctx.measureText(personaText);
        const bgWidth = textMetrics.width + 80;
        const bgHeight = 100;
        const bgX = centerX - bgWidth / 2;
        const bgY = avatarY + 320;
        
        ctx.fillStyle = 'rgba(0, 0, 0, 0.25)';
        ctx.beginPath();
        ctx.roundRect(bgX, bgY, bgWidth, bgHeight, 50);
        ctx.fill();
        
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        ctx.fillStyle = '#ffffff';
        ctx.fillText(personaText, centerX, bgY + 65);
    }
    
    const statsData = [
        { value: stats.total_commits.toLocaleString(), label: t.stats.commit },
        { value: stats.total_repos.toString(), label: t.stats.projects },
        { value: stats.active_days.toString(), label: t.stats.activeDays },
        { value: (stats.total_merges || 0).toString(), label: 'Merge' },
        { value: (stats.total_prs || 0).toString(), label: t.stats.totalPRs },
        { value: stats.longest_streak.toString(), label: t.stats.longestStreakDays }
    ];
    
    const boxWidth = 350;
    const boxHeight = 220;
    const boxGap = 40;
    const startY = 750;
    
    statsData.forEach((stat, index) => {
        const row = Math.floor(index / 2);
        const col = index % 2;
        const totalGridWidth = (boxWidth * 2) + boxGap;
        const gridStartX = (canvas.width - totalGridWidth) / 2;
        
        const x = gridStartX + col * (boxWidth + boxGap);
        const y = startY + row * (boxHeight + boxGap);
        
        ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.beginPath();
        ctx.roundRect(x, y, boxWidth, boxHeight, 20);
        ctx.fill();
        
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 64px -apple-system, sans-serif';
        ctx.fillText(stat.value, x + boxWidth / 2, y + 100);
        
        ctx.font = '32px -apple-system, sans-serif';
        ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
        ctx.fillText(stat.label, x + boxWidth / 2, y + 160);
    });
    
    ctx.font = '24px -apple-system, sans-serif';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
    // ctx.fillText(window.location.host, centerX, canvas.height - 30);
    
    return canvas;
}

function downloadImage(blob, fileName) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('Görsel indirildi.', '⬇️');
}

function showToast(message, icon = 'ℹ️') {
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) existingToast.remove();
    
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, 400);
    }, 4000);
}

// Stats Helpers
function displaySummaryStats(stats) {
    const container = document.getElementById('summary-stats');
    const allStats = [
        { label: 'Toplam Katkı', value: stats.total_contributions || stats.total_commits },
        { label: 'Toplam Commit', value: stats.total_commits },
        { label: 'Pull Request', value: stats.total_prs || 0 },
        { label: 'Merge', value: stats.total_merges || 0 },
        { label: 'Issue', value: stats.total_issues || 0 },
        { label: 'Review', value: stats.total_reviews || 0 },
        { label: 'Aktif Proje', value: stats.total_repos },
        { label: 'Aktif Gün', value: stats.active_days },
        { label: 'En Uzun Seri', value: stats.longest_streak },
        { label: 'Aldığı Star', value: stats.stars_received || 0 },
        { label: 'Aldığı Fork', value: stats.forks_received || 0 },
        { label: 'Oluşturulan Repo', value: stats.repos_created || 0 }
    ];
    
    container.innerHTML = allStats.map(stat => `
        <div class="summary-item">
            <span class="summary-label">${stat.label}</span>
            <span class="summary-value">${stat.value.toLocaleString()}</span>
        </div>
    `).join('');
}

function animateNumber(elementId, targetValue) {
    const element = document.getElementById(elementId);
    const duration = 1500;
    const steps = 50;
    const stepValue = targetValue / steps;
    let currentValue = 0;
    let currentStep = 0;
    const interval = setInterval(() => {
        currentStep++;
        currentValue += stepValue;
        if (currentStep >= steps) {
            currentValue = targetValue;
            clearInterval(interval);
        }
        element.textContent = Math.floor(currentValue).toLocaleString();
    }, duration / steps);
}

function displayTopRepos(topRepos) {
    const container = document.getElementById('top-repos-container');
    container.innerHTML = '';
    const repos = [
        { title: 'En Çok Commit', data: topRepos.most_commits, key: 'count', unit: 'commit' },
        { title: 'En Çok PR', data: topRepos.most_prs, key: 'count', unit: 'PR' },
        { title: 'En Çok Değişiklik', data: topRepos.most_changes, key: 'changes', unit: 'değişiklik' },
        { title: 'En Uzun Katkı', data: topRepos.longest_contribution, key: 'days', unit: 'gün' }
    ];
    if (topRepos.most_starred) {
        repos.push({ title: 'En Çok Star', data: topRepos.most_starred, key: 'stars', unit: 'star' });
    }
    repos.forEach(repo => {
        const card = document.createElement('div');
        card.className = 'repo-card';
        card.innerHTML = `
            <div class="repo-header">
                <a href="${repo.data.url}" target="_blank" class="repo-name">${repo.data.name}</a>
                <span class="repo-badge">${repo.title}</span>
            </div>
            <p class="repo-stat"><strong>${repo.data[repo.key].toLocaleString()}</strong> ${repo.unit}</p>
        `;
        container.appendChild(card);
    });
}

function displayCreatedRepos(repos) {
    const container = document.getElementById('created-repos-container');
    if (!repos || repos.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary);">Bu yıl yeni repo oluşturulmadı</p>';
        return;
    }
    container.innerHTML = repos.map(repo => `
        <div class="created-repo-item">
            <a href="${repo.url}" target="_blank" class="created-repo-name">${repo.name}</a>
            <p class="created-repo-desc">${repo.description}</p>
            <div class="created-repo-stats">
                <span>⭐ ${repo.stars}</span>
                <span>🍴 ${repo.forks}</span>
                <span>${repo.language || 'N/A'}</span>
            </div>
        </div>
    `).join('');
}

function displayOrgContributions(orgs) {
    const container = document.getElementById('org-container');
    if (!orgs || orgs.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary);">Organizasyon katkısı yok</p>';
        return;
    }
    container.innerHTML = orgs.map(org => `
        <div class="org-item">
            <div class="org-header">
                <span class="org-name">${org.name}</span>
                <span class="org-count">${org.repos} repo</span>
            </div>
            <div class="org-stats">
                <span>💻 ${org.commits} commit</span>
                <span>🔀 ${org.prs} PR</span>
            </div>
            <div class="org-repos">${org.repo_names.join(', ')}</div>
        </div>
    `).join('');
}

function displayCommitMessages(messages) {
    const container = document.getElementById('commit-messages-container');
    if (!messages || messages.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary);">Commit mesajı bulunamadı</p>';
        return;
    }
    container.innerHTML = messages.map(msg => `
        <div class="commit-message-item">
            <span class="message-text">${escapeHtml(msg.message)}</span>
            <span class="message-count">${msg.count}</span>
        </div>
    `).join('');
}

function displayLanguages(languages) {
    const container = document.getElementById('languages-container');
    if (!languages || Object.keys(languages).length === 0) {
        const t = translations[currentLang];
        container.innerHTML = `<p style="color: var(--text-secondary);">${currentLang === 'tr' ? 'Dil bilgisi bulunamadı' : 'No language data found'}</p>`;
        return;
    }
    container.innerHTML = Object.entries(languages).map(([lang, percent]) => `
        <div class="language-item">
            <span class="language-name">${lang}</span>
            <div class="language-bar-container">
                <div class="language-bar" style="width: 0%">
                    <span class="language-percentage">${percent}%</span>
                </div>
            </div>
        </div>
    `).join('');
    setTimeout(() => {
        document.querySelectorAll('.language-bar').forEach((bar, i) => {
            bar.style.width = Object.values(languages)[i] + '%';
        });
    }, 100);
}

function displayMonthlyChart(monthlyData) {
    const container = document.getElementById('monthly-chart');
    const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    const monthNames = { 'January': 'Oca', 'February': 'Şub', 'March': 'Mar', 'April': 'Nis', 'May': 'May', 'June': 'Haz', 'July': 'Tem', 'August': 'Ağu', 'September': 'Eyl', 'October': 'Eki', 'November': 'Kas', 'December': 'Ara' };
    const maxValue = Math.max(...Object.values(monthlyData), 1);
    container.innerHTML = months.map(month => {
        const value = monthlyData[month] || 0;
        const heightPercent = (value / maxValue) * 100;
        return `
            <div class="month-bar">
                <div class="month-bar-fill">
                    <div class="month-bar-inner" style="height: 0%">
                        <span class="month-value">${value}</span>
                    </div>
                </div>
                <span class="month-label">${monthNames[month]}</span>
            </div>
        `;
    }).join('');
    setTimeout(() => {
        document.querySelectorAll('.month-bar-inner').forEach((bar, i) => {
            const value = monthlyData[months[i]] || 0;
            const heightPercent = (value / maxValue) * 100;
            bar.style.height = Math.max(heightPercent, 30) + '%';
        });
    }, 200);
}

function toggleSection(id) {
    const section = document.getElementById(id);
    const parent = section ? section.closest('.collapsible-section') : document.getElementById(id).closest('.collapsible-section');
    const icon = parent.querySelector('.toggle-icon');
    const content = parent.querySelector('.section-content');
    const isHidden = content.style.display === 'none';
    content.style.display = isHidden ? 'block' : 'none';
    icon.textContent = isHidden ? '▼' : '▶';
}

function toggleAllSections(show) {
    document.querySelectorAll('.collapsible-section').forEach(section => {
        const content = section.querySelector('.section-content');
        const icon = section.querySelector('.toggle-icon');
        content.style.display = show ? 'block' : 'none';
        icon.textContent = show ? '▼' : '▶';
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showLinkedInCard() {
    // Deprecated but kept for compatibility
}

function closeLinkedInCard() {
    const overlay = document.querySelector('.share-overlay');
    const card = document.getElementById('linkedin-card');
    if (overlay) overlay.remove();
    if (card) card.remove();
}

function copyShareLink() {
    const url = window.location.origin;
    navigator.clipboard.writeText(url).then(() => {
        const btn = event.target.closest('.share-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="share-icon">✅</span> Kopyalandı!';
        setTimeout(() => {
            btn.innerHTML = originalText;
        }, 2000);
    });
}

usernameInput.focus();