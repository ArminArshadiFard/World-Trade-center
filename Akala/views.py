from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.db.models.functions import ExtractYear, ExtractWeek, ExtractMonth
from django.utils import timezone
from datetime import datetime, timedelta, date
import datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from .models import Category, Product, Basket, Price_history, Sold_products
from .forms import login_user, Createuserform, Add_product, Add_to_basket, NewCommentForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from chartjs.views.lines import BaseLineChartView
from django.contrib.auth.forms import AuthenticationForm


def categories(request):
    return {
        'categories': Category.objects.all()
    }


def product_all(request):
    products = Product.products.all()
    return render(request, 'home.html', {'products': products})


def seller_signup(request):
    form = Createuserform()

    if request.method == 'POST':
        form = Createuserform(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'alrighttttttt' + user)
            return redirect('Akala:product_all')

    return render(request, 'seller_sign.html', {'form': form})


class LineChartJSONView(BaseLineChartView):

    def get_labels(self, *args, **kwargs):
        product = get_object_or_404(Product, slug=self.kwargs['slug'])
        doo = Price_history.objects.filter(my_product=product)
        down = [date.strftime('%Y-%m-%d') for date in (doo.values_list("my_date", flat=True))]
        return down

    def get_providers(self):
        return ["price"]

    def get_data(self, *args, **kwargs):
        product = get_object_or_404(Product, slug=self.kwargs['slug'])
        poo = Price_history.objects.filter(my_product=product)
        left = [float(x) for x in poo.values_list("my_price", flat=True)]
        return [left]


line_chart_json = LineChartJSONView.as_view()


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, in_stock=True)

    my_price = False
    if Price_history.objects.filter(my_product=product).first():
        my_price = True

    comments = product.comments.filter(status=True)
    user_comment = None

    if request.method == 'POST':
        if "add_comment" in request.POST:
            comment_form = NewCommentForm(request.POST)
            if comment_form.is_valid():
                user_comment = comment_form.save(commit=False)
                user_comment.product_com = product
                user_comment.save()
                return redirect('Akala:product_detail', slug=slug)
        if request.user.is_authenticated:
            if 'add_to_basket' in request.POST:
                basket = Basket.objects.filter(basket_user=request.user).first()
                if not basket:
                    basket = Basket.objects.create(basket_user=request.user)
                basket.basket_product.add(product)
                return redirect('Akala:product_detail', slug=slug)
        else:
            redirect('Akala:login_user')

    comment_form = NewCommentForm
    basket_form = Add_to_basket
    error = basket_form.errors

    contex = {
        'error': error,
        'product': product,
        'form': basket_form,
        'user_comment': user_comment,
        'comments': comments,
        'comment_form': comment_form,
        'chart': line_chart_json,
        'my_price': my_price,
    }

    return render(request, 'products/single.html', contex)


@login_required(login_url='Akala:login_user')
def basket_show(request):
    basket = Basket.objects.filter(basket_user=request.user).first()
    if not basket:
        Basket.objects.create(basket_user=request.user)

    user = request.user.username
    products = basket.basket_product.all()

    total_price = 0
    for product in products:
        if product.is_discount:
            total_price += product.discounted_price
        else:
            total_price += product.price

    contex = {
        'products': products,
        'user': user,
        'total_price': total_price,
    }
    return render(request, 'products/basket.html', contex)


@login_required(login_url='Akala:login_user')
def delete_basket_product(request, slug):
    basket_product = get_object_or_404(Product, slug=slug)
    basket_all = Basket.objects.filter(basket_user=request.user).first()
    basket_all.basket_product.remove(basket_product)
    return redirect('Akala:basket_show')


def buy_basket(request):
    basket = Basket.objects.filter(basket_user=request.user).first()
    all_products = basket.basket_product.all()
    current_date = date.today()

    for product in all_products:
        if product.is_discount:
            price_sold = product.discounted_price
        else:
            price_sold = product.price

        if product.quantity != 0:
            product.quantity -= 1
        else:
            print('out of stock')
        sold_product = Sold_products(products_sold=product, price_sold=price_sold, date_sold=current_date)
        product.save()
        sold_product.save()
        basket.basket_product.clear()
    return redirect('Akala:basket_show')


def category_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    return render(request, 'products/category.html', {'category': category, 'products': products})


def login_view(request):
    error_msg = ""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                error_msg = 'Your credentials are not correct'
        else:
            error_msg = 'Your credentials are not correct'
    else:
        form = AuthenticationForm()

    context = {
        "form": form,
        "error_message": error_msg
    }
    
    return render(request, 'seller_login.html', context)


def logoutSeller(request):
    logout(request)
    return redirect('/')


@login_required(login_url='Akala:login_user')
def edit_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    form = Add_product(instance=product)

    if request.method == 'POST':
        form = Add_product(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()

    return render(request, 'edit_product.html', {'form': form})


@login_required(login_url='Akala:login_user')
def delete_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product.delete()
    return redirect('Akala:user_page')


@login_required(login_url='Akala:login_user')
def user_page(request):
    products = Product.products.filter(created_by=request.user)
    if request.method == 'POST':
        form = Add_product(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            return redirect('Akala:user_page')
    else:
        form = Add_product(request.POST)

    what_seller_sold = Sold_products.objects.filter(products_sold__created_by=request.user)

    income = 0
    for product in what_seller_sold:
        if product.products_sold.is_discount:
            income += product.products_sold.discounted_price
        else:
            income += product.products_sold.price

    previous_months_sales = last_month_sales()
    previous_weeks_sales = last_week_sales()
    previous_years_sales = last_years_sales()
    this_years_sales = current_year_sales()
    this_weeks_sales = current_week_sales()
    this_months_sales = current_month_sales(products)
    todays_sales = last_24h_sales()
    yearly_data = yearly_chart_data()
    # weekly_data = weekly_chart_data()
    # monthly_data = monthly_chart_data()

    contex = {
        'form': form,
        'products': products,
        'what_seller_sold': what_seller_sold,
        'income': income,
        'previous_months_sales': previous_months_sales,
        'previous_weeks_sales': previous_weeks_sales,
        'previous_years_sales': previous_years_sales,
        'this_years_sales': this_years_sales,
        'this_weeks_sales': this_weeks_sales,
        'this_months_sales': this_months_sales,
        'todays_sales': todays_sales,
        'yearly_data': yearly_data,
        # 'monthly_data': monthly_data,
        # 'weekly_data': weekly_data,

    }

    return render(request, 'seller_page.html', contex)


def monthly_chart_data():
    last_month_end = timezone.now()
    last_12_months_end = last_month_end - timedelta(days=30 * 12)

    sales_data = Sold_products.objects.filter(date_sold__gte=last_12_months_end, date_sold__lte=last_month_end) \
        .annotate(month=ExtractMonth('date_sold')).values('month').annotate(total_sales=Sum('price_sold')).order_by(
        'month')

    if not last_month_end.year == last_12_months_end.year:
        start_month_number = last_12_months_end.month
        end_month_number = last_month_end.month
        start_month_number -= 12
        month_numbers = list(range(start_month_number, end_month_number + 1))

        data = [[month_number, 0] for month_number in month_numbers]

        for item in sales_data:
            month_number = item['month']
            total_sales = int(item['total_sales'])
            data[month_number - start_month_number][1] = total_sales

        return data


def weekly_chart_data():
    today = timezone.now()
    last_week_end = today
    last_6_weeks_end = today - timedelta(weeks=6)

    sales_data = Sold_products.objects.filter(date_sold__gte=last_6_weeks_end, date_sold__lte=last_week_end) \
        .annotate(week=ExtractWeek('date_sold')).values('week').annotate(total_sales=Sum('price_sold')).order_by('week')

    start_week_number = last_6_weeks_end.isocalendar()[1]
    end_week_number = last_week_end.isocalendar()[1]
    week_numbers = list(range(start_week_number, end_week_number + 1))

    data = [[week_number, 0] for week_number in week_numbers]

    for item in sales_data:
        week_number = item['week']
        total_sales = int(item['total_sales'])
        data[week_number - start_week_number][1] = total_sales
    return data


def yearly_chart_data():
    today = timezone.now()
    last_year_end = today
    last_5_years_end = today - relativedelta(years=5)

    sales_data = Sold_products.objects.filter(date_sold__gte=last_5_years_end, date_sold__lte=last_year_end) \
        .annotate(year=ExtractYear('date_sold')).values('year').annotate(total_sales=Sum('price_sold')).order_by('year')

    default_data = [
        [2016, 0],
        [2017, 1000],
        [2018, 10000],
        [2019, 15000],
        [2020, 30000],
    ]

    data = default_data + [[item['year'], int(item['total_sales'])] for item in sales_data]

    return data


def last_24h_sales():
    # Get the current date and time
    now = timezone.now()

    # Calculate the start date and time for the last 24 hours
    last_24h_start = now - timedelta(hours=24)

    # Query the Sold_products model for sales within the last 24 hours
    last_24h_sales = Sold_products.objects.filter(date_sold__gte=last_24h_start, date_sold__lte=now)

    # Calculate the total sales amount for the last 24 hours
    last_24h_sales_total = sum([sale.price_sold for sale in last_24h_sales])
    return last_24h_sales_total


def current_month_sales(products):
    x = products.last()
    # Get the current date
    today = timezone.now()

    # Calculate the start date for the current month (1st day of the current month)
    current_month_start = today.replace(day=1)

    # Query the Sold_products model for sales within the current month until today
    current_month_sales = Sold_products.objects.filter(date_sold__gte=current_month_start, date_sold__lte=today).filter(
        products_sold=x)
    # Calculate the total sales amount for the current month
    current_month_sales_total = sum([sale.price_sold for sale in current_month_sales])
    return current_month_sales_total


def current_year_sales():
    # Get the current date
    today = timezone.now()

    # Calculate the start date for the current year
    current_year_start = today.replace(month=1, day=1)

    # Query the Sold_products model for sales within the current year until today
    current_year_sales = Sold_products.objects.filter(date_sold__gte=current_year_start, date_sold__lte=today)

    # Calculate the total sales amount for the current year
    current_year_sales_total = sum([sale.price_sold for sale in current_year_sales])
    return current_year_sales_total


def current_week_sales():
    # Get the current date
    today = timezone.now()

    # Calculate the start date for the current week (Monday of the current week)
    current_week_start = today - timedelta(days=today.weekday())

    # Query the Sold_products model for sales within the current week until today
    current_week_sales = Sold_products.objects.filter(date_sold__gte=current_week_start, date_sold__lte=today)

    # Calculate the total sales amount for the current week
    current_week_sales_total = sum([sale.price_sold for sale in current_week_sales])
    return current_week_sales_total


def last_month_sales():
    # Get the current date
    today = timezone.now()

    # Calculate the start and end dates for last month
    last_month_end = today - datetime.timedelta(days=today.day)
    last_month_start = last_month_end.replace(day=1)

    # Query the Sold_products model for sales within last month
    last_month_sales = Sold_products.objects.filter(date_sold__gte=last_month_start, date_sold__lte=last_month_end)

    # Calculate the total sales amount for last month
    last_month_sales_total = sum([sale.price_sold for sale in last_month_sales])
    return last_month_sales_total


def last_week_sales():
    today = timezone.now().date()

    # Calculate the start and end dates for last week (assuming Monday to Sunday week)
    last_week_end = today - datetime.timedelta(days=today.weekday())
    last_week_start = last_week_end - datetime.timedelta(days=6)

    # Query the Sold_products model for sales within last week
    last_week_sales = Sold_products.objects.filter(date_sold__gte=last_week_start, date_sold__lte=last_week_end)

    # Calculate the total sales amount for last week
    last_week_sales_total = sum([sale.price_sold for sale in last_week_sales])
    return last_week_sales_total


def last_years_sales():
    today = timezone.now().date()

    # Calculate the start and end dates for last year
    last_year_end = today.replace(month=1, day=1) - datetime.timedelta(days=1)
    last_year_start = last_year_end.replace(year=last_year_end.year - 1, month=1, day=1)

    # Query the Sold_products model for sales within last year
    last_year_sales = Sold_products.objects.filter(date_sold__gte=last_year_start, date_sold__lte=last_year_end)

    # Calculate the total sales amount for last year
    last_year_sales_total = sum([sale.price_sold for sale in last_year_sales])
    return last_year_sales_total


def basket_delete_all(request):
    user_basket = Basket.objects.get(basket_user=request.user)

    user_basket.basket_product.clear()
    return redirect('Akala:basket_show')
