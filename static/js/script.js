// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Sort functionality
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            // Get the current search term if any
            const searchParams = new URLSearchParams(window.location.search);
            const currentSearch = searchParams.get('search') || '';
            
            // Redirect to the same page with the new sort parameter
            window.location.href = `/sell?sort=${this.value}${currentSearch ? `&search=${encodeURIComponent(currentSearch)}` : ''}`;
        });
    }
    
    // Search form submission
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get the search term
            const searchInput = this.querySelector('input[name="search"]');
            const searchTerm = searchInput.value.trim();
            
            // Get the current sort parameter if any
            const sortSelect = document.getElementById('sort-select');
            const currentSort = sortSelect ? sortSelect.value : 'date';
            
            // Redirect to the search results
            window.location.href = `/sell?sort=${currentSort}${searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : ''}`;
        });
    }
    
    // Add animation to jersey cards
    const jerseyCards = document.querySelectorAll('.jersey-card');
    jerseyCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.2)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 3px 10px rgba(0, 0, 0, 0.1)';
        });
    });
    
    // Add smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Only apply smooth scroll for links that start with #
            if (href.startsWith('#')) {
                e.preventDefault();
                const targetElement = document.querySelector(href);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Buy Now button
    // const buyButton = document.querySelector('.buy-button .btn');
    // if (buyButton) {
    //     buyButton.addEventListener('click', function(e) {
    //         e.preventDefault();
    //         alert('The purchase functionality is coming soon!');
    //     });
    // }
    
    // Password confirmation for admin actions
    const adminForms = document.querySelectorAll('.admin-panel form');
    if (adminForms) {
        adminForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const passwordField = this.querySelector('input[type="password"]');
                if (passwordField && !passwordField.value) {
                    e.preventDefault();
                    alert('Please enter your password to confirm this action.');
                }
            });
        });
    }
}); 