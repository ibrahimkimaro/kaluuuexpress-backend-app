# Jazzmin Admin Theme Configuration

JAZZMIN_SETTINGS = {
    # Title on the login screen & top navbar
    "site_title": "Kaluu Express Cargo",
    "site_header": "Kaluu Admin",
    "site_brand": "Kaluu Express Cargo",
    "site_logo": "images/kaluu_logo.png",
    "login_logo": "images/kaluu_logo.png",
    "site_logo_classes": "img-circle",
    "site_icon": "images/kaluu_logo.png",
    
    # Welcome text on the login screen
    "welcome_sign": "Welcome to Kaluu Express Cargo Admin",
    
    # Copyright on the footer
    "copyright": "Kaluu Express Cargo - Fast & Safe Delivery",
    
    # Search model in the navbar
    "search_model": ["authentication.User", "shipping.Shipment", "shipping.Invoice"],
    
    # Field name on user model that contains avatar
    "user_avatar": "profile_picture",
    
    ############
    # Top Menu #
    ############
    
    # Links to put along the top menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Support", "url": "https://github.com", "new_window": True},
        {"model": "authentication.User"},
    ],
    
    #############
    # User Menu #
    #############
    
    # Additional links to include in the user menu on the top right
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com", "new_window": True},
        {"model": "authentication.user"}
    ],
    
    #############
    # Side Menu #
    #############
    
    # Whether to display the side menu
    "show_sidebar": True,
    
    # Whether to aut expand the menu
    "navigation_expanded": True,
    
    # Hide these apps when generating side menu
    "hide_apps": [],
    
    # Hide these models when generating side menu
    "hide_models": [],
    
    # List of apps to base side menu ordering off of
    "order_with_respect_to": ["authentication", "shipping"],
    
    # Custom links to append to app groups
    "custom_links": {
        "shipping": [{
            "name": "View Shipments", 
            "url": "/admin/shipping/shipment/",
            "icon": "fas fa-shipping-fast",
            "permissions": ["shipping.view_shipment"]
        }]
    },
    
    # Custom icons for side menu apps/models
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "authentication.User": "fas fa-user-circle",
        "shipping.Shipment": "fas fa-shipping-fast",
        "shipping.Invoice": "fas fa-file-invoice-dollar",
        "shipping.ServiceTier": "fas fa-layer-group",
        "shipping.WeightHandling": "fas fa-weight",
        "shipping.PackingList": "fas fa-clipboard-list",
    },
    
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    #################
    # Related Modal #
    #################
    
    "related_modal_active": False,
    
    #############
    # UI Tweaks #
    #############
    
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    
    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,
    
    ###############
    # Change view #
    ###############
    
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "authentication.user": "collapsible",
        "auth.group": "vertical_tabs"
    },
    
    # Override settings for navbar
    "navbar_small_text": False,
    "footer_small_text": False,
    
    # HTML body classes
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
