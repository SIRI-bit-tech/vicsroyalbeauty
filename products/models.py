from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import uuid
from cloudinary.models import CloudinaryField
from cloudinary import CloudinaryImage

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = CloudinaryField('categories', blank=True, null=True, 
                           transformation={'quality': 'auto', 'fetch_format': 'auto'})
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:product_list_by_category', args=[self.slug])
    
    @property
    def image_url(self):
        """Get optimized image URL with Cloudinary transformations"""
        if self.image:
            return CloudinaryImage(str(self.image)).build_url(
                transformation=[
                    {'width': 400, 'height': 300, 'crop': 'fill', 'quality': 'auto'},
                    {'fetch_format': 'auto'}
                ]
            )
        return None

class Product(models.Model):
    HAIR_CARE_SIZES = [
        ('8', '8 inches'),
        ('10', '10 inches'),
        ('12', '12 inches'),
        ('14', '14 inches'),
        ('16', '16 inches'),
        ('18', '18 inches'),
        ('20', '20 inches'),
        ('22', '22 inches'),
        ('24', '24 inches'),
        ('26', '26 inches'),
        ('28', '28 inches'),
        ('30', '30 inches'),
        ('32', '32 inches'),
        ('34', '34 inches'),
        ('36', '36 inches'),
        ('38', '38 inches'),
        ('40', '40 inches'),
        ('42', '42 inches'),
        ('44', '44 inches'),
        ('46', '46 inches'),
        ('48', '48 inches'),
        ('50', '50 inches'),
    ]
    
    SHOE_SIZES = [
        ('34', '34'),
        ('35', '35'),
        ('36', '36'),
        ('37', '37'),
        ('38', '38'),
        ('39', '39'),
        ('40', '40'),
        ('41', '41'),
        ('42', '42'),
        ('43', '43'),
        ('44', '44'),
        ('45', '45'),
        ('46', '46'),
        ('47', '47'),
        ('48', '48'),
        ('49', '49'),
        ('50', '50'),
        
    ]
    
    PERFUME_SIZES = [
        ('30ml', '30ml'),
        ('50ml', '50ml'),
        ('65ml', '65ml'),
        ('75ml', '75ml'),
        ('100ml', '100ml'),
        ('200ml', '200ml'),
        ('300ml', '300ml'),
        ('500ml', '500ml'),
        ('1000ml', '1000ml'),
    ]
    
    COLORS = [
        ('black', 'Black'),
        ('white', 'White'),
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('brown', 'Brown'),
        ('gray', 'Gray'),
        ('navy', 'Navy'),
        ('beige', 'Beige'),
        ('navy-blue', 'Navy Blue'),
        ('champagne', 'Champagne'),
        ('pink', 'Pink'),
        ('orange', 'Orange'),
        ('purple', 'Purple'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('turquoise', 'Turquoise'),
        ('pearl', 'Pearl'),
        ('ivory', 'Ivory'),
        ('lilac', 'Lilac'),
        
    ]
    
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    available_sizes = models.CharField(max_length=200, blank=True, null=True, help_text='Enter sizes separated by commas. For hair extensions: 8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50 inches. For perfumes: 30ml,50ml,75ml,100ml,200ml. For shoes: 34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50')
    colors = models.CharField(max_length=200, help_text='Enter colors separated by commas (e.g., red,blue,black)', blank=True)
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SEO fields
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate a unique slug
            base_slug = slugify(self.name)
            unique_id = str(uuid.uuid4())[:8]
            self.slug = f"{base_slug}-{unique_id}"
        
        if not self.sku:
            # Generate a unique SKU
            self.sku = f"VICS-{str(uuid.uuid4())[:8].upper()}"
        
        # Generate SEO metadata if not provided
        if not self.meta_title:
            self.meta_title = f"{self.name} - Vics Royal Beauty"
        
        if not self.meta_description:
            self.meta_description = f"{self.description[:157]}..." if len(self.description) > 160 else self.description
        
        if not self.meta_keywords:
            keywords = [self.name, self.category.name, 'hair care', 'premium hair products']
            self.meta_keywords = ', '.join(keywords)
        
        # Clean and format sizes based on category
        if self.available_sizes:
            sizes = [s.strip() for s in self.available_sizes.split(',')]
            category_name = self.category.name.lower()
            
            if 'perfume' in category_name:
                valid_sizes = dict(self.PERFUME_SIZES)
                self.available_sizes = ','.join(s for s in sizes if s in valid_sizes)
            elif 'shoe' in category_name:
                valid_sizes = dict(self.SHOE_SIZES)
                self.available_sizes = ','.join(s for s in sizes if s in valid_sizes)
            else:  # Default to hair care sizes
                valid_sizes = dict(self.HAIR_CARE_SIZES)
                self.available_sizes = ','.join(s.upper() for s in sizes if s.upper() in valid_sizes)
        
        # Clean and format colors
        if self.colors:
            if self.colors.lower().strip() == 'none':
                self.colors = ''  # Set to empty string if 'none' is specified
            else:
                colors = [c.strip().lower() for c in self.colors.split(',')]
                valid_colors = dict(self.COLORS)
                self.colors = ','.join(c for c in colors if c in valid_colors)
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    def get_price(self):
        return self.sale_price if self.sale_price else self.price
    
    @property
    def discount_percentage(self):
        if self.sale_price:
            discount = ((self.price - self.sale_price) / self.price) * 100
            return round(discount)
        return 0
    
    @property
    def is_on_sale(self):
        return bool(self.sale_price)
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    @property
    def size_list(self):
        return [size.strip() for size in self.available_sizes.split(',')] if self.available_sizes else []
    
    @property
    def color_list(self):
        return [color.strip() for color in self.colors.split(',')] if self.colors else []

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = CloudinaryField('products', transformation={'quality': 'auto', 'fetch_format': 'auto'})
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-is_primary', 'id']
    
    def __str__(self):
        return f"{self.product.name} - Image {self.id}"
    
    def save(self, *args, **kwargs):
        # Auto-generate alt text if not provided
        if not self.alt_text:
            self.alt_text = f"{self.product.name} product image"
        super().save(*args, **kwargs)
    
    @property
    def thumbnail_url(self):
        """Get thumbnail version of the image"""
        if self.image:
            return CloudinaryImage(str(self.image)).build_url(
                transformation=[
                    {'width': 150, 'height': 150, 'crop': 'fill', 'quality': 'auto'},
                    {'fetch_format': 'auto'}
                ]
            )
        return None
    
    @property
    def medium_url(self):
        """Get medium size version of the image"""
        if self.image:
            return CloudinaryImage(str(self.image)).build_url(
                transformation=[
                    {'width': 400, 'height': 400, 'crop': 'fill', 'quality': 'auto'},
                    {'fetch_format': 'auto'}
                ]
            )
        return None
    
    @property
    def large_url(self):
        """Get large size version of the image"""
        if self.image:
            return CloudinaryImage(str(self.image)).build_url(
                transformation=[
                    {'width': 800, 'height': 800, 'crop': 'fill', 'quality': 'auto'},
                    {'fetch_format': 'auto'}
                ]
            )
        return None

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')
    
    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name}"
