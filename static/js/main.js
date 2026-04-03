// Navbar scroll effect
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        if (window.scrollY > 20) navbar.classList.add('scrolled');
        else navbar.classList.remove('scrolled');
    }
});

(function () {
    const movieInput = document.getElementById('movieInput');
    const autocomplete = document.getElementById('autocomplete');
    const mainForm = document.getElementById('mainForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');

    let debounceTimer = null;

    if (movieInput && autocomplete) {
        movieInput.addEventListener('input', function () {
            clearTimeout(debounceTimer);
            const q = this.value.trim();
            if (q.length < 2) {
                autocomplete.innerHTML = '';
                return;
            }
            debounceTimer = setTimeout(function () {
                fetch('/api/search?q=' + encodeURIComponent(q))
                    .then(function (r) { return r.json(); })
                    .then(function (results) {
                        autocomplete.innerHTML = '';
                        results.forEach(function (title) {
                            const div = document.createElement('div');
                            div.className = 'ac-item';
                            div.textContent = title;
                            div.addEventListener('click', function () {
                                movieInput.value = title;
                                autocomplete.innerHTML = '';
                            });
                            autocomplete.appendChild(div);
                        });
                    });
            }, 200);
        });

        document.addEventListener('click', function (e) {
            if (!movieInput.contains(e.target) && !autocomplete.contains(e.target)) {
                autocomplete.innerHTML = '';
            }
        });
    }

    if (mainForm && submitBtn) {
        mainForm.addEventListener('submit', function () {
            if (btnText) btnText.classList.add('hidden');
            if (btnLoader) {
                btnLoader.classList.remove('hidden');
                btnLoader.textContent = 'Analyzing...';
            }
            submitBtn.disabled = true;
        });
    }

    const moodCards = document.querySelectorAll('.mood-card');
    moodCards.forEach(function (card) {
        card.addEventListener('click', function () {
            moodCards.forEach(function (c) { c.classList.remove('selected'); });
            card.classList.add('selected');
            const color = card.getAttribute('data-color');
            if (color) card.style.setProperty('--mood-color', color);
        });
    });

window.toggleWatchlist = function(btn, title) {
    fetch('/watchlist/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'title=' + encodeURIComponent(title)
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.action === 'added') {
            btn.innerHTML = '💜';
            btn.classList.add('hearted');
            showToast('💜 Added to My List — ' + title);
        } else {
            btn.innerHTML = '🤍';
            btn.classList.remove('hearted');
            showToast('Removed from My List');
        }
        const badge = document.querySelector('.wl-badge');
        if (badge) {
            badge.textContent = data.count;
            badge.style.display = data.count > 0 ? 'inline' : 'none';
        } else if (data.count > 0) {
            const wlLink = document.querySelector('.nav-link[href*="watchlist"]');
            if (wlLink) {
                const newBadge = document.createElement('span');
                newBadge.className = 'wl-badge';
                newBadge.textContent = data.count;
                wlLink.appendChild(newBadge);
            }
        }
    })
    .catch(function() {
        showToast('Something went wrong. Try again.');
    });
};

    window.showToast = function (msg) {
        const toast = document.getElementById('toast');
        if (!toast) return;
        toast.textContent = msg;
        toast.classList.add('show');
        setTimeout(function () { toast.classList.remove('show'); }, 2800);
    };

    const scoreBar = document.querySelectorAll('.score-fill');
    if ('IntersectionObserver' in window) {
        const io = new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
                if (e.isIntersecting) {
                    e.target.style.width = e.target.style.width;
                    io.unobserve(e.target);
                }
            });
        }, { threshold: 0.1 });
        scoreBar.forEach(function (bar) { io.observe(bar); });
    }
})();

// Mood visual feedback
const moodCards = document.querySelectorAll('.mood-card');
const moodDisplay = document.getElementById('moodDisplay');
const moodDisplayText = document.getElementById('moodDisplayText');

moodCards.forEach(function(card) {
    card.addEventListener('click', function() {
        moodCards.forEach(function(c) { c.classList.remove('selected'); });
        card.classList.add('selected');

        const moodName = card.getAttribute('data-mood');
        const radio = card.querySelector('input[type="radio"]');

        if (radio && radio.value === '') {
            if (moodDisplay) moodDisplay.style.display = 'none';
        } else {
            if (moodDisplay) {
                moodDisplay.style.display = 'flex';
                if (moodDisplayText) moodDisplayText.textContent = moodName + ' mood selected';
            }
        }
    });
});

window.searchMovie = function(title) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/recommend';
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'movie_title';
    input.value = title;
    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
};
