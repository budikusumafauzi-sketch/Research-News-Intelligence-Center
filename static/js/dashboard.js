document.addEventListener('DOMContentLoaded', () => {
    // Determine context for the Chart
    const ctxElement = document.getElementById('trendingChart');

    if (ctxElement) {
        const ctx = ctxElement.getContext('2d');

        // Setup Chart.js global defaults for Light Theme
        Chart.defaults.color = '#6B7280';
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.font.size = 11;

        // Create Gradient for the primary line
        const gradientPrimary = ctx.createLinearGradient(0, 0, 0, 300);
        gradientPrimary.addColorStop(0, 'rgba(220, 38, 38, 0.4)');
        gradientPrimary.addColorStop(1, 'rgba(220, 38, 38, 0.0)');

        // Create Gradient for the secondary line
        const gradientSecondary = ctx.createLinearGradient(0, 0, 0, 300);
        gradientSecondary.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
        gradientSecondary.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

        const trendingChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Today'],
                datasets: [
                    {
                        label: 'Artificial Intelligence',
                        data: [120, 150, 180, 170, 210, 240, 290],
                        borderColor: '#DC2626',
                        backgroundColor: gradientPrimary,
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#FFFFFF',
                        pointBorderColor: '#DC2626',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Quantum Computing',
                        data: [40, 50, 45, 60, 55, 80, 110],
                        borderColor: '#3B82F6',
                        backgroundColor: gradientSecondary,
                        borderWidth: 2,
                        borderDash: [5, 5],
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        align: 'end',
                        labels: {
                            usePointStyle: true,
                            boxWidth: 8,
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: '#FFFFFF',
                        titleColor: '#1F2937',
                        bodyColor: '#6B7280',
                        borderColor: '#E5E7EB',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: true,
                        usePointStyle: true,
                        cornerRadius: 8,
                        titleFont: { size: 13, weight: '600' },
                        bodyFont: { size: 12 }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#E5E7EB',
                            drawBorder: false,
                            borderDash: [4, 4]
                        },
                        border: { display: false }
                    },
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        border: { display: false }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index',
                },
            }
        });
        window.trendingChartInstance = trendingChart;
    }
});

// Phase 5.1 - Semi-Realtime Auto Refresh Logic
document.addEventListener('DOMContentLoaded', () => {
    let knownIntelligenceIds = new Set();

    // Initialize the set with currently displayed intelligence items
    document.querySelectorAll('#intelligenceFeed .insight-card').forEach(card => {
        if (card.dataset.id) {
            knownIntelligenceIds.add(card.dataset.id);
        }
    });

    function showNotification(message) {
        const container = document.getElementById('notificationContainer');
        if (!container) return;

        const banner = document.createElement('div');
        banner.className = 'notification-banner';
        banner.innerHTML = `<i class="bi bi-info-circle text-primary"></i> <span>${message}</span>`;
        container.appendChild(banner);

        // Remove from DOM after animation completes (5 seconds)
        setTimeout(() => {
            if (banner.parentNode) {
                banner.parentNode.removeChild(banner);
            }
        }, 5000);
    }

    function formatTime(date) {
        const h = String(date.getHours()).padStart(2, '0');
        const m = String(date.getMinutes()).padStart(2, '0');
        const s = String(date.getSeconds()).padStart(2, '0');
        return `${h}:${m}:${s}`;
    }

    async function refreshDashboard() {
        try {
            const [newsRes, intelRes] = await Promise.all([
                fetch('/news'),
                fetch('/intelligence/latest')
            ]);

            if (newsRes.ok && intelRes.ok) {
                const newsData = await newsRes.json();
                const intelData = await intelRes.json();

                updateNewsFeed(newsData.slice(0, 6));
                const newCount = updateIntelligenceFeed(intelData.slice(0, 4));

                if (newCount > 0) {
                    showNotification(`${newCount} new intelligence items detected`);
                    console.log('INFO: New intelligence items detected.');
                }

                const indicator = document.getElementById('lastUpdatedIndicator');
                if (indicator) {
                    indicator.innerHTML = `<i class="bi bi-clock-history"></i> Last updated: ${formatTime(new Date())}`;
                }

                console.log('INFO: Dashboard auto-refresh completed.');
            } else {
                console.warn('WARNING: Dashboard refresh failed (non-200 response).');
            }
            
            // Also refresh analytics
            await refreshAnalytics();
        } catch (error) {
            console.warn('WARNING: Dashboard refresh failed.', error);
        }
    }

    async function refreshAnalytics() {
        try {
            const [trendsRes, momentumRes, emergingRes] = await Promise.all([
                fetch('/analytics/trends').catch(() => null),
                fetch('/analytics/momentum').catch(() => null),
                fetch('/analytics/emerging').catch(() => null)
            ]);
            
            if (trendsRes && trendsRes.ok) {
                const data = await trendsRes.json();
                updateTrendsChart(data.trends || []);
            }
            if (momentumRes && momentumRes.ok) {
                const data = await momentumRes.json();
                updateMomentumList(data.momentum || []);
            }
            if (emergingRes && emergingRes.ok) {
                const data = await emergingRes.json();
                updateEmergingList(data.technologies || []);
            }
        } catch (e) {
            console.warn('WARNING: Failed to refresh analytics.', e);
        }
    }

    function updateTrendsChart(trends) {
        if (!window.trendingChartInstance || trends.length === 0) return;
        
        // Update the chart with new labels and data
        const labels = trends.slice(0, 7).map(t => t.topic.length > 15 ? t.topic.substring(0, 15) + '...' : t.topic);
        const data = trends.slice(0, 7).map(t => t.score);
        
        window.trendingChartInstance.data.labels = labels;
        window.trendingChartInstance.data.datasets[0].data = data;
        window.trendingChartInstance.data.datasets[0].label = 'Top Trends Velocity';
        
        // Hide secondary dataset as we are now plotting top trends dynamically
        if(window.trendingChartInstance.data.datasets.length > 1) {
            window.trendingChartInstance.data.datasets[1].hidden = true;
        }
        
        window.trendingChartInstance.update();
    }

    function updateMomentumList(momentumData) {
        const container = document.getElementById('momentumList');
        if (!container) return;

        if (momentumData.length === 0) {
            container.innerHTML = `
                <div class="p-4 text-center text-muted">
                    <i class="bi bi-rocket fs-2 mb-2 d-block"></i>
                    <p class="mb-0 small">No momentum data yet.</p>
                    <p class="small">Will populate after analytics engine runs.</p>
                </div>
            `;
            return;
        }

        let html = '';
        momentumData.slice(0, 5).forEach((item, index) => {
            const icon = item.direction === 'up' ? '<i class="bi bi-graph-up-arrow text-success"></i>' : 
                         item.direction === 'down' ? '<i class="bi bi-graph-down-arrow text-danger"></i>' : 
                         '<i class="bi bi-dash text-muted"></i>';
            html += `
            <div class="feed-item align-items-center">
                <div class="feed-icon" style="background: rgba(0,0,0,0.05); color: #1F2937; font-weight: bold; font-size: 0.8rem;">#${index+1}</div>
                <div class="feed-content d-flex justify-content-between w-100">
                    <div>
                        <h6 class="mb-0 text-dark">${item.entity}</h6>
                        <div class="feed-meta">Score: ${item.momentum_score}</div>
                    </div>
                    <div class="fs-5">${icon}</div>
                </div>
            </div>
            `;
        });
        container.innerHTML = html;
    }

    function updateEmergingList(techData) {
        const container = document.getElementById('emergingTechList');
        if (!container) return;

        if (techData.length === 0) {
            container.innerHTML = `
                <div class="p-4 text-center text-muted">
                    <i class="bi bi-cpu fs-2 mb-2 d-block"></i>
                    <p class="mb-0 small">No emerging tech detected.</p>
                    <p class="small">Will populate after analytics engine runs.</p>
                </div>
            `;
            return;
        }

        let html = '';
        techData.slice(0, 5).forEach((item) => {
            html += `
            <div class="feed-item align-items-center">
                <div class="feed-icon news"><i class="bi bi-lightning-charge-fill text-warning"></i></div>
                <div class="feed-content d-flex justify-content-between w-100">
                    <div>
                        <h6 class="mb-0 text-dark">${item.technology}</h6>
                        <div class="feed-meta">Mentions: ${item.recent_mentions}</div>
                    </div>
                    <div>
                        <span class="badge bg-primary bg-opacity-25 text-primary border border-primary border-opacity-50">${item.ratio}x Growth</span>
                    </div>
                </div>
            </div>
            `;
        });
        container.innerHTML = html;
    }

    function updateIntelligenceFeed(intelData) {
        const feedContainer = document.getElementById('intelligenceFeed');
        if (!feedContainer) return 0;

        let newCount = 0;
        let html = '';

        if (intelData.length === 0) {
            html = `
                <div class="text-center text-muted py-3">
                    <i class="bi bi-cpu fs-3 mb-2 d-block"></i>
                    <p class="small mb-0">Intelligence engine warming up.</p>
                    <p class="small">Insights will appear after first data sync.</p>
                </div>
            `;
        } else {
            intelData.forEach(intel => {
                if (!knownIntelligenceIds.has(intel.id)) {
                    newCount++;
                    knownIntelligenceIds.add(intel.id);
                }

                let summary = intel.summary || 'No summary available.';
                if (summary.length > 100) summary = summary.substring(0, 100) + '...';

                let topicsHtml = (intel.topics || []).slice(0, 3).map(t => `<span class="tag">${t}</span>`).join('');
                let typeTag = intel.content_type === 'news'
                    ? `<span class="tag sentiment-pos">News</span>`
                    : `<span class="tag sentiment-neu">Research</span>`;

                html += `
                <div class="insight-card" data-id="${intel.id}">
                    <div class="d-flex justify-content-between align-items-start mb-1">
                        <h6 class="mb-0" style="font-size:0.85rem; line-height:1.4;">${summary}</h6>
                        <span class="ms-2" style="font-size:0.65rem; color:var(--text-muted); white-space:nowrap;">${Math.round(intel.confidence_score)}%</span>
                    </div>
                    <div class="insight-tags mt-2">
                        ${topicsHtml}
                        ${typeTag}
                    </div>
                </div>
                `;
            });
        }

        feedContainer.innerHTML = html;
        return newCount;
    }

    function updateNewsFeed(newsData) {
        const feedContainer = document.getElementById('newsFeedList');
        if (!feedContainer) return;

        let html = '';
        if (newsData.length === 0) {
            html = `
                <div class="p-4 text-center text-muted">
                    <i class="bi bi-inbox fs-2 mb-2 d-block"></i>
                    <p class="mb-0 small">No intelligence gathered yet.</p>
                    <p class="small">The background worker will sync shortly.</p>
                </div>
            `;
        } else {
            newsData.forEach(item => {
                let dateStr = 'Just now';
                if (item.published_at) {
                    const d = new Date(item.published_at);
                    dateStr = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0') + ' ' + String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
                }
                const sourceName = item.source || 'Unknown Source';

                html += `
                <div class="feed-item">
                    <div class="feed-icon news"><i class="bi bi-newspaper"></i></div>
                    <div class="feed-content">
                        <h6><a href="${item.original_url}" target="_blank" class="feed-title text-decoration-none">${item.title}</a></h6>
                        <div class="feed-meta">${sourceName} • ${dateStr}</div>
                    </div>
                </div>
                `;
            });
        }

        feedContainer.innerHTML = html;
    }

    // Refresh every 60 seconds
    setInterval(refreshDashboard, 60000);
    
    // Initial fetch for analytics
    setTimeout(refreshAnalytics, 1500);
});
