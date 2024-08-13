
from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view
from . forms import LoginForm,  MyPasswordChangeForm

urlpatterns = [
    path("", views.home,name="home"),
    path("about/", views.about,name="about"),
    path("contact/", views.contact,name="contact"),
    path("category/<slug:val>", views.CategoryView.as_view(),name="category"),
    path("category-title/<val>", views.CategoryTitle.as_view(),name="category-title"),
    path("productdetail/<int:pk>", views.ProductDetail.as_view(),name="productdetail"),
    path("profile/", views.ProfileView.as_view(),name="profile"),
    path("address/", views.address,name="address"),
    path("update/<int:pk>", views.Update.as_view(),name="update"),
    path("add-to-cart/", views.add_to_cart,name="add-to-cart"),
    path("cart/", views.show_cart,name="showcart"),
    path("checkout/", views.checkout.as_view(),name="checkout"),
    path("pluscart/", views.plus_cart,name="pluscart"),
    path("paymentdone/", views.payment_done,name="paymentdone"),
    path("orders/", views.home,name="orders"),
    


    # authentication urls
    path("customerregistration", views.CustomerRegistrationView.as_view(),name='customerregistration'),
    path("login", auth_view.LoginView.as_view(template_name='login.html', authentication_form=LoginForm), name='login'),
    path("logout/", views.Logout,name="logout"),
   
    
    path('passwordchange/', auth_view.PasswordChangeView.as_view(template_name='changepassword.html', form_class=MyPasswordChangeForm, success_url='/passwordchangedone'), name='passwordchange'),
    

    

    ]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
