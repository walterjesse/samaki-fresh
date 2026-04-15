"""
Django settings for ShopZatao ecommerce project.
"""

from pathlib import Path

import dj_database_url
from environs import Env
from django.contrib import messages

# --------------------------------------------------
# Base
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env.read_env(BASE_DIR / ".env")

# --------------------------------------------------
# Security / Debug
# --------------------------------------------------
SECRET_KEY = env.str(
    "DJANGO_SECRET_KEY",
    default="shopzatao-local-dev-secure-key-change-in-prod!!",
)

DEBUG = env.bool("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=["127.0.0.1", "localhost"],
)

CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "https://*.ngrok-free.app",
        "https://shopzatao.up.railway.app",
    ],
)

SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=False)
SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SECURE = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=False)

# --------------------------------------------------
# Applications
# --------------------------------------------------
INSTALLED_APPS = [
    "jazzmin",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.humanize",
    "django.contrib.staticfiles",

    # Local apps
    "userauths",
    "store",
    "vendor",
    "customer",
    "blog",

    # Third-party apps
    "django_ckeditor_5",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ecom_prj.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "store.context.default",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ecom_prj.wsgi.application"

# --------------------------------------------------
# Database
# --------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{(BASE_DIR / 'db.sqlite3').as_posix()}",
        conn_max_age=600,
    )
}

# --------------------------------------------------
# Password validation
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 6,  # Reduced minimum for convenience
        }
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# --------------------------------------------------
# Internationalization
# --------------------------------------------------
LANGUAGE_CODE = env.str("DJANGO_LANGUAGE_CODE", default="en-us")
TIME_ZONE = env.str("DJANGO_TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# Static / Media
# --------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --------------------------------------------------
# Cache Configuration
# --------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# --------------------------------------------------
# Session Configuration
# --------------------------------------------------
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_COOKIE_NAME = "sessionid"

# --------------------------------------------------
# Custom user model
# --------------------------------------------------
AUTH_USER_MODEL = "userauths.User"

# --------------------------------------------------
# Payment gateway keys
# --------------------------------------------------
# M-Pesa only - other payment methods removed

# --------------------------------------------------
# Email
# --------------------------------------------------
EMAIL_BACKEND = env.str(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
FROM_EMAIL = env.str("FROM_EMAIL", default="noreply@shopzatao.com")
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default=FROM_EMAIL)
SERVER_EMAIL = env.str("SERVER_EMAIL", default=FROM_EMAIL)

# --------------------------------------------------
# Messages
# --------------------------------------------------
MESSAGE_TAGS = {
    messages.ERROR: "danger",
}

# --------------------------------------------------
# Login redirects
# --------------------------------------------------
LOGIN_URL = "userauths:sign-in"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "userauths:sign-in"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ==================================================
# JAZZMIN ADMIN CUSTOMIZATION
# ==================================================
JAZZMIN_SETTINGS = {
    "site_title": "ShopZatao Admin",
    "site_header": "ShopZatao",
    "site_brand": "ShopZatao",
    "welcome_sign": "Welcome to ShopZatao Admin",
    "copyright": "ShopZatao",

    # Put these files in:
    # static/images/logo.png
    # static/images/favicon.ico
    "site_logo": "images/logo.png",
    "site_icon": "images/favicon.ico",

    "show_sidebar": True,
    "navigation_expanded": True,
    "related_modal_active": True,

    # Custom frontend-matching assets
    "custom_css": "admin/css/custom.css",
    "custom_js": "admin/js/custom.js",

    "user_avatar": None,
    "search_model": "store.Product",
    "show_ui_builder": False,

    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },

    "order_with_respect_to": [
        "auth",
        "auth.user",
        "userauths",
        "userauths.user",
        "userauths.profile",
        "store",
        "store.category",
        "store.brand",
        "store.product",
        "store.cart",
        "store.cartorder",
        "store.cartorderitem",
        "store.review",
        "store.productfaq",
        "store.tag",
        "store.notification",
        "customer",
        "customer.address",
        "customer.wishlist",
        "vendor",
        "vendor.vendor",
        "vendor.coupon",
        "vendor.deliverycouriers",
        "vendor.notification",
        "vendor.payouttracker",
        "vendor.chatmessage",
        "blog",
    ],

    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",

        "userauths.User": "fas fa-user-circle",
        "userauths.Profile": "fas fa-address-card",

        "store.Product": "fas fa-boxes",
        "store.Category": "fas fa-tags",
        "store.Brand": "fas fa-award",
        "store.Cart": "fas fa-shopping-cart",
        "store.CartOrder": "fas fa-receipt",
        "store.CartOrderItem": "fas fa-box-open",
        "store.Review": "fas fa-star",
        "store.ProductFaq": "fas fa-circle-question",
        "store.Tag": "fas fa-tag",
        "store.Notification": "fas fa-bell",

        "customer.Address": "fas fa-location-dot",
        "customer.Wishlist": "fas fa-heart",

        "vendor.Vendor": "fas fa-store",
        "vendor.Coupon": "fas fa-percent",
        "vendor.DeliveryCouriers": "fas fa-truck",
        "vendor.Notification": "fas fa-bell",
        "vendor.PayoutTracker": "fas fa-wallet",
        "vendor.ChatMessage": "fas fa-envelope",

        "blog.Post": "fas fa-blog",
        "blog.Category": "fas fa-folder",
    },

    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-arrow-circle-right",
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "navbar": "navbar-dark navbar-primary",
    "sidebar": "sidebar-dark-primary",
    "accent": "accent-primary",
    "brand_colour": "navbar-primary",
    "navbar_fixed": True,
    "footer_fixed": False,
    "layout_boxed": False,
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
}

# ==================================================
# CKEDITOR 5 CONFIGURATION
# ==================================================
customColorPalette = [
    {"color": "hsl(4, 90%, 58%)", "label": "Red"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
    {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
    {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
    {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
    {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
]

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "imageUpload",
        ],
    },
    "comment": {
        "language": {"ui": "en", "content": "en"},
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
        ],
    },
    "extends": {
        "language": "en",
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
        ],
        "toolbar": [
            "bold",
            "italic",
            "underline",
            "|",
            "link",
            "strikethrough",
            "code",
            "subscript",
            "superscript",
            "highlight",
            "|",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "blockQuote",
            "insertImage",
            "|",
            "fontSize",
            "fontFamily",
            "fontColor",
            "fontBackgroundColor",
            "mediaEmbed",
            "removeFormat",
            "insertTable",
            "sourceEditing",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
                "imageStyle:side",
                "|",
                "toggleImageCaption",
                "|",
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
                "alignCenter",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
            "tableProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
            "tableCellProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
        "list": {
            "properties": {
                "styles": True,
                "startIndex": True,
                "reversed": True,
            }
        },
        "htmlSupport": {
            "allow": [
                {"name": "/.*/", "attributes": True, "classes": True, "styles": True}
            ]
        },
    },
}