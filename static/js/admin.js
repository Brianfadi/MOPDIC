/**
 * MOPDIC Admin JavaScript
 * Handles core admin interface functionality
 */

// Document Ready
$(document).ready(function() {
    // Toggle Sidebar
    $('#sidebarCollapse').on('click', function(e) {
        e.preventDefault();
        $('body').toggleClass('sb-sidenav-toggled');
        localStorage.setItem('sb|sidebar-toggle', $('body').hasClass('sb-sidenav-toggled'));
    });
    
    // Initialize sidebar state from localStorage
    if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
        $('body').addClass('sb-sidenav-toggled');
    }

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // File upload preview with image preview
    $("input[type='file']").on('change', function() {
        var fileName = $(this).val().split('\\').pop();
        var $fileInput = $(this);
        var $previewContainer = $fileInput.closest('.file-upload-wrapper').find('.file-preview');
        
        if (fileName) {
            $fileInput.next('.custom-file-label').html(fileName);
            
            // Show image preview if it's an image
            if (this.files && this.files[0] && this.files[0].type.match('image.*')) {
                var reader = new FileReader();
                
                reader.onload = function(e) {
                    if ($previewContainer.length) {
                        $previewContainer.html(
                            '<div class="img-thumbnail mt-2">' +
                            '<img src="' + e.target.result + '" class="img-fluid" alt="Preview">' +
                            '</div>'
                        );
                    }
                };
                
                reader.readAsDataURL(this.files[0]);
            } else if ($previewContainer.length) {
                $previewContainer.html(
                    '<div class="file-icon mt-2">' +
                    '<i class="fas fa-file fa-3x text-muted"></i>' +
                    '<div class="small text-muted mt-1">' + fileName + '</div>' +
                    '</div>'
                );
            }
        }
    });
    
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip({
        trigger: 'hover',
        placement: 'top',
        container: 'body'
    });
    
    // Initialize popovers
    $('[data-bs-toggle="popover"]').popover({
        trigger: 'hover',
        placement: 'top',
        container: 'body',
        html: true
    });

    // Datatable initialization
    if ($.fn.DataTable) {
        $('.datatable').DataTable({
            responsive: true,
            "order": [],
            "language": {
                "search": "<i class='fas fa-search'></i>",
                "searchPlaceholder": "Search...",
                "lengthMenu": "Show _MENU_ entries",
                "info": "Showing _START_ to _END_ of _TOTAL_ entries",
                "infoEmpty": "No entries found",
                "infoFiltered": "(filtered from _MAX_ total entries)",
                "paginate": {
                    "previous": "<i class='fas fa-chevron-left'></i>",
                    "next": "<i class='fas fa-chevron-right'></i>"
                }
            },
            "dom": "<'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'f>>" +
                   "<'row'<'col-sm-12'tr>>" +
                   "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>"
        });
    }

    // CKEditor initialization
    if (typeof CKEDITOR !== 'undefined') {
        CKEDITOR.replaceAll('wysiwyg-editor', {
            toolbar: [
                { name: 'document', items: ['Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates'] },
                { name: 'clipboard', items: ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo'] },
                { name: 'editing', items: ['Find', 'Replace', '-', 'SelectAll', '-', 'Scayt'] },
                { name: 'forms', items: ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton', 'HiddenField'] },
                '/',
                { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'CopyFormatting', 'RemoveFormat'] },
                { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl', 'Language'] },
                { name: 'links', items: ['Link', 'Unlink', 'Anchor'] },
                { name: 'insert', items: ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe'] },
                '/',
                { name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize'] },
                { name: 'colors', items: ['TextColor', 'BGColor'] },
                { name: 'tools', items: ['Maximize', 'ShowBlocks'] },
                { name: 'about', items: ['About'] }
            ],
            height: 400,
            removeButtons: ''
        });
    }

    // Datepicker initialization
    if ($.fn.datepicker) {
        $('.datepicker').datepicker({
            format: 'yyyy-mm-dd',
            autoclose: true,
            todayHighlight: true
        });
    }

    // Timepicker initialization
    if ($.fn.timepicker) {
        $('.timepicker').timepicker({
            showMeridian: false,
            minuteStep: 15
        });
    }

    // Select2 initialization
    if ($.fn.select2) {
        $('.select2').select2({
            theme: 'bootstrap4',
            width: '100%'
        });
    }

    // Password toggle
    $('.toggle-password').on('click', function() {
        const input = $($(this).attr('toggle'));
        const type = input.attr('type') === 'password' ? 'text' : 'password';
        input.attr('type', type);
        $(this).toggleClass('fa-eye fa-eye-slash');
    });

    // Form validation
    if ($.fn.validate) {
        $('.needs-validation').validate({
            errorElement: 'div',
            errorClass: 'invalid-feedback',
            highlight: function(element, errorClass, validClass) {
                $(element).addClass('is-invalid');
            },
            unhighlight: function(element, errorClass, validClass) {
                $(element).removeClass('is-invalid');
            },
            errorPlacement: function(error, element) {
                if (element.parent('.input-group').length) {
                    error.insertAfter(element.parent());
                } else {
                    error.insertAfter(element);
                }
            }
        });
    }

    // Delete confirmation with SweetAlert2
    $(document).on('click', '.confirm-delete', function(e) {
        e.preventDefault();
        const deleteUrl = $(this).attr('href');
        
        Swal.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it!',
            cancelButtonText: 'Cancel',
            customClass: {
                confirmButton: 'btn btn-danger me-2',
                cancelButton: 'btn btn-secondary'
            },
            buttonsStyling: false
        }).then((result) => {
            if (result.isConfirmed) {
                // Show loading state
                Swal.fire({
                    title: 'Deleting...',
                    text: 'Please wait while we delete the item.',
                    allowOutsideClick: false,
                    didOpen: () => {
                        Swal.showLoading();
                    }
                });
                
                // Submit delete form
                $('<form>', {
                    'method': 'POST',
                    'action': deleteUrl
                }).append($('<input>', {
                    'type': 'hidden',
                    'name': 'csrfmiddlewaretoken',
                    'value': $('meta[name="csrf-token"]').attr('content')
                })).appendTo('body').submit();
            }
        });
    });
    
    // Toggle password visibility
    $('.toggle-password').on('click', function() {
        const $input = $($(this).attr('toggle'));
        const type = $input.attr('type') === 'password' ? 'text' : 'password';
        $input.attr('type', type);
        $(this).find('i').toggleClass('fa-eye fa-eye-slash');
    });
    
    // Auto-hide alerts after 5 seconds
    window.setTimeout(function() {
        $('.alert:not(.alert-permanent)').fadeTo(500, 0).slideUp(500, function(){
            $(this).remove();
        });
    }, 5000);
    
    // Initialize summernote if available
    if ($.fn.summernote) {
        $('.summernote').summernote({
            height: 300,
            minHeight: null,
            maxHeight: null,
            focus: true,
            toolbar: [
                ['style', ['style']],
                ['font', ['bold', 'italic', 'underline', 'clear']],
                ['fontname', ['fontname']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['height', ['height']],
                ['table', ['table']],
                ['insert', ['link', 'picture', 'video']],
                ['view', ['fullscreen', 'codeview', 'help']]
            ]
        });
    }

    /**
 * Read URL for image preview
 * @param {object} input - File input element
 * @param {string} previewId - ID of the preview container
 */
/**
 * Read URL for image preview
 * @param {object} input - File input element
 * @param {string} previewId - ID of the preview container
 */
function readURL(input, previewId) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            $('#' + previewId).attr('src', e.target.result);
            $('#' + previewId).parent().show();
        };
        reader.readAsDataURL(input.files[0]);
    }
}

    $('.image-upload').on('change', function() {
        var previewId = $(this).data('preview');
        readURL(this, previewId);
    });

    // Auto-slug generation
    $('.auto-slug').on('keyup', function() {
        var slug = $(this).val()
            .toLowerCase()
            .replace(/[^\w\s-]/g, '') // Remove special chars
            .replace(/\s+/g, '-')      // Replace spaces with -
            .replace(/--+/g, '-');     // Replace multiple - with single -
        $('#slug').val(slug);
    });

    // Toggle password visibility in login form
    $('.toggle-password').click(function() {
        $(this).toggleClass('fa-eye fa-eye-slash');
        var input = $($(this).attr('toggle'));
        if (input.attr('type') == 'password') {
            input.attr('type', 'text');
        } else {
            input.attr('type', 'password');
        }
    });

    // Initialize Summernote
    if ($.fn.summernote) {
        $('.summernote').summernote({
            height: 300,
            minHeight: null,
            maxHeight: null,
            focus: true,
            toolbar: [
                ['style', ['style']],
                ['font', ['bold', 'underline', 'clear']],
                ['fontname', ['fontname']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
                ['insert', ['link', 'picture', 'video']],
                ['view', ['fullscreen', 'codeview', 'help']]
            ]
        });
    }

    // Custom file input
    bsCustomFileInput.init();

    // Auto-hide alerts after 5 seconds
    window.setTimeout(function() {
        $(".alert").fadeTo(500, 0).slideUp(500, function(){
            $(this).remove();
        });
    }, 5000);

    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

/**
 * Show page loader
 */
function showLoader() {
    if ($('.page-loader').length === 0) {
        $('body').append(`
            <div class="page-loader">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        </div>`;
    
    $('.toast-container').append(toast);
    $('.toast').toast('show');
    
    // Remove toast after it's hidden
    $('.toast').on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// AJAX form submission
function submitForm(formId, successCallback, errorCallback) {
    const form = $(`#${formId}`);
    const formData = new FormData(form[0]);
    
    $.ajax({
        url: form.attr('action'),
        type: form.attr('method'),
        data: formData,
        processData: false,
        contentType: false,
        beforeSend: function() {
            showLoader();
            form.find('button[type="submit"]').prop('disabled', true);
        },
        success: function(response) {
            if (typeof successCallback === 'function') {
                successCallback(response);
            } else {
                showToast('success', response.message || 'Operation completed successfully');
                if (response.redirect) {
                    setTimeout(() => {
                        window.location.href = response.redirect;
                    }, 1500);
                }
            }
        },
        error: function(xhr) {
            let errorMessage = 'An error occurred. Please try again.';
            if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMessage = xhr.responseJSON.message;
            }
            
            if (typeof errorCallback === 'function') {
                errorCallback(xhr);
            } else {
                showToast('danger', errorMessage);
            }
        },
        complete: function() {
            hideLoader();
            form.find('button[type="submit"]').prop('disabled', false);
        }
    });
}
