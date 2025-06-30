// MPS Recruitment - Advanced Search Component
// This file contains the JavaScript code for the advanced search functionality
// It handles dynamic filtering, suggestion algorithms, and search result rendering

class MPSAdvancedSearch {
    constructor(options = {}) {
        // Default configuration
        this.config = {
            apiEndpoint: '/api/search',
            suggestionsEndpoint: '/api/suggestions',
            searchDelay: 500,
            minQueryLength: 2,
            maxSuggestions: 5,
            ...options
        };
        
        // Search state
        this.state = {
            lastQuery: '',
            searchTimeout: null,
            isSearching: false,
            filters: {},
            sortBy: 'relevance',
            page: 1,
            resultsPerPage: 10
        };
        
        // Cache for suggestions and previous results
        this.cache = {
            suggestions: {},
            searchResults: {}
        };
        
        // Initialize event listeners
        this.initEventListeners();
    }
    
    // Initialize event listeners for search inputs and filters
    initEventListeners() {
        // Main search input
        const searchInput = document.getElementById('keyword');
        if (searchInput) {
            searchInput.addEventListener('input', this.handleSearchInput.bind(this));
            searchInput.addEventListener('focus', this.showSuggestions.bind(this));
            searchInput.addEventListener('blur', () => {
                // Delay hiding suggestions to allow for clicks
                setTimeout(() => this.hideSuggestions(), 200);
            });
        }
        
        // Search form submission
        const searchForm = document.getElementById('job-search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', this.handleSearchSubmit.bind(this));
        }
        
        // Filter checkboxes
        const filterCheckboxes = document.querySelectorAll('.filter-card input[type="checkbox"]');
        filterCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', this.handleFilterChange.bind(this));
        });
        
        // Sort dropdown
        const sortSelect = document.querySelector('select[name="sort"]');
        if (sortSelect) {
            sortSelect.addEventListener('change', this.handleSortChange.bind(this));
        }
        
        // Pagination
        document.addEventListener('click', (e) => {
            if (e.target.matches('.page-link') || e.target.closest('.page-link')) {
                e.preventDefault();
                const pageLink = e.target.matches('.page-link') ? e.target : e.target.closest('.page-link');
                const page = pageLink.dataset.page;
                if (page) {
                    this.handlePageChange(parseInt(page));
                }
            }
        });
    }
    
    // Handle input in the search box
    handleSearchInput(e) {
        const query = e.target.value.trim();
        
        // Clear previous timeout
        if (this.state.searchTimeout) {
            clearTimeout(this.state.searchTimeout);
        }
        
        // Update state
        this.state.lastQuery = query;
        
        // If query is too short, hide suggestions
        if (query.length < this.config.minQueryLength) {
            this.hideSuggestions();
            return;
        }
        
        // Set timeout for suggestions
        this.state.searchTimeout = setTimeout(() => {
            this.fetchSuggestions(query);
        }, this.config.searchDelay);
    }
    
    // Handle search form submission
    handleSearchSubmit(e) {
        e.preventDefault();
        
        // Get form values
        const keyword = document.getElementById('keyword').value.trim();
        const location = document.getElementById('location').value;
        const category = document.getElementById('category').value;
        
        // Update filters
        this.state.filters = {
            keyword,
            location,
            category,
            ...this.collectCheckboxFilters()
        };
        
        // Reset pagination
        this.state.page = 1;
        
        // Perform search
        this.performSearch();
    }
    
    // Handle filter checkbox changes
    handleFilterChange(e) {
        // Update filters with all checkbox states
        this.state.filters = {
            ...this.state.filters,
            ...this.collectCheckboxFilters()
        };
        
        // Reset pagination
        this.state.page = 1;
        
        // Perform search with delay
        if (this.state.searchTimeout) {
            clearTimeout(this.state.searchTimeout);
        }
        
        this.state.searchTimeout = setTimeout(() => {
            this.performSearch();
        }, this.config.searchDelay);
    }
    
    // Handle sort dropdown changes
    handleSortChange(e) {
        this.state.sortBy = e.target.value;
        this.performSearch();
    }
    
    // Handle pagination clicks
    handlePageChange(page) {
        this.state.page = page;
        this.performSearch();
        
        // Scroll to top of results
        const resultsContainer = document.querySelector('.jobs-list');
        if (resultsContainer) {
            resultsContainer.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    // Collect all checkbox filter values
    collectCheckboxFilters() {
        const filters = {};
        const filterGroups = {
            level: ['level-entry', 'level-junior', 'level-senior', 'level-manager', 'level-director'],
            type: ['type-fulltime', 'type-parttime', 'type-contract', 'type-temporary'],
            experience: ['exp-none', 'exp-1', 'exp-1-3', 'exp-3-5', 'exp-5-plus'],
            salary: ['salary-negotiable', 'salary-under-10', 'salary-10-20', 'salary-20-30', 'salary-30-plus']
        };
        
        // For each filter group
        Object.entries(filterGroups).forEach(([group, ids]) => {
            const selectedValues = ids
                .map(id => {
                    const checkbox = document.getElementById(id);
                    return checkbox && checkbox.checked ? id.split('-').pop() : null;
                })
                .filter(Boolean);
            
            if (selectedValues.length > 0) {
                filters[group] = selectedValues;
            }
        });
        
        return filters;
    }
    
    // Fetch search suggestions
    async fetchSuggestions(query) {
        // Check cache first
        if (this.cache.suggestions[query]) {
            this.renderSuggestions(this.cache.suggestions[query]);
            return;
        }
        
        try {
            // In a real implementation, this would be an API call
            // For demo purposes, we'll simulate it
            console.log(`Fetching suggestions for: ${query}`);
            
            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 300));
            
            // Mock suggestions based on query
            const suggestions = this.getMockSuggestions(query);
            
            // Cache suggestions
            this.cache.suggestions[query] = suggestions;
            
            // Render suggestions
            this.renderSuggestions(suggestions);
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    }
    
    // Get mock suggestions (in a real implementation, this would come from the API)
    getMockSuggestions(query) {
        query = query.toLowerCase();
        
        const allSuggestions = [
            { type: 'position', text: 'Kỹ sư Điện tử', count: 12 },
            { type: 'position', text: 'Kỹ sư Phần mềm', count: 8 },
            { type: 'position', text: 'Kỹ thuật viên Bảo trì', count: 5 },
            { type: 'position', text: 'Kỹ sư Cơ khí', count: 7 },
            { type: 'position', text: 'Kỹ sư Tự động hóa', count: 4 },
            { type: 'company', text: 'Samsung Electronics', count: 15 },
            { type: 'company', text: 'LG Display', count: 9 },
            { type: 'company', text: 'Intel Vietnam', count: 6 },
            { type: 'company', text: 'Foxconn', count: 11 },
            { type: 'skill', text: 'Kỹ năng lập trình', count: 22 },
            { type: 'skill', text: 'Kỹ năng quản lý', count: 18 },
            { type: 'skill', text: 'Kỹ năng giao tiếp', count: 30 },
            { type: 'location', text: 'Khu công nghiệp Bắc Ninh', count: 14 },
            { type: 'location', text: 'Khu công nghiệp Bình Dương', count: 16 }
        ];
        
        // Filter suggestions based on query
        return allSuggestions
            .filter(suggestion => suggestion.text.toLowerCase().includes(query))
            .slice(0, this.config.maxSuggestions);
    }
    
    // Render suggestions dropdown
    renderSuggestions(suggestions) {
        // Find or create suggestions container
        let suggestionsContainer = document.getElementById('search-suggestions');
        if (!suggestionsContainer) {
            suggestionsContainer = document.createElement('div');
            suggestionsContainer.id = 'search-suggestions';
            suggestionsContainer.className = 'search-suggestions';
            
            // Style the suggestions container
            Object.assign(suggestionsContainer.style, {
                position: 'absolute',
                zIndex: '1000',
                backgroundColor: 'white',
                width: '100%',
                maxHeight: '300px',
                overflowY: 'auto',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                borderRadius: '0 0 4px 4px',
                border: '1px solid #ddd',
                borderTop: 'none'
            });
            
            // Insert after search input
            const searchInput = document.getElementById('keyword');
            searchInput.parentNode.style.position = 'relative';
            searchInput.parentNode.appendChild(suggestionsContainer);
        }
        
        // Clear previous suggestions
        suggestionsContainer.innerHTML = '';
        
        // If no suggestions, hide container
        if (suggestions.length === 0) {
            suggestionsContainer.style.display = 'none';
            return;
        }
        
        // Group suggestions by type
        const groupedSuggestions = suggestions.reduce((groups, suggestion) => {
            if (!groups[suggestion.type]) {
                groups[suggestion.type] = [];
            }
            groups[suggestion.type].push(suggestion);
            return groups;
        }, {});
        
        // Create suggestion elements
        Object.entries(groupedSuggestions).forEach(([type, items]) => {
            // Add group header
            const groupHeader = document.createElement('div');
            groupHeader.className = 'suggestion-group-header';
            groupHeader.textContent = this.getGroupTitle(type);
            Object.assign(groupHeader.style, {
                padding: '8px 12px',
                fontWeight: 'bold',
                backgroundColor: '#f8f9fa',
                fontSize: '0.8rem',
                color: '#6c757d',
                textTransform: 'uppercase'
            });
            suggestionsContainer.appendChild(groupHeader);
            
            // Add group items
            items.forEach(suggestion => {
                const item = document.createElement('div');
                item.className = 'suggestion-item';
                item.innerHTML = `
                    <span>${this.highlightQuery(suggestion.text, this.state.lastQuery)}</span>
                    <span class="suggestion-count">${suggestion.count}</span>
                `;
                Object.assign(item.style, {
                    padding: '10px 12px',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                });
                
                // Add hover effect
                item.addEventListener('mouseenter', () => {
                    item.style.backgroundColor = '#f0f0f0';
                });
                item.addEventListener('mouseleave', () => {
                    item.style.backgroundColor = 'transparent';
                });
                
                // Add click handler
                item.addEventListener('click', () => {
                    document.getElementById('keyword').value = suggestion.text;
                    this.hideSuggestions();
                    this.handleSearchSubmit(new Event('submit'));
                });
                
                suggestionsContainer.appendChild(item);
            });
        });
        
        // Show suggestions container
        suggestionsContainer.style.display = 'block';
    }
    
    // Get title for suggestion group
    getGroupTitle(type) {
        const titles = {
            position: 'Vị trí',
            company: 'Công ty',
            skill: 'Kỹ năng',
            location: 'Địa điểm'
        };
        return titles[type] || type;
    }
    
    // Highlight query in suggestion text
    highlightQuery(text, query) {
        if (!query) return text;
        
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<strong>$1</strong>');
    }
    
    // Show suggestions dropdown
    showSuggestions() {
        const suggestionsContainer = document.getElementById('search-suggestions');
        if (suggestionsContainer && this.state.lastQuery.length >= this.config.minQueryLength) {
            suggestionsContainer.style.display = 'block';
        }
    }
    
    // Hide suggestions dropdown
    hideSuggestions() {
        const suggestionsContainer = document.getElementById('search-suggestions');
        if (suggestionsContainer) {
            suggestionsContainer.style.display = 'none';
        }
    }
    
    // Perform search with current filters and sort
    async performSearch() {
        if (this.state.isSearching) return;
        
        this.state.isSearching = true;
        
        try {
            // Show loading state
            this.showLoadingState();
            
            // Create cache key from search parameters
            const cacheKey = JSON.stringify({
                filters: this.state.filters,
                sortBy: this.state.sortBy,
                page: this.state.page
            });
            
            // Check cache first
            if (this.cache.searchResults[cacheKey]) {
                this.renderSearchResults(this.cache.searchResults[cacheKey]);
                this.hideLoadingState();
                this.state.isSearching = false;
                return;
            }
            
            // In a real implementation, this would be an API call
            // For demo purposes, we'll simulate it
            console.log('Performing search with:', {
                filters: this.state.filters,
                sortBy: this.state.sortBy,
                page: this.state.page,
                resultsPerPage: this.state.resultsPerPage
            });
            
            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 800));
            
            // Mock search results
            const results = this.getMockSearchResults();
            
            // Cache results
            this.cache.searchResults[cacheKey] = results;
            
            // Render results
            this.renderSearchResults(results);
        } catch (error) {
            console.error('Error performing search:', error);
            this.showErrorState('Có lỗi xảy ra khi tìm kiếm. Vui lòng thử lại sau.');
        } finally {
            this.hideLoadingState();
            this.state.isSearching = false;
        }
    }
    
    // Get mock search results (in a real implementation, this would come from the API)
    getMockSearchResults() {
        // In a real implementation, this would filter based on this.state.filters
        const totalResults = 56;
        const totalPages = Math.ceil(totalResults / this.state.resultsPerPage);
        
        // Generate mock job listings
        const jobs = [
            {
                id: 1,
                title: 'Kỹ sư Điện tử',
                company: 'ABC Electronics Vietnam',
                location: 'Bắc Ninh',
                salary: '20 - 25 triệu',
                type: 'Toàn thời gian',
                tags: ['Điện tử', 'Kỹ thuật', 'Sản xuất'],
                logo: '/assets/company-logo-1.png',
                posted_days_ago: 2
            },
            {
                id: 2,
                title: 'Quản lý Sản xuất',
                company: 'XYZ Manufacturing Co., Ltd',
                location: 'Bình Dương',
                salary: '30 - 35 triệu',
                type: 'Toàn thời gian',
                tags: ['Sản xuất', 'Quản lý', 'Cấp cao'],
                logo: '/assets/company-logo-2.png',
                posted_days_ago: 7
            },
            {
                id: 3,
                title: 'Kỹ thuật viên Bảo trì',
                company: 'DEF Industries Vietnam',
                location: 'Hà Nội',
                salary: '15 - 18 triệu',
                type: 'Toàn thời gian',
                tags: ['Kỹ thuật', 'Bảo trì', 'Sản xuất'],
                logo: '/assets/company-logo-3.png',
                posted_days_ago: 0
            },
            {
                id: 4,
                title: 'Chuyên viên Nhân sự',
                company: 'GHI Technology Co., Ltd',
                location: 'TP. Hồ Chí Minh',
                salary: '18 - 22 triệu',
                type: 'Toàn thời gian',
                tags: ['Nhân sự', 'Tuyển dụng', 'Hành chính'],
                logo: '/assets/company-logo-4.png',
                posted_days_ago: 3
            },
            {
                id: 5,
                title: 'Kỹ sư Phần mềm',
                company: 'JKL Software Vietnam',
                location: 'Đà Nẵng',
                salary: '25 - 30 triệu',
                type: 'Toàn thời gian',
                tags: ['IT', 'Phần mềm', 'Lập trình'],
                logo: '/assets/company-logo-5.png',
                posted_days_ago: 5
            }
        ];
        
        // Apply sorting
        if (this.state.sortBy === 'date') {
            jobs.sort((a, b) => a.posted_days_ago - b.posted_days_ago);
        } else if (this.state.sortBy === 'salary-high') {
            jobs.sort((a, b) => {
                const aAvg = this.getAverageSalary(a.salary);
                const bAvg = this.getAverageSalary(b.salary);
                return bAvg - aAvg;
            });
        } else if (this.state.sortBy === 'salary-low') {
            jobs.sort((a, b) => {
                const aAvg = this.getAverageSalary(a.salary);
                const bAvg = this.getAverageSalary(b.salary);
                return aAvg - bAvg;
            });
        }
        
        // Return paginated results
        return {
            jobs: jobs,
            pagination: {
                currentPage: this.state.page,
                totalPages: totalPages,
                totalResults: totalResults,
                resultsPerPage: this.state.resultsPerPage,
                startResult: (this.state.page - 1) * this.state.resultsPerPage + 1,
                endResult: Math.min(this.state.page * this.state.resultsPerPage, totalResults)
            }
        };
    }
    
    // Helper to extract average salary from salary range string
    getAverageSalary(salaryString) {
        const matches = salaryString.match(/(\d+)\s*-\s*(\d+)/);
        if (matches && matches.length === 3) {
            return (parseInt(matches[1]) + parseInt(matches[2])) / 2;
        }
        return 0;
    }
    
    // Show loading state
    showLoadingState() {
        const jobsContainer = document.querySelector('.col-lg-9');
        if (!jobsContainer) return;
        
        // Create loading overlay if it doesn't exist
        let loadingOverlay = document.getElementById('search-loading-overlay');
        if (!loadingOverlay) {
            loadingOverlay = document.createElement('div');
            loadingOverlay.id = 'search-loading-overlay';
            loadingOverlay.className = 'search-loading-overlay';
            loadingOverlay.innerHTML = `
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Đang tải...</span>
                </div>
                <p class="mt-2">Đang tìm kiếm việc làm phù hợp...</p>
            `;
            
            // Style the loading overlay
            Object.assign(loadingOverlay.style, {
                position: 'absolute',
                top: '0',
                left: '0',
                width: '100%',
                height: '100%',
                backgroundColor: 'rgba(255, 255, 255, 0.8)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                zIndex: '100'
            });
            
            // Make container position relative for absolute positioning of overlay
            jobsContainer.style.position = 'relative';
            jobsContainer.appendChild(loadingOverlay);
        } else {
            loadingOverlay.style.display = 'flex';
        }
    }
    
    // Hide loading state
    hideLoadingState() {
        const loadingOverlay = document.getElementById('search-loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }
    
    // Show error state
    showErrorState(message) {
        const jobsContainer = document.querySelector('.col-lg-9');
        if (!jobsContainer) return;
        
        // Create error message
        const errorElement = document.createElement('div');
        errorElement.className = 'alert alert-danger mt-3';
        errorElement.textContent = message;
        
        // Clear previous content and show error
        const resultsInfo = jobsContainer.querySelector('.d-flex.justify-content-between');
        if (resultsInfo) {
            resultsInfo.insertAdjacentElement('afterend', errorElement);
        } else {
            jobsContainer.prepend(errorElement);
        }
    }
    
    // Render search results
    renderSearchResults(results) {
        const { jobs, pagination } = results;
        
        // Update results count info
        const resultsInfo = document.querySelector('.col-lg-9 p.mb-0');
        if (resultsInfo) {
            resultsInfo.innerHTML = `Hiển thị <strong>${pagination.startResult}-${pagination.endResult}</strong> trong số <strong>${pagination.totalResults}</strong> việc làm`;
        }
        
        // Find jobs container
        const jobsContainer = document.querySelector('.col-lg-9');
        if (!jobsContainer) return;
        
        // Remove existing job cards
        const existingJobCards = jobsContainer.querySelectorAll('.job-card');
        existingJobCards.forEach(card => card.remove());
        
        // Remove existing pagination
        const existingPagination = jobsContainer.querySelector('nav[aria-label="Page navigation"]');
        if (existingPagination) {
            existingPagination.remove();
        }
        
        // Insert point (after the results info div)
        const insertPoint = jobsContainer.querySelector('.d-flex.justify-content-between.align-items-center');
        
        // Create and append job cards
        jobs.forEach(job => {
            const jobCard = this.createJobCard(job);
            insertPoint.insertAdjacentElement('afterend', jobCard);
        });
        
        // Create and append pagination
        const paginationElement = this.createPagination(pagination);
        jobsContainer.appendChild(paginationElement);
    }
    
    // Create job card element
    createJobCard(job) {
        const jobCard = document.createElement('div');
        jobCard.className = 'job-card';
        
        // Format posted time
        let postedTime = '';
        if (job.posted_days_ago === 0) {
            postedTime = 'Đăng hôm nay';
        } else if (job.posted_days_ago === 1) {
            postedTime = 'Đăng hôm qua';
        } else if (job.posted_days_ago < 7) {
            postedTime = `Đăng ${job.posted_days_ago} ngày trước`;
        } else if (job.posted_days_ago < 30) {
            const weeks = Math.floor(job.posted_days_ago / 7);
            postedTime = `Đăng ${weeks} tuần trước`;
        } else {
            const months = Math.floor(job.posted_days_ago / 30);
            postedTime = `Đăng ${months} tháng trước`;
        }
        
        // Create tags HTML
        const tagsHtml = job.tags.map(tag => `<span class="badge">${tag}</span>`).join('');
        
        // Set job card HTML
        jobCard.innerHTML = `
            <div class="row">
                <div class="col-md-9">
                    <h5 class="job-title">${job.title}</h5>
                    <p class="company-name">${job.company}</p>
                    <div class="job-meta">
                        <p class="mb-2"><i class="fas fa-map-marker-alt"></i> ${job.location}</p>
                        <p class="mb-2"><i class="fas fa-money-bill-wave"></i> ${job.salary}</p>
                        <p class="mb-0"><i class="fas fa-briefcase"></i> ${job.type}</p>
                    </div>
                    <div class="job-tags">
                        ${tagsHtml}
                    </div>
                </div>
                <div class="col-md-3">
                    <img src="${job.logo}" alt="${job.company}" class="img-fluid mb-3">
                    <p class="text-muted small mb-0">${postedTime}</p>
                </div>
            </div>
            <div class="job-actions">
                <a href="/job/${job.id}" class="btn btn-outline-primary">Xem chi tiết</a>
                <a href="/candidate-form?job_id=${job.id}" class="btn btn-primary">Ứng tuyển ngay</a>
            </div>
        `;
        
        return jobCard;
    }
    
    // Create pagination element
    createPagination(pagination) {
        const { currentPage, totalPages } = pagination;
        
        const nav = document.createElement('nav');
        nav.setAttribute('aria-label', 'Page navigation');
        nav.className = 'mt-4';
        
        const ul = document.createElement('ul');
        ul.className = 'pagination justify-content-center';
        
        // Previous button
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
        
        const prevLink = document.createElement('a');
        prevLink.className = 'page-link';
        prevLink.href = '#';
        prevLink.textContent = 'Trước';
        if (currentPage > 1) {
            prevLink.dataset.page = currentPage - 1;
        } else {
            prevLink.setAttribute('tabindex', '-1');
            prevLink.setAttribute('aria-disabled', 'true');
        }
        
        prevLi.appendChild(prevLink);
        ul.appendChild(prevLi);
        
        // Page numbers
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, startPage + 4);
        
        for (let i = startPage; i <= endPage; i++) {
            const li = document.createElement('li');
            li.className = `page-item ${i === currentPage ? 'active' : ''}`;
            
            const link = document.createElement('a');
            link.className = 'page-link';
            link.href = '#';
            link.textContent = i;
            link.dataset.page = i;
            
            if (i === currentPage) {
                link.setAttribute('aria-current', 'page');
            }
            
            li.appendChild(link);
            ul.appendChild(li);
        }
        
        // Next button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
        
        const nextLink = document.createElement('a');
        nextLink.className = 'page-link';
        nextLink.href = '#';
        nextLink.textContent = 'Tiếp';
        if (currentPage < totalPages) {
            nextLink.dataset.page = currentPage + 1;
        } else {
            nextLink.setAttribute('tabindex', '-1');
            nextLink.setAttribute('aria-disabled', 'true');
        }
        
        nextLi.appendChild(nextLink);
        ul.appendChild(nextLi);
        
        nav.appendChild(ul);
        return nav;
    }
}

// Initialize search when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const searchInstance = new MPSAdvancedSearch();
    
    // Make instance available globally for debugging
    window.mpsSearch = searchInstance;
});
