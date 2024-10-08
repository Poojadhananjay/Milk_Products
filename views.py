# from urllib import request
from datetime import date
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
import razorpay
from . models import Customer, Product, Cart, Payment, OrderPlaced
from . forms import CustomerProfileForm, CustomerRegistrationForm
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Q
from django.conf import settings

# Create your views here.
def home(request):
    return render(request,'home.html')

def about(request):
    return render(request,'about.html')


def contact(request):
    return render(request,'contact.html')

def Logout(request):
    logout(request)
    messages.success(request,"Logout Success")    
    return redirect('home')


class CategoryView(View):
    def get(self,request,val):
       product = Product.objects.filter(category=val)
       title = Product.objects.filter(category=val).values('title').annotate(total=Count('title'))
       return render(request,"category.html",locals())
    
class CategoryTitle(View):
    def get(self, request, val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request, "category.html",locals())  
   
class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        return render(request,"productdetail.html",locals())
    
class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request,"customerregistration.html",locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Successfully Registered")
        else:
            messages.warning(request,"Invalid Data")    
        return render(request,"customerregistration.html",locals())
    
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'profile.html',locals())
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name =  form.cleaned_data['name']
            locality =  form.cleaned_data['locality']
            city  = form.cleaned_data['city']
            mobile  = form.cleaned_data['mobile']
            state =  form.cleaned_data['state']
            zipcode  = form.cleaned_data['zipcode']
            reg  = Customer(user=user, name=name, locality=locality, mobile=mobile, city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(request, "Congratulations! Profile Save Successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return render(request, 'profile.html',locals())

def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'address.html',locals())
        


class Update(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'update.html', locals())
    def post(self, request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Congratulations! Profile Update Successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return redirect("address")


    
def add_to_cart(request):
    user=request.user
    product_id=request.GET.get('prod_id')
    product= Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect("/cart")

def show_cart(request):
    user =request.user
    cart= Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value= p.quantity * p.product.discounted_price
        amount= amount + value
        totalamount = amount + 40
    return render(request, 'addtocart.html',locals())

class checkout(View):
    def get(self,request):
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items =Cart.objects.filter(user=user)
        famount=0
        for p in cart_items:
            value= p.quantity* p.product.discounted_price
            famount= famount +value
        totalamount= famount + 40
        razoramount= int(totalamount * 100)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = {"amount": razoramount, "currency":"INR", "receipt":"order_reptid_11"}
        payment_response = client.order.create(data=data)
        print(payment_response)
        # {'amount': 1054000, 'amount_due': 1054000, 'amount_paid': 0, 'attempts': 0, 'created_at': 1721625464, 'currency': 'INR', 'entity': 'order', 'id': 'order_ObYkycKkSUTPWM', 'notes': [], 'offer_id': None, 'receipt': 'order_reptid_11', 'status': 'created'}
        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
            payment = Payment(
                user=user, 
                amount=totalamount,
                razorpay_order_id=order_id, 
                razorpay_payment_status =order_status
            )
            payment.save()

        return render(request, 'checkout.html',locals())
    
def payment_done(request):
    order_id=request.GET.get('order_id')
    payment_id= request.GET.get('payment_id')
    cust_id=request.GET.get('cust_id')
    #print("payment_done: oid",order_id," pid",payment_id," cid",cust_id)
    user=request.user
    #return redirect("orders")
    customer=Customer.objects.get(id=cust_id)
    #To update payment status and payment id
    payment=Payment.objects.get(razorpay_order_id=order_id)
    payment.paid=True
    payment.razorpay_payment_id = payment_id
    payment.save()
    #To save order details
    cart=Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, product=c.product,quantity=c.quantity,payment=payment).save()
        c.delete()
    return redirect("orders")    


def orders(request):
    Order_placed=OrderPlaced.objects.filter(user=request.user)
    return render(request, 'orders.html',locals())

    

def plus_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c =  Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1 
        c.save()
        User = request.user
        cart = Cart.objects.filter(user=User)
        amount = 0
        for p in cart:
            value= p.quantity * p.product.discounted_price
            amount= amount + value
        totalamount = amount + 40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
            }
        return JsonResponse(data)

           
