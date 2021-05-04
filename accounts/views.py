from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib import messages
# Create your views here.
from .models import *
from .forms import OrderForm, CreateUserForm
from .filters import OrderFilter




def registerPage(request):
    if request.user.is_authenticated:
        return redirect('login')
    else:    
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)
                return redirect('login')


    context = {'form':form}
    return render(request, 'accounts/register.html', context)


def logingPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:    
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username Or password is incorrect')


    context = {}
    return render(request, 'accounts/login.html', context)
            
def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):
    orders = order.objects.all()
    customers = customer.objects.all()
    total_orders = orders.count()
    total_cus = customers.count()
    delevred = orders.filter(status='Delivered').count()
    Pending = orders.filter(status='Pending').count()
    context = {'orders': orders, 'customers': customers,
    'delevred':delevred, 'Pending': Pending, 'total_orders': total_orders,
    'total_cus': total_cus}
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
def Products(request):
    Pr = products.objects.all()
    return render(request, 'accounts/products.html', {'Pr': Pr})

@login_required(login_url='login')
def Customers(request, pk):
    Customer = customer.objects.get(id=pk)
    orders = Customer.order_set.all()
    nb = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    context ={'Customer':Customer, 'orders':orders, 'nb': nb, 'myFilter':myFilter}
    return render(request, 'accounts/customer.html', context)

@login_required(login_url='login')
def create_order(request, pk):
    OrderFormSet = inlineformset_factory(customer, order, fields=('product', 'status'), extra=10)
    cus = customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=order.objects.none(), instance=cus)
    # form = OrderForm(initial={'cus': cus})
    if request.method == 'POST':
       # print('Printing POST', request.POST)
       #form = OrderForm(request.POST)
       formset = OrderFormSet(request.POST, instance=cus)
       if formset.is_valid():
            formset.save()
            return redirect('/') 
    context = {'formset': formset}
    return render(request, 'accounts/orders_form.html', context)

@login_required(login_url='login')
def updateOrder(request, pk):
    Order = order.objects.get(id=pk)
    form = OrderForm(instance=Order)
    if request.method == 'POST':
       form = OrderForm(request.POST, instance=Order)
       if form.is_valid():
            form.save()
            return redirect('/') 
    context = {'form':form}
    return render(request, 'accounts/orders_form.html', context)


@login_required(login_url='login')
def deleteOrder(request, pk):
    Order = order.objects.get(id=pk)
    if request.method == 'POST':
        Order.delete()
        return redirect('/')
    context = {'item':Order}
    return render(request, 'accounts/delete.html', context)
 