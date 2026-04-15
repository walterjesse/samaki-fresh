from django.core.management.base import BaseCommand
from django.db import connection
from django.core.cache import cache
from django.conf import settings

class Command(BaseCommand):
    help = 'Display performance optimization status and recommendations'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('🚀 FastCart Performance Optimization Report'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

        # 1. Cache Status
        self.stdout.write(self.style.HTTP_INFO('\n📦 CACHING STATUS'))
        self.stdout.write('-' * 60)
        
        cache_backend = settings.CACHES.get('default', {}).get('BACKEND', 'Not configured')
        self.stdout.write(f'Cache Backend: {cache_backend}')
        
        if 'LocMemCache' in cache_backend:
            self.stdout.write(self.style.WARNING('⚠️  Local memory cache (development only)'))
            self.stdout.write('   → Use Redis for production')
        elif 'RedisCache' in cache_backend or 'redis' in cache_backend:
            self.stdout.write(self.style.SUCCESS('✅ Redis configured (production ready)'))
        
        # Try to get cache stats
        try:
            cache.set('test_key', 'test_value', 30)
            val = cache.get('test_key')
            if val:
                self.stdout.write(self.style.SUCCESS('✅ Cache is working'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Cache error: {str(e)}'))

        # 2. Database Indexes
        self.stdout.write(self.style.HTTP_INFO('\n🗂️  DATABASE INDEXES'))
        self.stdout.write('-' * 60)
        
        with connection.cursor() as cursor:
            if 'sqlite' in connection.settings_dict['ENGINE']:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
                indexes = cursor.fetchall()
                self.stdout.write(f'Total indexes: {len(indexes)}')
                for idx in indexes[:10]:
                    self.stdout.write(f'  - {idx[0]}')
            else:
                self.stdout.write('Database type: ' + connection.settings_dict['ENGINE'])

        # 3. Compression
        self.stdout.write(self.style.HTTP_INFO('\n🗜️  COMPRESSION'))
        self.stdout.write('-' * 60)
        
        gzip_enabled = 'django.middleware.gzip.GZipMiddleware' in settings.MIDDLEWARE
        if gzip_enabled:
            self.stdout.write(self.style.SUCCESS('✅ GZip compression enabled'))
        else:
            self.stdout.write(self.style.ERROR('❌ GZip compression disabled'))
            self.stdout.write('   → Add to settings.MIDDLEWARE for faster responses')

        # 4. Session Configuration
        self.stdout.write(self.style.HTTP_INFO('\n🔐 SESSION CONFIGURATION'))
        self.stdout.write('-' * 60)
        
        session_engine = settings.SESSION_ENGINE
        self.stdout.write(f'Session Engine: {session_engine}')
        if 'redis' in session_engine.lower() or 'cache' in session_engine.lower():
            self.stdout.write(self.style.SUCCESS('✅ Sessions using cache (optimal)'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Sessions in database (slower)'))

        # 5. Debug Mode
        self.stdout.write(self.style.HTTP_INFO('\n🐛 DEBUG MODE'))
        self.stdout.write('-' * 60)
        
        if settings.DEBUG:
            self.stdout.write(self.style.ERROR('❌ DEBUG = True (production risk)'))
            self.stdout.write('   → Set DEBUG = False in production')
        else:
            self.stdout.write(self.style.SUCCESS('✅ DEBUG = False (production safe)'))

        # 6. Query Analysis
        self.stdout.write(self.style.HTTP_INFO('\n🔍 CURRENT QUERY COUNT'))
        self.stdout.write('-' * 60)
        
        query_count = len(connection.queries)
        self.stdout.write(f'Active queries: {query_count}')
        if query_count > 100:
            self.stdout.write(self.style.WARNING(f'⚠️  High query count! Consider optimization.'))

        # 7. Recommendations
        self.stdout.write(self.style.HTTP_INFO('\n✨ RECOMMENDATIONS'))
        self.stdout.write('-' * 60)
        
        recommendations = []
        
        if 'LocMemCache' in cache_backend:
            recommendations.append('1. Install Redis: pip install django-redis')
            recommendations.append('   Configure in settings.py for production')
        
        if not gzip_enabled:
            recommendations.append('2. Enable GZip compression in MIDDLEWARE')
        
        if session_engine == 'django.contrib.sessions.backends.db':
            recommendations.append('3. Use cache-based sessions for better performance')
        
        if settings.DEBUG:
            recommendations.append('4. Set DEBUG = False for deployment')
        
        if recommendations:
            for rec in recommendations:
                self.stdout.write(f'   {rec}')
        else:
            self.stdout.write(self.style.SUCCESS('✅ All major optimizations in place!'))

        # 8. Performance Tips
        self.stdout.write(self.style.HTTP_INFO('\n💡 QUICK WINS'))
        self.stdout.write('-' * 60)
        self.stdout.write('1. Use select_related() for ForeignKey queries')
        self.stdout.write('2. Use prefetch_related() for ManyToMany queries')
        self.stdout.write('3. Add db_index=True to frequently filtered fields')
        self.stdout.write('4. Cache expensive calculations and API calls')
        self.stdout.write('5. Use lazy loading for images (already done)')
        self.stdout.write('6. Monitor N+1 queries in development')

        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('📖 See PERFORMANCE_OPTIMIZATIONS.md for details\n'))
