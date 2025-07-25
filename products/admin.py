from django.contrib import admin
from .models import Category, Product, ProductImage, Review
from django import forms

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    ordering = ('name',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('user', 'rating', 'comment', 'created_at')
    can_delete = False

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'sale_price', 'stock', 'is_featured', 'is_active')
    list_filter = ('category', 'is_featured', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ReviewInline]
    list_editable = ('price', 'sale_price', 'stock', 'is_featured', 'is_active')
    
    def get_fieldsets(self, request, obj=None):
        # Get the base fieldsets
        fieldsets = [
        (None, {
            'fields': ('category', 'name', 'slug', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'sale_price', 'stock')
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'is_new_arrival', 'is_active')
        }),
        ]
        
        # Add size and color fields based on category
        if obj and 'perfume' in obj.category.name.lower():
            # For perfumes, only show sizes (no colors)
            fieldsets.insert(2, ('Options', {
                'fields': ('available_sizes',),
                'description': 'Enter perfume sizes (e.g., 50ml,100ml)'
            }))
        elif obj and any(word in obj.category.name.lower() for word in ['extensions', 'wigs']):
            # For hair extensions and wigs, show both sizes and colors
            fieldsets.insert(2, ('Options', {
                'fields': ('available_sizes', 'colors'),
                'description': 'Enter hair lengths in inches (e.g., 12,14,16,18) and colors. Type "none" if no colors are available.'
            }))
        else:
            # For hair care products, show sizes in ml and colors
            fieldsets.insert(2, ('Options', {
                'fields': ('available_sizes', 'colors'),
                'description': 'Enter product sizes (e.g., 30ml,50ml,100ml) and colors. Type "none" if no colors are available.'
            }))
        
        return fieldsets
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            # Update help text based on category
            if 'perfume' in obj.category.name.lower():
                form.base_fields['available_sizes'].help_text = 'Enter sizes separated by commas (e.g., 50ml,100ml)'
                if 'colors' in form.base_fields:
                    form.base_fields['colors'].widget = forms.HiddenInput()
            elif any(word in obj.category.name.lower() for word in ['extensions', 'wigs']):
                form.base_fields['available_sizes'].help_text = 'Enter hair lengths in inches separated by commas (e.g., 12,14,16,18,20)'
                form.base_fields['colors'].help_text = 'Enter colors separated by commas (e.g., black,brown,blonde) or type "none" if no colors are available'
            else:
                form.base_fields['available_sizes'].help_text = 'Enter sizes in ml separated by commas (e.g., 30ml,50ml,100ml)'
                form.base_fields['colors'].help_text = 'Enter colors separated by commas (e.g., red,blue,black) or type "none" if no colors are available'
        return form

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__email', 'comment')
    readonly_fields = ('created_at',)
