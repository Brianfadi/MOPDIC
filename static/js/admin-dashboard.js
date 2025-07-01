/**
 * MOPDIC Admin Dashboard JavaScript
 * Handles all interactive elements of the admin dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Sidebar toggle functionality
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }

    // Theme toggle functionality
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        // Check for saved theme preference or use preferred color scheme
        const currentTheme = localStorage.getItem('theme') || 
            (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        
        // Set the initial theme
        if (currentTheme === 'dark') {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            document.documentElement.setAttribute('data-bs-theme', 'light');
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
        
        // Toggle theme on button click
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            if (currentTheme === 'dark') {
                document.documentElement.setAttribute('data-bs-theme', 'light');
                localStorage.setItem('theme', 'light');
                themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
            } else {
                document.documentElement.setAttribute('data-bs-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            }
        });
    }

    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        // Users Chart
        const usersCtx = document.getElementById('usersChart');
        if (usersCtx) {
            new Chart(usersCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                    datasets: [{
                        label: 'New Users',
                        data: [65, 59, 80, 81, 56, 55, 40],
                        backgroundColor: 'rgba(78, 115, 223, 0.1)',
                        borderColor: 'rgba(78, 115, 223, 1)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgba(78, 115, 223, 1)',
                        pointBorderColor: '#fff',
                        pointHoverRadius: 5,
                        pointHoverBackgroundColor: 'rgba(78, 115, 223, 1)',
                        pointHoverBorderColor: '#fff',
                        pointHitRadius: 10,
                        pointBorderWidth: 2,
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleFont: {
                                size: 14
                            },
                            bodyFont: {
                                size: 14
                            },
                            callbacks: {
                                label: function(context) {
                                    return 'Users: ' + context.raw;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false,
                                drawBorder: false
                            },
                            ticks: {
                                maxRotation: 0,
                                autoSkipPadding: 15
                            }
                        },
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)',
                                drawBorder: false
                            },
                            ticks: {
                                maxTicksLimit: 5,
                                padding: 10
                            }
                        }
                    }
                }
            });
        }


        // Projects Chart
        const projectsCtx = document.getElementById('projectsChart');
        if (projectsCtx) {
            new Chart(projectsCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Completed', 'In Progress', 'Not Started'],
                    datasets: [{
                        data: [55, 30, 15],
                        backgroundColor: ['#1cc88a', '#36b9cc', '#e74a3b'],
                        hoverBackgroundColor: ['#17a673', '#2c9faf', '#be2617'],
                        hoverBorderColor: 'rgba(234, 236, 244, 1)',
                        borderWidth: 2
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                usePointStyle: true,
                                padding: 20,
                                font: {
                                    size: 12
                                }
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleFont: {
                                size: 14
                            },
                            bodyFont: {
                                size: 14
                            },
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.raw || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = Math.round((value / total) * 100) + '%';
                                    return `${label}: ${value} (${percentage})`;
                                }
                            }
                        }
                    },
                    cutout: '70%'
                }
            });
        }
    }


    // Handle refresh button click
    const refreshBtn = document.getElementById('refreshDashboard');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const btn = this;
            const originalHtml = btn.innerHTML;
            
            // Show loading state
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Refreshing...';
            
            // Simulate API call
            setTimeout(function() {
                // Reset button state
                btn.innerHTML = originalHtml;
                btn.disabled = false;
                
                // Show success toast
                showToast('Dashboard refreshed successfully!', 'success');
                
                // Here you would typically reload the data
                // For now, we'll just log to console
                console.log('Dashboard data refreshed');
            }, 1500);
        });
    }
    
    // Handle export button click
    const exportBtn = document.getElementById('exportDashboard');
    if (exportBtn) {
        exportBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const btn = this;
            const originalHtml = btn.innerHTML;
            
            // Show loading state
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Exporting...';
            
            // Simulate export process
            setTimeout(function() {
                // Reset button state
                btn.innerHTML = originalHtml;
                btn.disabled = false;
                
                // Show success toast with download link
                showToast('Export completed! Preparing download...', 'success');
                
                // Here you would typically generate and trigger a file download
                // For now, we'll just log to console
                console.log('Exporting dashboard data...');
                
                // Simulate file download after a short delay
                setTimeout(function() {
                    // This would be replaced with actual file download logic
                    const link = document.createElement('a');
                    link.href = '#';
                    link.download = 'dashboard-export-' + new Date().toISOString().split('T')[0] + '.pdf';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }, 1000);
            }, 2000);
        });
    }
    
    // Initialize DataTables if available
    if (typeof $.fn.DataTable === 'function') {
        $('.datatable').DataTable({
            responsive: true,
            pageLength: 10,
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
            language: {
                search: "_INPUT_",
                searchPlaceholder: "Search...",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "Showing 0 to 0 of 0 entries",
                infoFiltered: "(filtered from _MAX_ total entries)",
                zeroRecords: "No matching records found",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                }
            },
            dom: "<'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'f>>" +
                 "<'row'<'col-sm-12'tr>>" +
                 "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
            drawCallback: function() {
            }
        });
    }
    
    // Show welcome toast on first visit
    if (!localStorage.getItem('dashboardWelcomeShown')) {
        setTimeout(function() {
            showToast('Welcome to MOPDIC Admin Dashboard!', 'info', 5000);
            localStorage.setItem('dashboardWelcomeShown', 'true');
        }, 1500);
    }
});

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of toast (success, error, warning, info)
 * @param {number} delay - Time in milliseconds before auto-hiding (default: 3000)
 */
function showToast(message, type = 'info', delay = 3000) {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const toastId = 'toast-' + Date.now();
    const iconMap = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${iconMap[type] || 'info-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        animation: true,
        autohide: true,
        delay: delay
    });
    
    bsToast.show();
    
    // Remove toast from DOM after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Handle AJAX form submissions
$(document).on('submit', '.ajax-form', function(e) {
    e.preventDefault();
    
    const form = $(this);
    const submitBtn = form.find('button[type="submit"]');
    const originalBtnText = submitBtn.html();
    const formData = new FormData(this);
    const url = form.attr('action') || window.location.href;
    const method = form.attr('method') || 'POST';
    
    // Show loading state
    submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...');
    
    // Submit form via AJAX
    $.ajax({
        url: url,
        type: method,
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                showToast(response.message || 'Operation completed successfully!', 'success');
                
                // If redirect URL is provided, redirect after a short delay
                if (response.redirect) {
                    setTimeout(function() {
                        window.location.href = response.redirect;
                    }, 1500);
                }
                
                // If a callback function is provided, execute it
                if (typeof window[response.callback] === 'function') {
                    window[response.callback](response);
                }
                
                // If form should be reset on success
                if (form.data('reset-on-success') !== false) {
                    form[0].reset();
                }
            } else {
                showToast(response.message || 'An error occurred. Please try again.', 'error');
            }
        },
        error: function(xhr, status, error) {
            let errorMessage = 'An error occurred. Please try again.';
            try {
                const response = JSON.parse(xhr.responseText);
                if (response.message) {
                    errorMessage = response.message;
                } else if (response.error) {
                    errorMessage = response.error;
                }
            } catch (e) {
                console.error('Error parsing error response:', e);
            }
            showToast(errorMessage, 'error');
        },
        complete: function() {
            // Restore button state
            submitBtn.prop('disabled', false).html(originalBtnText);
        }
    });
});

// Handle delete confirmations
$(document).on('click', '.confirm-delete', function(e) {
    e.preventDefault();
    
    const button = $(this);
    const title = button.data('title') || 'Are you sure?';
    const text = button.data('text') || 'This action cannot be undone.';
    const confirmText = button.data('confirm-text') || 'Yes, delete it!';
    const cancelText = button.data('cancel-text') || 'Cancel';
    const icon = button.data('icon') || 'warning';
    const url = button.attr('href');
    const method = button.data('method') || 'DELETE';
    const form = button.closest('form');
    
    Swal.fire({
        title: title,
        text: text,
        icon: icon,
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        confirmButtonText: confirmText,
        cancelButtonText: cancelText,
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            if (form.length) {
                // If it's a form submission
                if (method.toUpperCase() !== 'POST') {
                    // Add method override for RESTful routes
                    $('<input>').attr({
                        type: 'hidden',
                        name: '_method',
                        value: method
                    }).appendTo(form);
                }
                form.submit();
            } else if (url) {
                // If it's a link with a URL
                if (method.toUpperCase() === 'GET') {
                    window.location.href = url;
                } else {
                    // For non-GET requests, create a form dynamically
                    const deleteForm = $('<form>', {
                        'method': 'POST',
                        'action': url
                    });
                    
                    if (method.toUpperCase() !== 'POST') {
                        $('<input>').attr({
                            type: 'hidden',
                            name: '_method',
                            value: method
                        }).appendTo(deleteForm);
                    }
                    
                    $('<input>').attr({
                        type: 'hidden',
                        name: '_token',
                        value: $('meta[name="csrf-token"]').attr('content')
                    }).appendTo(deleteForm);
                    
                    deleteForm.appendTo('body').submit();
                }
            } else {
                // If it's a button with a click handler
                const clickHandler = button.data('click-handler');
                if (clickHandler && typeof window[clickHandler] === 'function') {
                    window[clickHandler](button);
                } else if (button.attr('onclick')) {
                    eval(button.attr('onclick'));
                }
            }
        }
    });
});
