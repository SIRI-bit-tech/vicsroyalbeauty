# Production Deployment Guide - Vics Royal Beauty

## 🚀 High-Traffic Production Setup

This guide covers the complete production setup for handling high traffic with optimal performance and security.

## Environment Variables Required

Create a `.env` file in your project root with the following variables:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ENVIRONMENT=production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://username:password@host:port/database_name

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# CloudFlare CDN Configuration
CLOUDFLARE_DOMAIN=cdn.yourdomain.com
CLOUDFLARE_ZONE_ID=your-zone-id
CLOUDFLARE_API_TOKEN=your-api-token

# Glitchtip (Sentry) Configuration
GLITCHTIP_DSN=https://your-glitchtip-dsn

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security Settings
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 🏗️ Infrastructure Setup

### 1. Server Requirements
- **CPU**: 4+ cores (8+ recommended for high traffic)
- **RAM**: 8GB+ (16GB+ recommended)
- **Storage**: 50GB+ SSD
- **OS**: Ubuntu 20.04+ or CentOS 8+

### 2. Database Setup
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE vics_royal_db;
CREATE USER vics_royal_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE vics_royal_db TO vics_royal_user;
```

### 3. Redis Setup
```bash
# Install Redis
sudo apt install redis-server

# Configure Redis for production
sudo nano /etc/redis/redis.conf

# Add these settings:
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 4. CloudFlare CDN Setup
1. **Create CloudFlare Account**
2. **Add Domain**: Add your domain to CloudFlare
3. **Configure DNS**: Point to your server IP
4. **Enable CDN**: Enable CloudFlare proxy for static assets
5. **Configure Rules**:
   - Cache static files for 1 year
   - Cache HTML for 1 hour
   - Enable compression
   - Enable minification

### 5. SSL Certificate Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 🚀 Deployment Process

### 1. Quick Deployment
```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 2. Manual Deployment Steps
```bash
# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Test the application
python manage.py runserver 0.0.0.0:8000
```

### 3. Production Server Setup
```bash
# Install Gunicorn
pip install gunicorn gevent

# Start Gunicorn
gunicorn vics_royal.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class gevent \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2
```

### 4. Celery Setup
```bash
# Start Celery worker
celery -A vics_royal worker --loglevel=info --concurrency=4

# Start Celery beat (in separate terminal)
celery -A vics_royal beat --loglevel=info
```

## 🔧 Performance Optimizations

### ✅ Database Optimizations
- **Connection Pooling**: Configured with 50 max connections
- **Query Optimization**: Added select_related and prefetch_related
- **Indexing**: Automatic indexing on frequently queried fields
- **Caching**: Redis-based query caching

### ✅ Caching Strategy
- **Page Cache**: 15 minutes for dynamic pages
- **Session Cache**: 7 days in Redis
- **Long-term Cache**: 30 days for static content
- **Database Cache**: Query result caching

### ✅ CDN Configuration
- **CloudFlare**: Global CDN for static assets
- **Image Optimization**: Cloudinary with automatic optimization
- **Compression**: Gzip compression enabled
- **Cache Headers**: Proper cache control headers

### ✅ Security Features
- **Rate Limiting**: 100 requests/hour per IP
- **DDoS Protection**: CloudFlare DDoS protection
- **Security Headers**: Comprehensive security headers
- **CSP**: Content Security Policy enabled
- **HTTPS**: SSL/TLS enforcement

## 📊 Monitoring & Health Checks

### Health Check Endpoints
- `/health/` - Basic health check
- `/status/` - Detailed system status

### Monitoring Tools
- **Glitchtip**: Error tracking and performance monitoring
- **Redis Monitoring**: Redis Commander or RedisInsight
- **Database Monitoring**: pgAdmin or similar
- **Server Monitoring**: htop, iotop, netstat

### Performance Metrics
- **Response Time**: Target < 200ms
- **Throughput**: Target 1000+ requests/second
- **Error Rate**: Target < 0.1%
- **Uptime**: Target 99.9%

## 🔄 Background Tasks

### Automated Tasks
- **Session Cleanup**: Every hour
- **Newsletter Digest**: Daily
- **Product Cache Update**: Every 30 minutes
- **Email Processing**: Asynchronous

### Task Queues
- **Default Queue**: General tasks
- **Orders Queue**: Order processing
- **Products Queue**: Product updates

## 🛡️ Security Checklist

### ✅ Implemented Security Features
- [x] HTTPS enforcement
- [x] Security headers
- [x] Rate limiting
- [x] CSRF protection
- [x] XSS protection
- [x] Content Security Policy
- [x] SQL injection protection
- [x] File upload validation

### 🔒 Additional Security Recommendations
- [ ] Regular security audits
- [ ] Automated vulnerability scanning
- [ ] Backup encryption
- [ ] Access logging
- [ ] Intrusion detection

## 📈 Scaling Strategy

### Horizontal Scaling
- **Load Balancer**: Nginx or HAProxy
- **Multiple Servers**: Auto-scaling groups
- **Database Replication**: Read replicas
- **Cache Clustering**: Redis cluster

### Vertical Scaling
- **CPU**: Upgrade to more cores
- **RAM**: Increase memory allocation
- **Storage**: SSD with higher IOPS
- **Network**: Better bandwidth

## 🚨 Emergency Procedures

### High Traffic Handling
1. **Enable Auto-scaling**
2. **Increase cache TTL**
3. **Reduce database queries**
4. **Enable maintenance mode if needed**

### Database Issues
1. **Check connection pool**
2. **Optimize slow queries**
3. **Add read replicas**
4. **Increase cache usage**

### Performance Issues
1. **Monitor resource usage**
2. **Check CDN status**
3. **Review error logs**
2. **Scale horizontally**

## 📞 Support & Maintenance

### Regular Maintenance
- **Daily**: Check health endpoints
- **Weekly**: Review performance metrics
- **Monthly**: Security updates
- **Quarterly**: Full system audit

### Contact Information
- **Technical Support**: tech@vicsroyalbeauty.com
- **Emergency**: +234-XXX-XXX-XXXX
- **Documentation**: [Internal Wiki]

---

## 🎯 Success Metrics

Your production environment is ready when you achieve:
- ✅ < 200ms average response time
- ✅ 99.9% uptime
- ✅ < 0.1% error rate
- ✅ 1000+ concurrent users
- ✅ < 1 second page load time
- ✅ 100% SSL coverage
- ✅ Automated monitoring alerts
- ✅ Regular backup success 