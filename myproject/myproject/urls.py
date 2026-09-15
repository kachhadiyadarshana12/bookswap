"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from myapp.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # home page
    path("", index, name="index"),
    path("browse", browse, name="browse"),
    path("sell_book_detail/<int:book_id>/", sell_book_detail, name="sell_book_detail"),
    path("sell_book/<int:book_id>/buy/", buy_book, name="buy_book"),
    path("checkout/<int:book_id>/", checkout, name="checkout"),
    path("exchange", exchange, name="exchange"),
    path("how_it_works", how_it_works, name="how_it_works"),
    path("notifications", notifications, name="notifications"),
    path(
        "notifications/<int:notification_id>/open/",
        open_notification,
        name="open_notification",
    ),
    path(
        "notifications/<int:notification_id>/<str:action>/",
        update_notification,
        name="update_notification",
    ),
    # user profile
    path("user_profile", user_profile, name="user_profile"),
    path("orders/<int:order_id>/cancel/", cancel_order, name="cancel_order"),
    path("profile/edit", edit_profile, name="edit_profile"),
    path("wishlist/add", add_to_wishlist, name="add_to_wishlist"),
    path(
        "wishlist/<int:wishlist_id>/remove",
        remove_from_wishlist,
        name="remove_from_wishlist",
    ),
    path(
        "exchange/<int:exchange_id>/request",
        create_exchange_request,
        name="create_exchange_request",
    ),
    path("exchange-request/<int:request_id>/chat", exchange_chat, name="exchange_chat"),
    path(
        "exchange-request/<int:request_id>/<str:status>",
        exchange_request_status,
        name="exchange_request_status",
    ),
    # footer files
    path("about/", about_us, name="about_us"),
    path("help/", help_center, name="help_center"),
    path(
        "help/contact/",
        create_user_support_ticket,
        name="create_user_support_ticket",
    ),
    path(
        "help/ticket/<int:ticket_id>/",
        user_support_ticket_detail,
        name="user_support_ticket_detail",
    ),
    path(
        "help/ticket/<int:ticket_id>/edit/",
        edit_user_support_ticket,
        name="edit_user_support_ticket",
    ),
    path(
        "help/ticket/<int:ticket_id>/delete/",
        delete_user_support_ticket,
        name="delete_user_support_ticket",
    ),
    path("terms-privacy/", terms_privacy, name="terms_privacy"),
    # login-registration
    path("registration", registration, name="registration"),
    path("login", login, name="login"),
    path("logout", logout, name="logout"),
    # seller
    path("seller_profile", seller_profile, name="seller_profile"),
    path("seller/orders/", seller_orders, name="seller_orders"),
    path(
        "seller/orders/<int:order_id>/update/",
        seller_update_order,
        name="seller_update_order",
    ),
    # seller add book crud
    path("all_sell_books", all_sell_books, name="all_sell_books"),
    path("all_exchange_books", all_exchange_books, name="all_exchange_books"),
    path("seller_add_book", seller_add_book, name="seller_add_book"),
    path("seller_add_option", seller_add_option, name="seller_add_option"),
    path("seller_edit_book/<int:id>/", seller_edit_book, name="seller_edit_book"),
    path("seller_delete_book/<int:id>/", seller_delete_book, name="seller_delete_book"),
    # seller support
    path("seller_support/", seller_support, name="seller_support"),
    path(
        "seller_support/create/",
        seller_create_support_ticket,
        name="seller_create_support_ticket",
    ),
    path(
        "seller_support/ticket/<int:ticket_id>/",
        seller_support_ticket_detail,
        name="seller_support_ticket_detail",
    ),
    # exchange
    path(
        "seller_add_exchange",
        seller_add_exchange,
        name="seller_add_exchange",
    ),
    path(
        "seller_exchange_condition/<int:book_id>/",
        seller_exchange_condition,
        name="seller_exchange_condition",
    ),
    path(
        "seller_exchange_photos/<int:book_id>/",
        seller_exchange_photos,
        name="seller_exchange_photos",
    ),
    path(
        "seller_exchange_photo_delete/<int:book_id>/<int:photo_id>/",
        seller_exchange_photo_delete,
        name="seller_exchange_photo_delete",
    ),
    path(
        "seller_exchange_pricing/<int:book_id>/",
        seller_exchange_pricing,
        name="seller_exchange_pricing",
    ),
    path(
        "seller_exchange_delivery/<int:book_id>/",
        seller_exchange_delivery,
        name="seller_exchange_delivery",
    ),
    path(
        "seller_exchange_review/<int:book_id>/",
        seller_exchange_review,
        name="seller_exchange_review",
    ),
    path(
        "seller_edit_exchange/<int:exchange_id>/",
        seller_edit_exchange,
        name="seller_edit_exchange",
    ),
    path(
        "seller_delete_exchange/<int:exchange_id>/",
        seller_delete_exchange,
        name="seller_delete_exchange",
    ),
    # client side
    path("client_exchange_books", client_exchange_books, name="client_exchange_books"),
    path(
        "client_exchange_book_detail/<int:exchange_id>/",
        client_exchange_book_detail,
        name="client_exchange_book_detail",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
