import datetime
from datetime import timezone
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class ProductManager(models.Manager):
    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(in_stock=True)


class Category(models.Model):
    name = models.CharField(max_length=300, db_index=True)
    slug = models.SlugField(max_length=300, unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('Akala:category_list', args=[self.slug])

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="product", on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_creator', null=True,
                                   blank=True)
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    slug = models.SlugField(max_length=300, blank=True, null=True, unique=True)
    price = models.DecimalField(max_digits=99, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=99, decimal_places=2, null=True, blank=True)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_discount = models.BooleanField(default=False)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    objects = models.Manager()
    products = ProductManager()

    class Meta:
        verbose_name_plural = 'products'
        ordering = ('-created',)

    def get_absolute_url(self):
        return reverse('Akala:product_detail', args=[self.slug])

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.id is not None:
            try:
                old_product = Product.objects.get(id=self.id)
            except Product.DoesNotExist:
                old_product = None

            if self.quantity is not None and self.quantity <= 0:
                self.in_stock = False

            if self.quantity is not None and self.quantity >= 1:
                self.in_stock = True

            if old_product.price != self.price:
                Price_history.objects.create(
                    my_product=self,
                    my_price=self.price,
                    my_date=datetime.datetime.now()
                )
        super(Product, self).save(*args, **kwargs)


class Price_history(models.Model):
    my_product = models.ForeignKey(Product, related_name='product', on_delete=models.CASCADE, default='1')
    my_price = models.CharField(max_length=100, null=True)
    my_date = models.DateField(null=True)


class Basket(models.Model):
    basket_product = models.ManyToManyField(Product, related_name="basket")
    basket_user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)


class Comment(models.Model):
    product_com = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    publish = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    class Meta:
        ordering = ('publish',)

    def __str__(self):
        return f"comment by {self.name}"


class Sold_products(models.Model):
    price_sold = models.DecimalField(max_digits=99, decimal_places=2, null=True, blank=True)
    date_sold = models.DateField()
    products_sold = models.ForeignKey(Product, related_name='product_sold', on_delete=models.CASCADE)

    def __str__(self):
        return self.products_sold.name
