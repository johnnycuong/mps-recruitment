// MPS Recruitment - Analytics and Reporting Module
// This file contains the JavaScript code for analytics and reporting features
// It handles KPI tracking, data visualization, and report generation

class MPSAnalytics {
    constructor(options = {}) {
        // Default configuration
        this.config = {
            apiEndpoint: '/api/analytics',
            reportEndpoint: '/api/reports',
            refreshInterval: 3600000, // 1 hour in milliseconds
            ...options
        };
        
        // Analytics state
        this.state = {
            dashboardData: null,
            currentReport: null,
            dateRange: 'month', // 'week', 'month', 'quarter', 'year'
            isLoading: false,
            charts: {}
        };
        
        // Cache for analytics data
        this.cache = {
            dashboardData: {},
            reports: {}
        };
        
        // Initialize event listeners
        this.initEventListeners();
    }
    
    // Initialize event listeners for the analytics interface
    initEventListeners() {
        // Date range selector
        const dateRangeSelector = document.getElementById('analytics-date-range');
        if (dateRangeSelector) {
            dateRangeSelector.addEventListener('change', (e) => {
                this.handleDateRangeChange(e.target.value);
            });
        }
        
        // Report type selector
        const reportTypeSelector = document.getElementById('report-type');
        if (reportTypeSelector) {
            reportTypeSelector.addEventListener('change', (e) => {
                this.handleReportTypeChange(e.target.value);
            });
        }
        
        // Export buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('#export-excel') || e.target.closest('#export-excel')) {
                e.preventDefault();
                this.exportToExcel();
            } else if (e.target.matches('#export-pdf') || e.target.closest('#export-pdf')) {
                e.preventDefault();
                this.exportToPDF();
            }
        });
        
        // Initial load of dashboard data
        this.loadDashboardData();
        
        // Set up periodic refresh
        setInterval(() => {
            this.loadDashboardData(true);
        }, this.config.refreshInterval);
    }
    
    // Handle date range change
    handleDateRangeChange(range) {
        this.state.dateRange = range;
        this.loadDashboardData();
    }
    
    // Handle report type change
    handleReportTypeChange(reportType) {
        this.loadReport(reportType);
    }
    
    // Load dashboard analytics data
    async loadDashboardData(isBackgroundRefresh = false) {
        if (this.state.isLoading && !isBackgroundRefresh) return;
        
        if (!isBackgroundRefresh) {
            this.state.isLoading = true;
            this.showLoadingState();
        }
        
        try {
            // Create cache key from date range
            const cacheKey = this.state.dateRange;
            
            // Check cache first (only if not a background refresh)
            if (!isBackgroundRefresh && this.cache.dashboardData[cacheKey]) {
                this.state.dashboardData = this.cache.dashboardData[cacheKey];
                this.renderDashboard();
                return;
            }
            
            // In a real implementation, this would be an API call
            console.log(`Loading dashboard data for range: ${this.state.dateRange}`);
            
            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 800));
            
            // Mock dashboard data
            const dashboardData = this.getMockDashboardData(this.state.dateRange);
            
            // Cache and update state
            this.cache.dashboardData[cacheKey] = dashboardData;
            this.state.dashboardData = dashboardData;
            
            // Render dashboard (only if not a background refresh)
            if (!isBackgroundRefresh) {
                this.renderDashboard();
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            if (!isBackgroundRefresh) {
                this.showErrorState('Không thể tải dữ liệu bảng điều khiển. Vui lòng thử lại sau.');
            }
        } finally {
            if (!isBackgroundRefresh) {
                this.state.isLoading = false;
                this.hideLoadingState();
            }
        }
    }
    
    // Get mock dashboard data
    getMockDashboardData(dateRange) {
        // Generate different data based on date range
        const multiplier = {
            'week': 1,
            'month': 4,
            'quarter': 12,
            'year': 52
        }[dateRange] || 1;
        
        // Generate time series data for charts
        const generateTimeSeriesData = (baseValues, variance = 0.2) => {
            const points = dateRange === 'week' ? 7 : 
                          dateRange === 'month' ? 30 : 
                          dateRange === 'quarter' ? 90 : 365;
            
            return Array.from({ length: points }, (_, i) => {
                const baseValue = baseValues[i % baseValues.length];
                const randomVariance = baseValue * variance * (Math.random() - 0.5);
                return Math.max(0, Math.round(baseValue + randomVariance));
            });
        };
        
        return {
            summary: {
                newApplications: Math.round(125 * multiplier),
                activeJobs: Math.round(42 * multiplier * 0.5),
                placementRate: Math.round(68 + (Math.random() - 0.5) * 10),
                averageTimeToHire: Math.round(18 - (multiplier - 1) * 2)
            },
            recruitmentFunnel: {
                applications: Math.round(250 * multiplier),
                screenings: Math.round(180 * multiplier),
                interviews: Math.round(120 * multiplier),
                shortlisted: Math.round(60 * multiplier),
                offers: Math.round(40 * multiplier),
                hires: Math.round(32 * multiplier)
            },
            applicationsByDepartment: {
                labels: ['Sản xuất', 'Kỹ thuật', 'IT', 'Hành chính', 'Kinh doanh', 'Tài chính'],
                data: [
                    Math.round(120 * multiplier),
                    Math.round(85 * multiplier),
                    Math.round(65 * multiplier),
                    Math.round(45 * multiplier),
                    Math.round(55 * multiplier),
                    Math.round(30 * multiplier)
                ]
            },
            applicationTrend: {
                labels: this.generateDateLabels(dateRange),
                data: generateTimeSeriesData([25, 28, 32, 30, 35, 40, 38])
            },
            timeToHire: {
                labels: ['Sản xuất', 'Kỹ thuật', 'IT', 'Hành chính', 'Kinh doanh', 'Tài chính'],
                data: [15, 22, 28, 18, 20, 17]
            },
            sourceEffectiveness: {
                labels: ['Website', 'Giới thiệu', 'LinkedIn', 'Đối tác', 'Hội chợ việc làm', 'Khác'],
                applications: [
                    Math.round(80 * multiplier),
                    Math.round(60 * multiplier),
                    Math.round(50 * multiplier),
                    Math.round(40 * multiplier),
                    Math.round(30 * multiplier),
                    Math.round(20 * multiplier)
                ],
                hires: [
                    Math.round(12 * multiplier),
                    Math.round(15 * multiplier),
                    Math.round(8 * multiplier),
                    Math.round(6 * multiplier),
                    Math.round(4 * multiplier),
                    Math.round(2 * multiplier)
                ]
            },
            candidateRetention: {
                labels: ['1 tháng', '2 tháng', '3 tháng', '6 tháng', '1 năm'],
                data: [98, 92, 85, 78, 70]
            }
        };
    }
    
    // Generate date labels based on date range
    generateDateLabels(dateRange) {
        const today = new Date();
        const labels = [];
        
        if (dateRange === 'week') {
            // Last 7 days
            for (let i = 6; i >= 0; i--) {
                const date = new Date(today);
                date.setDate(today.getDate() - i);
                labels.push(date.toLocaleDateString('vi-VN', { weekday: 'short' }));
            }
        } else if (dateRange === 'month') {
            // Last 30 days, grouped by week
            for (let i = 4; i >= 0; i--) {
                const date = new Date(today);
                date.setDate(today.getDate() - (i * 7));
                labels.push(`Tuần ${4-i}`);
            }
        } else if (dateRange === 'quarter') {
            // Last 3 months
            for (let i = 2; i >= 0; i--) {
                const date = new Date(today);
                date.setMonth(today.getMonth() - i);
                labels.push(date.toLocaleDateString('vi-VN', { month: 'short' }));
            }
        } else {
            // Last 12 months
            for (let i = 11; i >= 0; i--) {
                const date = new Date(today);
                date.setMonth(today.getMonth() - i);
                labels.push(date.toLocaleDateString('vi-VN', { month: 'short' }));
            }
        }
        
        return labels;
    }
    
    // Render dashboard with charts and metrics
    renderDashboard() {
        if (!this.state.dashboardData) return;
        
        // Update summary metrics
        this.updateSummaryMetrics();
        
        // Render charts
        this.renderRecruitmentFunnelChart();
        this.renderApplicationsByDepartmentChart();
        this.renderApplicationTrendChart();
        this.renderTimeToHireChart();
        this.renderSourceEffectivenessChart();
        this.renderCandidateRetentionChart();
    }
    
    // Update summary metrics
    updateSummaryMetrics() {
        const { summary } = this.state.dashboardData;
        
        // Update each metric element if it exists
        const updateMetric = (id, value, suffix = '') => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = `${value}${suffix}`;
            }
        };
        
        updateMetric('metric-new-applications', summary.newApplications);
        updateMetric('metric-active-jobs', summary.activeJobs);
        updateMetric('metric-placement-rate', summary.placementRate, '%');
        updateMetric('metric-time-to-hire', summary.averageTimeToHire, ' ngày');
    }
    
    // Render recruitment funnel chart
    renderRecruitmentFunnelChart() {
        const chartCanvas = document.getElementById('chart-recruitment-funnel');
        if (!chartCanvas) return;
        
        const { recruitmentFunnel } = this.state.dashboardData;
        
        // Destroy existing chart if it exists
        if (this.state.charts.recruitmentFunnel) {
            this.state.charts.recruitmentFunnel.destroy();
        }
        
        // Create new chart
        this.state.charts.recruitmentFunnel = new Chart(chartCanvas, {
            type: 'bar',
            data: {
                labels: ['Hồ sơ', 'Sơ vấn', 'Phỏng vấn', 'Shortlist', 'Đề xuất', 'Tuyển dụng'],
                datasets: [{
                    label: 'Số lượng',
                    data: [
                        recruitmentFunnel.applications,
                        recruitmentFunnel.screenings,
                        recruitmentFunnel.interviews,
                        recruitmentFunnel.shortlisted,
                        recruitmentFunnel.offers,
                        recruitmentFunnel.hires
                    ],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(153, 102, 255, 0.8)',
                        'rgba(255, 159, 64, 0.8)',
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(40, 167, 69, 0.8)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(40, 167, 69, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Số lượng'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Phễu Tuyển dụng'
                    },
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Số lượng: ${context.raw}`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Render applications by department chart
    renderApplicationsByDepartmentChart() {
        const chartCanvas = document.getElementById('chart-applications-by-department');
        if (!chartCanvas) return;
        
        const { applicationsByDepartment } = this.state.dashboardData;
        
        // Destroy existing chart if it exists
        if (this.state.charts.applicationsByDepartment) {
            this.state.charts.applicationsByDepartment.destroy();
        }
        
        // Create new chart
        this.state.charts.applicationsByDepartment = new Chart(chartCanvas, {
            type: 'pie',
            data: {
                labels: applicationsByDepartment.labels,
                datasets: [{
                    data: applicationsByDepartment.data,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(153, 102, 255, 0.8)',
                        'rgba(255, 159, 64, 0.8)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Hồ sơ theo Phòng ban'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Render application trend chart
    renderApplicationTrendChart() {
        const chartCanvas = document.getElementById('chart-application-trend');
        if (!chartCanvas) return;
        
        const { applicationTrend } = this.state.dashboardData;
        
        // Destroy existing chart if it exists
        if (this.state.charts.applicationTrend) {
            this.state.charts.applicationTrend.destroy();
        }
        
        // Create new chart
        this.state.charts.applicationTrend = new Chart(chartCanvas, {
            type: 'line',
            data: {
                labels: applicationTrend.labels,
                datasets: [{
                    label: 'Hồ sơ',
                    data: applicationTrend.data,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Số lượng hồ sơ'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Xu hướng Hồ sơ'
                    }
                }
            }
        });
    }
    
    // Render time to hire chart
    renderTimeToHireChart() {
        const chartCanvas = document.getElementById('chart-time-to-hire');
        if (!chartCanvas) return;
        
        const { timeToHire } = this.state.dashboardData;
        
        // Destroy existing chart if it exists
        if (this.state.charts.timeToHire) {
            this.state.charts.timeToHire.destroy();
        }
        
        // Create new chart
        this.state.charts.timeToHire = new Chart(chartCanvas, {
            type: 'bar',
            data: {
                labels: timeToHire.labels,
                datasets: [{
                    label: 'Số ngày',
                    data: timeToHire.data,
                    backgroundColor: 'rgba(75, 192, 192, 0.8)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Số ngày trung bình'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Thời gian Tuyển dụng theo Phòng ban'
                    },
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Render source effectiveness chart
    renderSourceEffectivenessChart() {
        const chartCanvas = document.getElementById('chart-source-effectiveness');
        if (!chartCanvas) return;
        
        const { sourceEffectiveness } = this.state.dashboardData;
        
        // Destroy existing chart if it exists
        if (this.state.charts.sourceEffectiveness) {
            this.state.charts.sourceEffectiveness.destroy();
        }
        
        // Create new chart
        this.state.charts.sourceEffectiveness = new Chart(chartCanvas, {
            type: 'bar',
            data: {
                labels: sourceEffectiveness.labels,
                datasets: [
                    {
                        label: 'Hồ sơ',
                        data: sourceEffectiveness.applications,
                        backgroundColor: 'rgba(54, 162, 235, 0.8)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Tuyển dụng',
                        data: sourceEffectiveness.hires,
                        backgroundColor: 'rgba(40, 167, 69, 0.8)',
                        borderColor: 'rgba(40, 167, 69, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Số lượng'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Hiệu quả Nguồn Tuyển dụng'
                    }
                }
            }
        });
    }
    
    // Render candidate retention chart
    renderCandidateRetentionChart() {
        const chartCanvas = document.getElementById('chart-candidate-retention');
        if (!chartCanvas) return;
        
        const { candidateRetention } = this.state.dashboardData;
        
        // Destroy existing chart if it exists
        if (this.state.charts.candidateRetention) {
            this.state.charts.candidateRetention.destroy();
        }
        
        // Create new chart
        this.state.charts.candidateRetention = new Chart(chartCanvas, {
            type: 'line',
            data: {
                labels: candidateRetention.labels,
                datasets: [{
                    label: 'Tỷ lệ giữ chân (%)',
                    data: candidateRetention.data,
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Tỷ lệ (%)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Tỷ lệ Giữ chân Ứng viên'
                    }
                }
            }
        });
    }
    
    // Load specific report data
    async loadReport(reportType) {
        if (this.state.isLoading) return;
        
        this.state.isLoading = true;
        this.showReportLoadingState();
        
        try {
            // Create cache key from report type and date range
            const cacheKey = `${reportType}-${this.state.dateRange}`;
            
            // Check cache first
            if (this.cache.reports[cacheKey]) {
                this.state.currentReport = this.cache.reports[cacheKey];
                this.renderReport();
                return;
            }
            
            // In a real implementation, this would be an API call
            console.log(`Loading report: ${reportType} for range: ${this.state.dateRange}`);
            
            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Mock report data
            const reportData = this.getMockReportData(reportType);
            
            // Cache and update state
            this.cache.reports[cacheKey] = reportData;
            this.state.currentReport = reportData;
            
            // Render report
            this.renderReport();
        } catch (error) {
            console.error('Error loading report:', error);
            this.showErrorState('Không thể tải báo cáo. Vui lòng thử lại sau.');
        } finally {
            this.state.isLoading = false;
            this.hideReportLoadingState();
        }
    }
    
    // Get mock report data
    getMockReportData(reportType) {
        // Generate different data based on report type
        switch (reportType) {
            case 'recruiter-performance':
                return {
                    title: 'Báo cáo Hiệu suất Tuyển dụng',
                    headers: ['Tuyển dụng viên', 'Hồ sơ xử lý', 'Phỏng vấn', 'Đề xuất', 'Tuyển dụng', 'Thời gian TB (ngày)', 'Tỷ lệ chuyển đổi (%)'],
                    data: [
                        ['Nguyễn Văn A', 120, 45, 20, 15, 18, 12.5],
                        ['Trần Thị B', 95, 40, 18, 12, 15, 12.6],
                        ['Lê Văn C', 110, 50, 22, 18, 16, 16.4],
                        ['Phạm Thị D', 85, 35, 15, 10, 20, 11.8],
                        ['Hoàng Văn E', 100, 42, 19, 14, 17, 14.0]
                    ]
                };
                
            case 'department-hiring':
                return {
                    title: 'Báo cáo Tuyển dụng theo Phòng ban',
                    headers: ['Phòng ban', 'Vị trí mở', 'Hồ sơ nhận', 'Phỏng vấn', 'Đề xuất', 'Tuyển dụng', 'Tỷ lệ lấp đầy (%)'],
                    data: [
                        ['Sản xuất', 15, 180, 60, 25, 12, 80],
                        ['Kỹ thuật', 10, 120, 45, 20, 8, 80],
                        ['IT', 8, 95, 40, 18, 7, 87.5],
                        ['Hành chính', 5, 70, 30, 12, 5, 100],
                        ['Kinh doanh', 12, 150, 55, 22, 10, 83.3],
                        ['Tài chính', 6, 80, 35, 15, 6, 100]
                    ]
                };
                
            case 'source-analysis':
                return {
                    title: 'Báo cáo Phân tích Nguồn Tuyển dụng',
                    headers: ['Nguồn', 'Hồ sơ', 'Phỏng vấn', 'Tuyển dụng', 'Chi phí (triệu VND)', 'Chi phí/Tuyển dụng', 'Tỷ lệ chuyển đổi (%)'],
                    data: [
                        ['Website', 120, 45, 12, 5, 0.42, 10],
                        ['Giới thiệu', 85, 40, 15, 2, 0.13, 17.6],
                        ['LinkedIn', 95, 38, 8, 8, 1, 8.4],
                        ['Đối tác', 75, 30, 6, 10, 1.67, 8],
                        ['Hội chợ việc làm', 60, 25, 4, 15, 3.75, 6.7],
                        ['Khác', 40, 15, 2, 1, 0.5, 5]
                    ]
                };
                
            case 'candidate-quality':
                return {
                    title: 'Báo cáo Chất lượng Ứng viên',
                    headers: ['Nguồn', 'Số lượng', 'Đạt yêu cầu (%)', 'Kỹ năng phù hợp (%)', 'Kinh nghiệm phù hợp (%)', 'Văn hóa phù hợp (%)', 'Điểm TB (1-10)'],
                    data: [
                        ['Website', 120, 65, 70, 60, 75, 7.2],
                        ['Giới thiệu', 85, 80, 85, 75, 90, 8.5],
                        ['LinkedIn', 95, 75, 80, 70, 65, 7.8],
                        ['Đối tác', 75, 70, 75, 65, 70, 7.5],
                        ['Hội chợ việc làm', 60, 60, 65, 55, 60, 6.8],
                        ['Khác', 40, 50, 55, 45, 50, 6.2]
                    ]
                };
                
            case 'retention-analysis':
                return {
                    title: 'Báo cáo Phân tích Giữ chân Nhân viên',
                    headers: ['Phòng ban', 'Tuyển dụng', '1 tháng (%)', '2 tháng (%)', '3 tháng (%)', '6 tháng (%)', '1 năm (%)'],
                    data: [
                        ['Sản xuất', 12, 100, 92, 83, 75, 67],
                        ['Kỹ thuật', 8, 100, 100, 88, 75, 63],
                        ['IT', 7, 100, 86, 86, 71, 57],
                        ['Hành chính', 5, 100, 100, 100, 80, 80],
                        ['Kinh doanh', 10, 100, 90, 80, 70, 60],
                        ['Tài chính', 6, 100, 100, 83, 83, 67]
                    ]
                };
                
            default:
                return {
                    title: 'Báo cáo Tổng hợp',
                    headers: ['Chỉ số', 'Giá trị', 'So với kỳ trước', 'Xu hướng'],
                    data: [
                        ['Tổng số hồ sơ', 475, '+12%', 'Tăng'],
                        ['Tỷ lệ phỏng vấn', '49%', '+5%', 'Tăng'],
                        ['Tỷ lệ đề xuất', '21%', '-2%', 'Giảm'],
                        ['Tỷ lệ tuyển dụng', '10%', '+1%', 'Tăng'],
                        ['Thời gian tuyển dụng TB', '18 ngày', '-3 ngày', 'Cải thiện'],
                        ['Chi phí tuyển dụng TB', '2.5 triệu', '-8%', 'Cải thiện']
                    ]
                };
        }
    }
    
    // Render report data as table
    renderReport() {
        if (!this.state.currentReport) return;
        
        const reportContainer = document.getElementById('report-container');
        if (!reportContainer) return;
        
        const { title, headers, data } = this.state.currentReport;
        
        // Update report title
        const reportTitle = document.getElementById('report-title');
        if (reportTitle) {
            reportTitle.textContent = title;
        }
        
        // Create table
        let tableHTML = `
            <table class="table table-striped table-hover">
                <thead class="table-primary">
                    <tr>
        `;
        
        // Add headers
        headers.forEach(header => {
            tableHTML += `<th>${header}</th>`;
        });
        
        tableHTML += `
                    </tr>
                </thead>
                <tbody>
        `;
        
        // Add data rows
        data.forEach(row => {
            tableHTML += '<tr>';
            row.forEach((cell, index) => {
                // Format numbers and percentages
                let formattedCell = cell;
                if (typeof cell === 'number') {
                    if (headers[index].includes('%')) {
                        formattedCell = `${cell}%`;
                    } else if (headers[index].includes('Chi phí')) {
                        formattedCell = `${cell.toLocaleString('vi-VN')}`;
                    }
                }
                tableHTML += `<td>${formattedCell}</td>`;
            });
            tableHTML += '</tr>';
        });
        
        tableHTML += `
                </tbody>
            </table>
        `;
        
        reportContainer.innerHTML = tableHTML;
    }
    
    // Export current report to Excel
    exportToExcel() {
        if (!this.state.currentReport) {
            alert('Không có dữ liệu báo cáo để xuất.');
            return;
        }
        
        try {
            const { title, headers, data } = this.state.currentReport;
            
            // In a real implementation, this would call an API endpoint to generate Excel
            console.log(`Exporting report "${title}" to Excel`);
            
            // For demo purposes, we'll simulate the export
            alert(`Đang xuất báo cáo "${title}" sang Excel. Trong môi trường thực tế, file Excel sẽ được tải xuống.`);
            
            // The actual implementation would use a library like SheetJS or call a backend endpoint
        } catch (error) {
            console.error('Error exporting to Excel:', error);
            alert('Có lỗi khi xuất báo cáo sang Excel. Vui lòng thử lại sau.');
        }
    }
    
    // Export current report to PDF
    exportToPDF() {
        if (!this.state.currentReport) {
            alert('Không có dữ liệu báo cáo để xuất.');
            return;
        }
        
        try {
            const { title, headers, data } = this.state.currentReport;
            
            // In a real implementation, this would call an API endpoint to generate PDF
            console.log(`Exporting report "${title}" to PDF`);
            
            // For demo purposes, we'll simulate the export
            alert(`Đang xuất báo cáo "${title}" sang PDF. Trong môi trường thực tế, file PDF sẽ được tải xuống.`);
            
            // The actual implementation would use a library like jsPDF or call a backend endpoint
        } catch (error) {
            console.error('Error exporting to PDF:', error);
            alert('Có lỗi khi xuất báo cáo sang PDF. Vui lòng thử lại sau.');
        }
    }
    
    // Show loading state for dashboard
    showLoadingState() {
        const dashboardContainer = document.getElementById('analytics-dashboard');
        if (!dashboardContainer) return;
        
        // Add loading overlay
        const loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'analytics-loading-overlay';
        loadingOverlay.className = 'd-flex justify-content-center align-items-center';
        loadingOverlay.style.position = 'absolute';
        loadingOverlay.style.top = '0';
        loadingOverlay.style.left = '0';
        loadingOverlay.style.width = '100%';
        loadingOverlay.style.height = '100%';
        loadingOverlay.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
        loadingOverlay.style.zIndex = '1000';
        
        loadingOverlay.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Đang tải...</span>
                </div>
                <p class="mt-2">Đang tải dữ liệu phân tích...</p>
            </div>
        `;
        
        dashboardContainer.style.position = 'relative';
        dashboardContainer.appendChild(loadingOverlay);
    }
    
    // Hide loading state for dashboard
    hideLoadingState() {
        const loadingOverlay = document.getElementById('analytics-loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.remove();
        }
    }
    
    // Show loading state for report
    showReportLoadingState() {
        const reportContainer = document.getElementById('report-container');
        if (!reportContainer) return;
        
        reportContainer.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Đang tải...</span>
                </div>
                <p class="mt-2">Đang tải báo cáo...</p>
            </div>
        `;
    }
    
    // Hide loading state for report
    hideReportLoadingState() {
        // The loading state is replaced by the rendered report
    }
    
    // Show error state
    showErrorState(message) {
        const errorAlert = document.createElement('div');
        errorAlert.className = 'alert alert-danger';
        errorAlert.textContent = message;
        
        // Find container to show error
        const container = document.getElementById('analytics-dashboard') || 
                         document.getElementById('report-container');
        
        if (container) {
            container.prepend(errorAlert);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                errorAlert.remove();
            }, 5000);
        }
    }
}

// Initialize analytics when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const analyticsInstance = new MPSAnalytics();
    
    // Make instance available globally for debugging
    window.mpsAnalytics = analyticsInstance;
});
