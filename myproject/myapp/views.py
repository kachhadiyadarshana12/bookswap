from decimal import Decimal, InvalidOperation
from functools import wraps
import re
from django.db import transaction
from django.db.models import Q, Sum
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from myapp.models import *
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.utils.text import slugify
from django.utils import timezone


def book_category_choices():
    choices = list(BookCategory.objects.values_list("code", "name"))
    return choices or Book.CATEGORY_CHOICES


def book_language_choices():
    choices = list(BookLanguage.objects.values_list("code", "name"))
    return choices or Book.LANGUAGE_CHOICES


def create_offer_notifications(book):
    if book.status != "published" or not book.offer_percentage:
        return

    users = User.objects.filter(is_active=True).exclude(id=book.seller.user_id)
    Notification.objects.bulk_create(
        [Notification(user=user, book=book) for user in users],
        ignore_conflicts=True,
    )


@login_required
def seller_add_option(request):
    if request.method != "POST":
        return redirect("seller_add_book")

    option_type = request.POST.get("option_type", "").strip()
    field_name = (
        "category_option_name" if option_type == "category" else "language_option_name"
    )
    name = request.POST.get(field_name, "").strip()
    model = (
        BookCategory
        if option_type == "category"
        else BookLanguage if option_type == "language" else None
    )

    if model is None or not name:
        messages.error(
            request, "Enter a valid category or language name.", extra_tags="catalog"
        )
    elif len(name) > 50:
        messages.error(
            request, "Name cannot exceed 50 characters.", extra_tags="catalog"
        )
    elif model.objects.filter(name__iexact=name).exists():
        messages.error(request, "This option already exists.", extra_tags="catalog")
    else:
        code = slugify(name) if option_type == "category" else name
        if model.objects.filter(code__iexact=code).exists():
            messages.error(request, "This option already exists.", extra_tags="catalog")
        else:
            model.objects.create(code=code, name=name)
            messages.success(
                request, f"{name} added successfully.", extra_tags="catalog"
            )

    return redirect(request.META.get("HTTP_REFERER") or "seller_add_book")


# Create your views here
# login & registration


def registration(request):

    if request.method == "POST":

        role = request.POST.get("role", "").strip()
        full_name = request.POST.get("full_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        location = request.POST.get("location", "").strip()

        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        profile_photo = request.FILES.get("profile_photo")

        store_name = request.POST.get("store_name", "").strip()
        seller_description = request.POST.get("seller_description", "").strip()

        terms = request.POST.get("terms")

        # FORM DATA FOR ERROR

        context = {
            "role": role,
            "full_name": full_name,
            "username": username,
            "email": email,
            "phone": phone,
            "location": location,
            "store_name": store_name,
            "seller_description": seller_description,
        }

        # BASIC VALIDATION

        if not role:
            context["error"] = "Please select a role."
            return render(request, "registration.html", context)

        if role not in ["reader", "seller"]:
            context["error"] = "Invalid role selected."
            return render(request, "registration.html", context)

        if not full_name:
            context["error"] = "Full Name is required."
            return render(request, "registration.html", context)

        if not username:
            context["error"] = "Username is required."
            return render(request, "registration.html", context)

        if not email:
            context["error"] = "Email is required."
            return render(request, "registration.html", context)

        if not phone:
            context["error"] = "Phone Number is required."
            return render(request, "registration.html", context)

        if not location:
            context["error"] = "Location is required."
            return render(request, "registration.html", context)

        if not password:
            context["error"] = "Password is required."
            return render(request, "registration.html", context)

        if not confirm_password:
            context["error"] = "Confirm Password is required."
            return render(request, "registration.html", context)

        if not profile_photo:
            context["error"] = "Profile Photo is required."
            return render(request, "registration.html", context)

        if not terms:
            context["error"] = "Please accept Terms and Privacy Policy."
            return render(request, "registration.html", context)

        # SELLER VALIDATION

        if role == "seller":

            if not store_name:
                context["error"] = "Store Name is required."
                return render(request, "registration.html", context)

            if not seller_description:
                context["error"] = "Store Description is required."
                return render(request, "registration.html", context)

        # EMAIL VALIDATION

        try:
            validate_email(email)

        except ValidationError:
            context["error"] = "Enter a valid email address."
            return render(request, "registration.html", context)

        # USERNAME CHECK

        if User.objects.filter(username__iexact=username).exists():

            context["error"] = "Username already exists."
            return render(request, "registration.html", context)

        # EMAIL CHECK

        if User.objects.filter(email__iexact=email).exists():

            context["error"] = "Email already exists."
            return render(request, "registration.html", context)

        # PHONE VALIDATION

        if not phone.isdigit():

            context["error"] = "Phone number must contain only numbers."
            return render(request, "registration.html", context)

        if len(phone) != 10:

            context["error"] = "Phone number must be exactly 10 digits."
            return render(request, "registration.html", context)

        # PASSWORD VALIDATION

        if password != confirm_password:

            context["error"] = "Password and Confirm Password do not match."
            return render(request, "registration.html", context)

        if len(password) < 8:

            context["error"] = "Password must contain at least 8 characters."
            return render(request, "registration.html", context)

        # CREATE USER

        user = User.objects.create_user(
            username=username, email=email, password=password
        )

        if role == "reader":

            readerprofile.objects.create(
                user=user,
                full_name=full_name,
                profile_photo=profile_photo,
                phone=phone,
                location=location,
            )

        elif role == "seller":

            sellerprofile.objects.create(
                user=user,
                full_name=full_name,
                profile_photo=profile_photo,
                phone=phone,
                location=location,
                store_name=store_name,
                seller_description=seller_description,
            )

        messages.success(request, "Registration successful! Please login.")

        return redirect("login")

    return render(request, "registration.html")


# hasattr() built-in function, It checks whether an object has a particular attribute.,hasattr(user, 'reader_profile') check in model ....


def login(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username:
            messages.error(request, "Please enter username.")
            return render(request, "login.html")

        if not password:
            messages.error(request, "Please enter password.")
            return render(request, "login.html")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password.")
            return render(request, "login.html")

        # Login user
        auth_login(request, user)

        # ==========================
        # ADMIN
        # ==========================

        if user.is_superuser:
            return redirect("/admin/")

        # ==========================
        # SELLER
        # ==========================

        if hasattr(request.user, "seller_profile"):
            return redirect("seller_profile")

        # ==========================
        # READER / USER
        # ==========================

        if hasattr(request.user, "reader_profile"):
            return redirect("user_profile")

        # ==========================
        # PROFILE NOT FOUND
        # ==========================

        messages.error(request, "Profile not found. Please contact administrator.")

        auth_logout(request)

        return render(request, "login.html")

    return render(request, "login.html")


def logout(request):

    auth_logout(request)

    messages.success(request, "You have been logged out successfully.")

    return redirect("index")


# reader_required
def reader_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        # Admin
        if request.user.is_superuser:
            return redirect("/admin/")

        # Seller cannot access reader side
        if hasattr(request.user, "seller_profile"):
            return redirect("seller_profile")

        # Reader allowed
        if hasattr(request.user, "reader_profile"):
            return view_func(request, *args, **kwargs)

        return redirect("login")

    return wrapper


#
def seller_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        # Admin
        if request.user.is_superuser:
            return redirect("/admin/")

        # Reader cannot access seller side
        if hasattr(request.user, "reader_profile"):
            return redirect("index")

        # Seller allowed
        if hasattr(request.user, "seller_profile"):
            return view_func(request, *args, **kwargs)

        return redirect("login")

    return wrapper


#  user side pages
def index(request):
    exchange_books = (
        ExchangeBook.objects.select_related("book", "seller")
        .prefetch_related("photos")
        .filter(status="published", book__status="published")
        .order_by("-created_at")[:4]
    )
    sale_books = (
        Book.objects.select_related("seller")
        .filter(status="published", price__isnull=False, offer_percentage__isnull=True)
        .order_by("-created_at")[:5]
    )
    offer_books = (
        Book.objects.select_related("seller")
        .filter(
            status="published",
            price__isnull=False,
            offer_percentage__gt=0,
        )
        .order_by("-created_at")[:5]
    )
    return render(
        request,
        "index.html",
        {
            "exchange_books": exchange_books,
            "sale_books": sale_books,
            "offer_books": offer_books,
        },
    )


@login_required
def notifications(request):
    user_notifications = Notification.objects.select_related("book", "book__seller").filter(
        user=request.user, is_removed=False
    )
    return render(request, "notifications.html", {"notifications": user_notifications})


@login_required
def open_notification(request, notification_id):
    notification = get_object_or_404(
        Notification, id=notification_id, user=request.user, is_removed=False
    )
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return redirect("sell_book_detail", book_id=notification.book_id)


@login_required
def update_notification(request, notification_id, action):
    notification = get_object_or_404(
        Notification, id=notification_id, user=request.user
    )
    if action == "remove":
        notification.is_removed = True
        notification.is_read = True
        notification.save(update_fields=["is_removed", "is_read"])
    elif action == "read":
        notification.is_read = True
        notification.save(update_fields=["is_read"])
    return redirect("notifications")


def browse(request):
    search = request.GET.get("search", "").strip()
    category = request.GET.get("category", "").strip()
    language = request.GET.get("language", "").strip()
    sort = request.GET.get("sort", "recommended").strip()

    books = Book.objects.select_related("seller").filter(
        status="published", price__isnull=False
    )

    if search:
        books = books.filter(
            Q(title__icontains=search)
            | Q(author__icontains=search)
            | Q(isbn__icontains=search)
            | Q(publisher__icontains=search)
        )

    if category:
        books = books.filter(category=category)

    if language:
        books = books.filter(language=language)

    if sort == "offer":
        books = books.filter(offer_percentage__gt=0).order_by(
            "-offer_percentage", "-created_at"
        )
    elif sort == "newest":
        books = books.order_by("-created_at")
    elif sort == "price_low":
        books = books.order_by("id")
    elif sort == "price_high":
        books = books.order_by("-id")
    else:
        books = books.order_by("-created_at")

    paginator = Paginator(books, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "browse.html",
        {
            "books": page_obj,
            "page_obj": page_obj,
            "book_count": paginator.count,
            "search": search,
            "selected_category": category,
            "selected_language": language,
            "selected_sort": sort,
            "category_choices": book_category_choices(),
            "language_choices": book_language_choices(),
        },
    )


def sell_book_detail(request, book_id):
    book = get_object_or_404(
        Book.objects.select_related("seller"),
        id=book_id,
        status="published",
        price__isnull=False,
    )
    in_wishlist = (
        request.user.is_authenticated
        and Wishlist.objects.filter(user=request.user, book=book).exists()
    )
    return render(
        request,
        "sell_book_detail.html",
        {"book": book, "seller": book.seller, "in_wishlist": in_wishlist},
    )


@login_required
def buy_book(request, book_id):
    book = get_object_or_404(Book.objects.select_related("seller__user"), id=book_id)
    if book.seller.user_id == request.user.id:
        messages.error(request, "You cannot buy your own book.")
        return redirect("sell_book_detail", book_id=book.id)
    if book.price is None:
        messages.error(request, "This book is not available for purchase yet.")
        return redirect("sell_book_detail", book_id=book.id)

    existing_order = (
        BookOrder.objects.filter(book=book, buyer=request.user)
        .exclude(status="cancelled")
        .first()
    )
    if existing_order:
        messages.info(
            request, f"You already placed order #{existing_order.id} for this book."
        )
        return redirect("user_profile")

    amount = book.offer_price if book.offer_percentage is not None else book.price
    if request.method == "GET":
        return render(request, "checkout.html", {"book": book, "amount": amount})

    recipient_name = request.POST.get("recipient_name", "").strip()
    recipient_phone = request.POST.get("recipient_phone", "").strip()
    address_line1 = request.POST.get("address_line1", "").strip()
    address_line2 = request.POST.get("address_line2", "").strip()
    city = request.POST.get("city", "").strip()
    state = request.POST.get("state", "").strip()
    postal_code = request.POST.get("postal_code", "").strip()

    text_pattern = r"^[A-Za-z][A-Za-z .'-]*$"
    validation_errors = []
    if not recipient_name:
        validation_errors.append("Full name is required.")
    elif (
        not re.fullmatch(text_pattern, recipient_name)
        or not 2 <= len(recipient_name) <= 100
    ):
        validation_errors.append(
            "Enter a valid full name using letters and spaces only."
        )
    if not re.fullmatch(r"[0-9]{10}", recipient_phone):
        validation_errors.append("Phone number must contain exactly 10 digits.")
    if not address_line1 or not 5 <= len(address_line1) <= 200:
        validation_errors.append("Address must be between 5 and 200 characters.")
    if len(address_line2) > 200:
        validation_errors.append("Address line 2 cannot exceed 200 characters.")
    if not re.fullmatch(text_pattern, city) or not 2 <= len(city) <= 80:
        validation_errors.append("Enter a valid city name.")
    if not re.fullmatch(text_pattern, state) or not 2 <= len(state) <= 80:
        validation_errors.append("Enter a valid state name.")
    if not re.fullmatch(r"[0-9]{6}", postal_code):
        validation_errors.append("Postal code must contain exactly 6 digits.")

    if validation_errors:
        messages.error(request, " ".join(validation_errors))
        return render(request, "checkout.html", {"book": book, "amount": amount})

    payment_method = request.POST.get("payment_method", "").strip()
    if payment_method not in {"cash", "online"}:
        messages.error(request, "Select a valid payment method.")
        return render(request, "checkout.html", {"book": book, "amount": amount})

    payment_confirmed = request.POST.get("payment_confirmed") == "1"
    if payment_method == "online" and not payment_confirmed:
        messages.error(request, "Confirm the online payment before placing the order.")
        return render(request, "checkout.html", {"book": book, "amount": amount})

    order = BookOrder.objects.create(
        book=book,
        buyer=request.user,
        amount=amount,
        payment_method=payment_method,
        payment_status="paid" if payment_method == "online" else "pending",
        recipient_name=recipient_name,
        recipient_phone=recipient_phone,
        address_line1=address_line1,
        address_line2=address_line2,
        city=city,
        state=state,
        postal_code=postal_code,
    )
    if payment_method == "cash":
        messages.success(
            request, f"Order #{order.id} placed. Pay cash when the book is delivered."
        )
    else:
        messages.success(
            request, f"Payment successful. Order #{order.id} has been placed."
        )
    return redirect("user_profile")


@login_required
def checkout(request, book_id):
    return buy_book(request, book_id)


def exchange(request):
    search = request.GET.get("search", "").strip()
    category = request.GET.get("category", "").strip()
    language = request.GET.get("language", "").strip()
    condition = request.GET.get("condition", "").strip()
    sort = request.GET.get("sort", "relevant").strip()

    exchange_books = (
        ExchangeBook.objects.filter(status="published")
        .select_related("book", "seller")
        .prefetch_related("photos")
    )

    if search:
        exchange_books = exchange_books.filter(
            Q(book__title__icontains=search)
            | Q(book__author__icontains=search)
            | Q(book__isbn__icontains=search)
            | Q(book__publisher__icontains=search)
        )

    if category:
        exchange_books = exchange_books.filter(book__category=category)

    if language:
        exchange_books = exchange_books.filter(book__language=language)

    if condition:
        exchange_books = exchange_books.filter(condition=condition)

    if sort == "price_low":
        exchange_books = exchange_books.order_by("selling_price", "-created_at")
    elif sort == "price_high":
        exchange_books = exchange_books.order_by("-selling_price", "-created_at")
    else:
        exchange_books = exchange_books.order_by("-created_at")

    return render(
        request,
        "exchange.html",
        {
            "exchange_books": exchange_books,
            "search": search,
            "selected_category": category,
            "selected_language": language,
            "selected_condition": condition,
            "selected_sort": sort,
            "category_choices": book_category_choices(),
            "language_choices": book_language_choices(),
            "condition_choices": ExchangeBook.CONDITION_CHOICES,
        },
    )


@login_required
@reader_required
def user_profile(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related(
        "book__seller", "exchange_book__book__seller", "exchange_book"
    )
    profile = getattr(request.user, "reader_profile", None) or getattr(
        request.user, "seller_profile", None
    )
    sent_requests = ExchangeRequest.objects.filter(
        requester=request.user
    ).select_related(
        "exchange_book__book", "exchange_book__seller__user", "offered_book"
    )
    received_requests = ExchangeRequest.objects.filter(
        exchange_book__seller__user=request.user
    ).select_related("exchange_book__book", "requester", "offered_book")
    my_exchange_books = (
        ExchangeBook.objects.filter(seller__user=request.user)
        .select_related("book")
        .prefetch_related("photos")
    )
    orders = BookOrder.objects.filter(buyer=request.user).select_related(
        "book", "book__seller"
    )
    return render(
        request,
        "user_profile.html",
        {
            "wishlist_items": wishlist_items,
            "profile": profile,
            "sent_requests": sent_requests,
            "received_requests": received_requests,
            "my_exchange_books": my_exchange_books,
            "orders": orders,
        },
    )


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(BookOrder, id=order_id, buyer=request.user)
    if request.method != "POST":
        return redirect("user_profile")

    if order.status == "cancelled":
        messages.info(request, f"Order #{order.id} is already cancelled.")
    elif order.delivery_status != "pending":
        messages.error(
            request,
            "This order cannot be cancelled because packing or delivery has started.",
        )
    elif timezone.now() > order.cancellation_deadline:
        messages.error(
            request,
            "Cancellation is available only within 3 days of placing the order.",
        )
    else:
        reason = request.POST.get("cancellation_reason", "").strip()
        if not reason:
            messages.error(request, "Please provide a reason for cancelling the order.")
        elif len(reason) > 500:
            messages.error(request, "Cancellation reason cannot exceed 500 characters.")
        else:
            order.status = "cancelled"
            order.cancelled_at = timezone.now()
            order.cancellation_reason = reason
            order.refund_status = (
                "pending" if order.payment_method == "online" else "not_applicable"
            )
            order.save(
                update_fields=[
                    "status",
                    "cancelled_at",
                    "cancellation_reason",
                    "refund_status",
                    "updated_at",
                ]
            )
            messages.success(
                request,
                f"Order #{order.id} cancelled. "
                + (
                    "Your online refund will be processed in 5–7 business days."
                    if order.payment_method == "online"
                    else "No refund is required for cash on delivery."
                ),
            )
    return redirect("user_profile")


@login_required
def edit_profile(request):
    profile = getattr(request.user, "reader_profile", None) or getattr(
        request.user, "seller_profile", None
    )
    if profile is None:
        messages.error(request, "Profile not found.")
        return redirect("user_profile")

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        location = request.POST.get("location", "").strip()
        photo = request.FILES.get("profile_photo")

        if not full_name:
            messages.error(request, "Full name is required.")
        elif not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Phone number must be exactly 10 digits.")
        elif not location:
            messages.error(request, "Address or city is required.")
        else:
            profile.full_name = full_name
            profile.phone = phone
            profile.location = location
            if photo:
                profile.profile_photo = photo
            profile.save()
            messages.success(request, "Profile and contact details updated.")
            if hasattr(request.user, "seller_profile"):
                return redirect("seller_profile")
            return redirect("user_profile")

    return render(request, "edit_profile.html", {"profile": profile})


@login_required
def add_to_wishlist(request):
    if request.method != "POST":
        return redirect("user_profile")

    book_id = request.POST.get("book_id")
    exchange_id = request.POST.get("exchange_id")
    if bool(book_id) == bool(exchange_id):
        messages.error(request, "Select one valid book to add to your wishlist.")
    elif book_id:
        book = get_object_or_404(Book, id=book_id)
        Wishlist.objects.get_or_create(user=request.user, book=book)
        messages.success(request, "Book added to your wishlist.")
    else:
        exchange_book = get_object_or_404(
            ExchangeBook, id=exchange_id, status="published"
        )
        Wishlist.objects.get_or_create(user=request.user, exchange_book=exchange_book)
        messages.success(request, "Exchange book added to your wishlist.")

    return redirect(request.POST.get("next") or "user_profile")


@login_required
def remove_from_wishlist(request, wishlist_id):
    if request.method == "POST":
        Wishlist.objects.filter(id=wishlist_id, user=request.user).delete()
        messages.success(request, "Removed from your wishlist.")
    return redirect(request.POST.get("next") or "user_profile")


def get_exchange_request_for_user(request, request_id):
    return get_object_or_404(
        ExchangeRequest.objects.select_related(
            "exchange_book__book",
            "exchange_book__seller__user",
            "requester",
            "offered_book",
        ),
        Q(id=request_id)
        & (Q(requester=request.user) | Q(exchange_book__seller__user=request.user)),
    )


@login_required
def create_exchange_request(request, exchange_id):
    exchange_book = get_object_or_404(
        ExchangeBook.objects.select_related("book", "seller__user"),
        id=exchange_id,
        status="published",
    )
    if request.method != "POST":
        return redirect("client_exchange_book_detail", exchange_id=exchange_id)
    if exchange_book.seller.user_id == request.user.id:
        messages.error(request, "You cannot request your own exchange book.")
        return redirect("client_exchange_book_detail", exchange_id=exchange_id)

    offered_book = Book.objects.filter(
        id=request.POST.get("offered_book"),
        seller__user=request.user,
        exchange_details__status="published",
    ).first()
    if offered_book is None:
        messages.error(
            request,
            "Choose one of your published exchange books before sending the request.",
        )
        return redirect("client_exchange_book_detail", exchange_id=exchange_id)
    exchange_request, created = ExchangeRequest.objects.get_or_create(
        exchange_book=exchange_book,
        requester=request.user,
        defaults={
            "offered_book": offered_book,
            "note": request.POST.get("note", "").strip(),
        },
    )
    if not created:
        if exchange_request.status in {"rejected", "cancelled"}:
            exchange_request.status = "pending"
            exchange_request.offered_book = offered_book
            exchange_request.note = request.POST.get("note", "").strip()
            exchange_request.save(
                update_fields=["status", "offered_book", "note", "updated_at"]
            )
        else:
            messages.info(request, "You already have an active request for this book.")
            return redirect("exchange_chat", request_id=exchange_request.id)
    messages.success(request, "Exchange request sent to the book owner.")
    return redirect("exchange_chat", request_id=exchange_request.id)


@login_required
def exchange_request_status(request, request_id, status):
    exchange_request = get_exchange_request_for_user(request, request_id)
    if request.method != "POST":
        return redirect("exchange_chat", request_id=request_id)
    if status not in {"accepted", "rejected", "cancelled"}:
        messages.error(request, "Invalid exchange request status.")
    elif (
        status in {"accepted", "rejected"}
        and exchange_request.exchange_book.seller.user_id != request.user.id
    ):
        messages.error(
            request, "Only the exchange book owner can accept or reject requests."
        )
    elif status == "cancelled" and exchange_request.requester_id != request.user.id:
        messages.error(request, "Only the requester can cancel this request.")
    else:
        exchange_request.status = status
        exchange_request.save(update_fields=["status", "updated_at"])
        messages.success(request, f"Exchange request marked {status}.")
    return redirect("exchange_chat", request_id=request_id)


@login_required
def exchange_chat(request, request_id):
    exchange_request = get_exchange_request_for_user(request, request_id)
    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        if not body:
            messages.error(request, "Message cannot be empty.")
        elif len(body) > 2000:
            messages.error(request, "Message cannot exceed 2000 characters.")
        else:
            ExchangeMessage.objects.create(
                exchange_request=exchange_request, sender=request.user, body=body
            )
            return redirect("exchange_chat", request_id=request_id)
    other_user = (
        exchange_request.exchange_book.seller.user
        if exchange_request.requester_id == request.user.id
        else exchange_request.requester
    )
    other_profile = getattr(other_user, "reader_profile", None) or getattr(
        other_user, "seller_profile", None
    )
    return render(
        request,
        "exchange_chat.html",
        {
            "exchange_request": exchange_request,
            "chat_messages": exchange_request.messages.select_related("sender"),
            "is_owner": exchange_request.exchange_book.seller.user_id
            == request.user.id,
            "other_profile": other_profile,
            "contact_shared": exchange_request.status == "accepted",
        },
    )


# seller


@login_required
def seller_profile(request):
    seller = get_object_or_404(sellerprofile, user=request.user)
    books = Book.objects.filter(seller=seller).order_by("-created_at")
    orders = BookOrder.objects.filter(book__seller=seller).select_related(
        "book", "buyer"
    )
    received_requests = ExchangeRequest.objects.filter(
        exchange_book__seller=seller
    ).select_related("exchange_book__book", "requester", "offered_book")
    exchange_books = ExchangeBook.objects.filter(seller=seller).select_related("book")
    paid_revenue = (
        orders.filter(payment_status="paid").aggregate(total=Sum("amount"))["total"]
        or 0
    )
    pending_orders = (
        orders.exclude(status="cancelled").exclude(delivery_status="delivered").count()
    )
    delivered_orders = orders.filter(delivery_status="delivered").count()
    return render(
        request,
        "seller/seller_profile.html",
        {
            "seller": seller,
            "books": books[:6],
            "book_count": books.count(),
            "exchange_books": exchange_books,
            "exchange_count": exchange_books.count(),
            "received_requests": received_requests[:6],
            "request_count": received_requests.count(),
            "orders": orders[:6],
            "order_count": orders.count(),
            "paid_revenue": paid_revenue,
            "pending_orders": pending_orders,
            "delivered_orders": delivered_orders,
        },
    )


@login_required
def seller_orders(request):
    orders = BookOrder.objects.filter(book__seller__user=request.user).select_related(
        "book", "buyer"
    )
    return render(
        request,
        "seller/orders.html",
        {
            "orders": orders,
            "delivery_status_choices": BookOrder.DELIVERY_STATUS_CHOICES,
        },
    )


@login_required
def seller_update_order(request, order_id):
    order = get_object_or_404(BookOrder, id=order_id, book__seller__user=request.user)
    if request.method == "POST":
        if order.status == "cancelled":
            messages.error(request, f"Cancelled order #{order.id} cannot be updated.")
            return redirect("seller_orders")
        delivery_status = request.POST.get("delivery_status", "").strip()
        payment_status = request.POST.get("payment_status", "").strip()
        if delivery_status not in dict(
            BookOrder.DELIVERY_STATUS_CHOICES
        ) or payment_status not in dict(BookOrder.PAYMENT_STATUS_CHOICES):
            messages.error(request, "Select valid payment and delivery statuses.")
        elif order.delivery_status != "pending" and delivery_status == "pending":
            messages.error(request, "A started delivery cannot be moved back to pending.")
        else:
            order.delivery_status = delivery_status
            order.payment_status = payment_status
            order.tracking_reference = request.POST.get(
                "tracking_reference", ""
            ).strip()
            order.delivery_note = request.POST.get("delivery_note", "").strip()
            order.save(
                update_fields=[
                    "delivery_status",
                    "payment_status",
                    "tracking_reference",
                    "delivery_note",
                    "updated_at",
                ]
            )
            messages.success(request, f"Order #{order.id} updated.")
    return redirect("seller_orders")


# =========================================================
# ALL SELL BOOKS
# =========================================================


@login_required
def all_sell_books(request):

    if hasattr(request.user, "reader_profile"):
        return redirect("user_profile")

    print("\n======================================")
    print("ALL SELL BOOKS")
    print("LOGGED IN USER:", request.user)
    print("USER ID:", request.user.id)
    print("USERNAME:", request.user.username)
    print("======================================")

    # -----------------------------------------------------
    # Find seller profile of logged-in user
    # -----------------------------------------------------

    try:
        seller = sellerprofile.objects.get(user=request.user)

    except sellerprofile.DoesNotExist:

        print("❌ SELLER PROFILE NOT FOUND")
        print("USER:", request.user)

        messages.error(request, "Seller profile not found for this account.")

        return redirect("seller_profile")

    # -----------------------------------------------------
    # Get seller's books
    # -----------------------------------------------------

    books = Book.objects.filter(seller=seller).select_related("seller").order_by("-id")

    print("\n======================================")
    print("SELLER:", seller)
    print("SELLER ID:", seller.id)
    print("BOOK COUNT:", books.count())

    for book in books:

        print(
            "BOOK:",
            book.id,
            "|",
            book.title,
            "| ISBN:",
            book.isbn,
            "| SELLER:",
            book.seller_id,
        )

    print("======================================\n")

    context = {
        "seller": seller,
        "books": books,
    }

    return render(request, "seller/all_sell_books.html", context)


# =========================================================
# ADD BOOK
# =========================================================


@login_required
def seller_add_book(request):
    user_side = hasattr(request.user, "reader_profile")
    seller = sellerprofile.objects.filter(user=request.user).first()
    if seller is None:
        reader = readerprofile.objects.filter(user=request.user).first()
        if reader is None:
            messages.error(
                request, "Please complete your profile before adding a book."
            )
            return redirect("user_profile")
        seller = sellerprofile.objects.create(
            user=request.user,
            full_name=reader.full_name,
            profile_photo=reader.profile_photo,
            phone=reader.phone,
            location=reader.location,
        )

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "").strip()
        isbn = request.POST.get("isbn", "").strip()
        publisher = request.POST.get("publisher", "").strip()

        publication_year = request.POST.get("publication_year", "").strip()

        category = request.POST.get("category", "").strip()

        language = request.POST.get("language", "").strip()

        page_count = request.POST.get("page_count", "").strip()

        description = request.POST.get("description", "").strip()
        price_value = request.POST.get("price", "").strip()
        sale_type = request.POST.get("sale_type", "normal").strip()
        offer_percentage_value = request.POST.get("offer_percentage", "").strip()
        action = request.POST.get("action", "publish").strip()
        is_draft = action == "save_draft"

        cover_image = request.FILES.get("cover_image")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not title:
            messages.error(request, "Book title is required.")
            return redirect("seller_add_book")

        if not author:
            messages.error(request, "Author is required.")
            return redirect("seller_add_book")

        if not isbn:
            messages.error(request, "ISBN-13 is required.")
            return redirect("seller_add_book")

        if len(isbn) != 13 or not isbn.isdigit():
            messages.error(request, "ISBN must contain exactly 13 digits.")
            return redirect("seller_add_book")

        # -------------------------------------------------
        # DUPLICATE ISBN
        # -------------------------------------------------

        if Book.objects.filter(isbn=isbn).exists():

            messages.error(request, "A book with this ISBN already exists.")

            return redirect("seller_add_book")

        if not publisher:
            messages.error(request, "Publisher is required.")
            return redirect("seller_add_book")

        if not publication_year:
            messages.error(request, "Publication year is required.")
            return redirect("seller_add_book")

        if not category:
            messages.error(request, "Category is required.")
            return redirect("seller_add_book")

        if category not in dict(book_category_choices()):
            messages.error(request, "Please select a valid category.")
            return redirect("seller_add_book")

        if not language:
            messages.error(request, "Language is required.")
            return redirect("seller_add_book")

        if language not in dict(book_language_choices()):
            messages.error(request, "Please select a valid language.")
            return redirect("seller_add_book")

        if not page_count:
            messages.error(request, "Page count is required.")
            return redirect("seller_add_book")

        if not description:
            messages.error(request, "Book description is required.")
            return redirect("seller_add_book")

        if len(description) > 1000:

            messages.error(request, "Book description cannot exceed 1000 characters.")

            return redirect("seller_add_book")

        if not is_draft and not price_value:
            messages.error(request, "Price is required before publishing this book.")
            return redirect("seller_add_book")

        if sale_type not in {"normal", "offer"}:
            messages.error(request, "Select Normal sale or Offer sale.")
            return redirect("seller_add_book")

        price = None
        if price_value:
            try:
                price = Decimal(price_value)
            except InvalidOperation:
                messages.error(request, "Price must be a valid amount.")
                return redirect("seller_add_book")
            if price <= 0:
                messages.error(request, "Price must be greater than zero.")
                return redirect("seller_add_book")

        offer_percentage = None
        if sale_type == "offer" and price_value:
            if not offer_percentage_value:
                messages.error(
                    request, "Offer percentage is required for an offer sale."
                )
                return redirect("seller_add_book")
            try:
                offer_percentage = int(offer_percentage_value)
            except ValueError:
                messages.error(request, "Offer must be a valid percentage.")
                return redirect("seller_add_book")
            if not 1 <= offer_percentage <= 99:
                messages.error(request, "Offer must be between 1 and 99 percent.")
                return redirect("seller_add_book")

        # -------------------------------------------------
        # CREATE BOOK
        # -------------------------------------------------

        try:

            book = Book.objects.create(
                seller=seller,
                title=title,
                author=author,
                isbn=isbn,
                publisher=publisher,
                publication_year=publication_year,
                category=category,
                language=language,
                page_count=page_count,
                description=description,
                price=price,
                offer_percentage=offer_percentage,
                status="draft" if is_draft else "published",
                cover_image=cover_image,
            )
            create_offer_notifications(book)

            print("✅ BOOK CREATED:", book.id, book.title, "SELLER:", seller.id)

            messages.success(
                request,
                "Book saved as draft." if is_draft else "Book published successfully.",
            )

            return redirect("user_profile" if user_side else "all_sell_books")

        except Exception as e:

            print("❌ BOOK CREATE ERROR:", e)

            messages.error(request, f"Unable to add book: {str(e)}")

            return redirect("seller_add_book")

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    return render(
        request,
        "seller/seller_add_book.html",
        {
            "seller": seller,
            "edit_mode": False,
            "exchange_mode": False,
            "user_side": user_side,
            "category_choices": book_category_choices(),
            "language_choices": book_language_choices(),
        },
    )


# =========================================================
# EDIT BOOK
# =========================================================


@login_required
def seller_edit_book(request, id):

    try:

        seller = sellerprofile.objects.get(user=request.user)

    except sellerprofile.DoesNotExist:

        messages.error(request, "Seller profile not found.")

        return redirect("seller_profile")

    # -----------------------------------------------------
    # IMPORTANT:
    # Seller can edit ONLY their own book
    # -----------------------------------------------------

    book = get_object_or_404(Book, id=id, seller=seller)
    original_offer_percentage = book.offer_percentage
    original_status = book.status

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        if request.POST.get("action") == "remove_offer":
            book.offer_percentage = None
            book.save(update_fields=["offer_percentage", "updated_at"])
            Notification.objects.filter(book=book).update(is_removed=True, is_read=True)
            messages.success(request, f'Offer removed from "{book.title}".')
            return redirect("all_sell_books")

        title = request.POST.get("title", "").strip()

        author = request.POST.get("author", "").strip()

        isbn = request.POST.get("isbn", "").strip()

        publisher = request.POST.get("publisher", "").strip()

        publication_year = request.POST.get("publication_year", "").strip()

        category = request.POST.get("category", "").strip()

        language = request.POST.get("language", "").strip()

        page_count = request.POST.get("page_count", "").strip()

        description = request.POST.get("description", "").strip()
        price_value = request.POST.get("price", "").strip()
        sale_type = request.POST.get("sale_type", "normal").strip()
        offer_percentage_value = request.POST.get("offer_percentage", "").strip()
        action = request.POST.get("action", "publish").strip()
        is_draft = action == "save_draft"

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not title:

            messages.error(request, "Book title is required.")

            return redirect("seller_edit_book", id=book.id)

        if not author:

            messages.error(request, "Author is required.")

            return redirect("seller_edit_book", id=book.id)

        if not isbn:

            messages.error(request, "ISBN-13 is required.")

            return redirect("seller_edit_book", id=book.id)

        if len(isbn) != 13 or not isbn.isdigit():

            messages.error(request, "ISBN must contain exactly 13 digits.")

            return redirect("seller_edit_book", id=book.id)

        # -------------------------------------------------
        # DUPLICATE ISBN
        # -------------------------------------------------

        if Book.objects.filter(isbn=isbn).exclude(id=book.id).exists():

            messages.error(request, "Another book already uses this ISBN.")

            return redirect("seller_edit_book", id=book.id)

        if not publisher:

            messages.error(request, "Publisher is required.")

            return redirect("seller_edit_book", id=book.id)

        if not publication_year:

            messages.error(request, "Publication year is required.")

            return redirect("seller_edit_book", id=book.id)

        if not category:

            messages.error(request, "Category is required.")

            return redirect("seller_edit_book", id=book.id)

        if category not in dict(book_category_choices()):
            messages.error(request, "Please select a valid category.")
            return redirect("seller_edit_book", id=book.id)

        if not language:

            messages.error(request, "Language is required.")

            return redirect("seller_edit_book", id=book.id)

        if language not in dict(book_language_choices()):
            messages.error(request, "Please select a valid language.")
            return redirect("seller_edit_book", id=book.id)

        if not page_count:

            messages.error(request, "Page count is required.")

            return redirect("seller_edit_book", id=book.id)

        if not description:

            messages.error(request, "Book description is required.")

            return redirect("seller_edit_book", id=book.id)

        if len(description) > 1000:

            messages.error(request, "Book description cannot exceed 1000 characters.")

            return redirect("seller_edit_book", id=book.id)

        if not is_draft and not price_value:
            messages.error(request, "Price is required before publishing this book.")
            return redirect("seller_edit_book", id=book.id)

        if sale_type not in {"normal", "offer"}:
            messages.error(request, "Select Normal sale or Offer sale.")
            return redirect("seller_edit_book", id=book.id)

        price = None
        if price_value:
            try:
                price = Decimal(price_value)
            except InvalidOperation:
                messages.error(request, "Price must be a valid amount.")
                return redirect("seller_edit_book", id=book.id)
            if price <= 0:
                messages.error(request, "Price must be greater than zero.")
                return redirect("seller_edit_book", id=book.id)

        offer_percentage = None
        if sale_type == "offer" and price_value:
            if not offer_percentage_value:
                messages.error(
                    request, "Offer percentage is required for an offer sale."
                )
                return redirect("seller_edit_book", id=book.id)
            try:
                offer_percentage = int(offer_percentage_value)
            except ValueError:
                messages.error(request, "Offer must be a valid percentage.")
                return redirect("seller_edit_book", id=book.id)
            if not 1 <= offer_percentage <= 99:
                messages.error(request, "Offer must be between 1 and 99 percent.")
                return redirect("seller_edit_book", id=book.id)

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        book.title = title
        book.author = author
        book.isbn = isbn
        book.publisher = publisher
        book.publication_year = publication_year
        book.category = category
        book.language = language
        book.page_count = page_count
        book.description = description
        book.price = price
        book.offer_percentage = offer_percentage
        book.status = "draft" if is_draft else "published"

        new_cover = request.FILES.get("cover_image")

        if new_cover:
            book.cover_image = new_cover

        book.save()
        if book.offer_percentage and (
            original_offer_percentage != book.offer_percentage
            or original_status != "published"
        ):
            create_offer_notifications(book)

        messages.success(request, "Book updated successfully.")

        return redirect("all_sell_books")

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    return render(
        request,
        "seller/seller_add_book.html",
        {
            "seller": seller,
            "book": book,
            "edit_mode": True,
            "exchange_mode": False,
            "category_choices": book_category_choices(),
            "language_choices": book_language_choices(),
        },
    )


# =========================================================
# DELETE BOOK
# =========================================================


@login_required
def seller_delete_book(request, id):

    try:

        seller = sellerprofile.objects.get(user=request.user)

    except sellerprofile.DoesNotExist:

        messages.error(request, "Seller profile not found.")

        return redirect("seller_profile")

    # -----------------------------------------------------
    # Only seller's own book
    # -----------------------------------------------------

    book = get_object_or_404(Book, id=id, seller=seller)

    # -----------------------------------------------------
    # DELETE
    # -----------------------------------------------------

    if request.method == "POST":

        book_title = book.title

        try:
            book.delete()
        except ProtectedError:
            messages.error(
                request,
                f'"{book_title}" cannot be deleted because it has existing orders.',
            )
            return redirect("all_sell_books")

        messages.success(request, f'"{book_title}" deleted successfully.')

        return redirect("all_sell_books")

    return redirect("all_sell_books")


# exchange


@login_required
def all_exchange_books(request):

    seller = get_object_or_404(sellerprofile, user=request.user)

    exchange_books = (
        ExchangeBook.objects.filter(seller=seller)
        .select_related("book")
        .prefetch_related("photos")
    )

    active_exchange_count = exchange_books.filter(status="published").count()

    draft_exchange_count = exchange_books.filter(status="draft").count()

    context = {
        "exchange_books": exchange_books,
        "active_exchange_count": active_exchange_count,
        "draft_exchange_count": draft_exchange_count,
    }

    return render(request, "seller/all_exchange_books.html", context)


@login_required
def seller_add_exchange(request):
    user_side = hasattr(request.user, "reader_profile")
    seller = sellerprofile.objects.filter(user=request.user).first()
    if seller is None:
        reader = readerprofile.objects.filter(user=request.user).first()
        if reader is None:
            messages.error(
                request, "Please complete your profile before adding an exchange book."
            )
            return redirect("user_profile")
        seller = sellerprofile.objects.create(
            user=request.user,
            full_name=reader.full_name,
            profile_photo=reader.profile_photo,
            phone=reader.phone,
            location=reader.location,
        )

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "").strip()
        isbn = request.POST.get("isbn", "").strip()
        publisher = request.POST.get("publisher", "").strip()
        publication_year = request.POST.get("publication_year", "").strip()
        category = request.POST.get("category", "").strip()
        language = request.POST.get("language", "").strip()
        page_count = request.POST.get("page_count", "").strip()
        description = request.POST.get("description", "").strip()

        cover_image = request.FILES.get("cover_image")

        is_draft = "save_draft" in request.POST

        # --------------------------------------------------
        # REQUIRED VALIDATION FOR CONTINUE
        # --------------------------------------------------

        if not is_draft:

            required_fields = {
                "Title": title,
                "Author": author,
                "ISBN": isbn,
                "Publisher": publisher,
                "Publication Year": publication_year,
                "Category": category,
                "Language": language,
                "Page Count": page_count,
                "Description": description,
            }

            missing_fields = [
                name for name, value in required_fields.items() if not value
            ]

            if not cover_image:
                messages.error(request, "Please upload a book cover.")

            if missing_fields:
                messages.error(
                    request,
                    "Please fill all required fields: " + ", ".join(missing_fields),
                )

            if not cover_image or missing_fields:

                return render(
                    request,
                    "seller/seller_add_book.html",
                    {
                        "edit_mode": False,
                        "exchange_mode": True,
                        "current_step": 1,
                        "user_side": user_side,
                        "category_choices": book_category_choices(),
                        "language_choices": book_language_choices(),
                    },
                )

            if category not in dict(book_category_choices()):
                messages.error(request, "Please select a valid category.")
                return redirect("seller_add_exchange")

            if language not in dict(book_language_choices()):
                messages.error(request, "Please select a valid language.")
                return redirect("seller_add_exchange")

        try:

            with transaction.atomic():

                book = Book.objects.create(
                    seller=seller,
                    title=title,
                    author=author,
                    isbn=isbn,
                    publisher=publisher,
                    publication_year=publication_year or None,
                    category=category,
                    language=language,
                    page_count=page_count or None,
                    description=description,
                    cover_image=cover_image,
                )

                exchange_book = ExchangeBook.objects.create(
                    book=book,
                    seller=seller,
                    status="draft",
                )

            # SAVE DRAFT
            if is_draft:

                messages.success(request, "Exchange book saved as draft.")

                return redirect("user_profile" if user_side else "all_exchange_books")

            # Continue to delivery; exchange listings do not use a selling price.
            return redirect("seller_exchange_condition", book_id=book.id)
            return redirect("seller_exchange_delivery", book_id=book.id)
        except Exception as e:

            messages.error(request, f"Unable to save exchange book: {str(e)}")

    return render(
        request,
        "seller/seller_add_book.html",
        {
            "edit_mode": False,
            "exchange_mode": True,
            "current_step": 1,
            "user_side": user_side,
            "category_choices": book_category_choices(),
            "language_choices": book_language_choices(),
        },
    )


# EXCHANGE CONDITION - STEP 2
@login_required
def seller_exchange_condition(request, book_id):

    seller = get_object_or_404(sellerprofile, user=request.user)

    book = get_object_or_404(Book, id=book_id, seller=seller)

    exchange_book = get_object_or_404(ExchangeBook, book=book, seller=seller)

    existing_photos = exchange_book.photos.all()

    if request.method == "POST":

        condition = request.POST.get("condition", "").strip()

        specific_details = request.POST.getlist("specific_details")

        additional_notes = request.POST.get("additional_notes", "").strip()

        uploaded_photos = request.FILES.getlist("photos")

        is_draft = "save_draft" in request.POST

        # --------------------------------------------------
        # UPDATE STEP 2 DATA
        # --------------------------------------------------

        exchange_book.condition = condition

        exchange_book.specific_details = specific_details

        exchange_book.additional_notes = additional_notes

        # --------------------------------------------------
        # PHOTO LIMIT
        # --------------------------------------------------

        existing_count = exchange_book.photos.count()

        total_count = existing_count + len(uploaded_photos)

        if total_count > 6:

            messages.error(request, "Maximum 6 photos are allowed.")

            return render(
                request,
                "seller/exchange_condition.html",
                {
                    "book": book,
                    "exchange_book": exchange_book,
                    "photos": existing_photos,
                    "current_step": 2,
                    "edit_mode": True,
                    "exchange_mode": True,
                },
            )

        # --------------------------------------------------
        # REQUIRED VALIDATION
        # --------------------------------------------------

        if not is_draft:

            errors = []

            if not condition:
                errors.append("Please select the book condition.")

            if total_count < 2:
                errors.append("Please upload at least 2 photos.")

            if errors:

                for error in errors:
                    messages.error(request, error)

                return render(
                    request,
                    "seller/exchange_condition.html",
                    {
                        "book": book,
                        "exchange_book": exchange_book,
                        "photos": existing_photos,
                        "current_step": 2,
                        "edit_mode": True,
                        "exchange_mode": True,
                    },
                )

        # --------------------------------------------------
        # SAVE NEW PHOTOS
        # --------------------------------------------------

        for photo in uploaded_photos:

            ExchangeBookPhoto.objects.create(exchange_book=exchange_book, photo=photo)

        # --------------------------------------------------
        # SAVE EXCHANGE
        # --------------------------------------------------

        exchange_book.save()

        # --------------------------------------------------
        # SAVE DRAFT
        # --------------------------------------------------

        if is_draft:

            exchange_book.status = "draft"

            exchange_book.save(update_fields=["status", "updated_at"])

            messages.success(request, "Exchange book saved as draft.")

            return redirect("all_exchange_books")

        # --------------------------------------------------
        # CONTINUE STEP 3
        # --------------------------------------------------

        return redirect("seller_exchange_delivery", book_id=book.id)

    return render(
        request,
        "seller/exchange_condition.html",
        {
            "book": book,
            "exchange_book": exchange_book,
            "photos": existing_photos,
            "current_step": 2,
            "edit_mode": True,
            "exchange_mode": True,
        },
    )


# photo
def seller_exchange_photos(request, book_id):

    book = get_object_or_404(Book, id=book_id)

    exchange_book = get_object_or_404(ExchangeBook, book=book)

    if request.method == "POST":

        photos = request.FILES.getlist("book_photos")

        if not photos:
            messages.error(request, "Please select photos.")

            return redirect("seller_exchange_photos", book_id=book.id)

        # Existing photos count
        existing_count = exchange_book.photos.count()

        # Maximum 4 photos
        if existing_count + len(photos) > 4:

            messages.error(request, "Maximum 4 photos allowed.")

            return redirect("seller_exchange_photos", book_id=book.id)

        # Save photos
        for photo in photos:

            ExchangeBookPhoto.objects.create(exchange_book=exchange_book, photo=photo)

        messages.success(request, "Photos uploaded successfully.")

        return redirect("seller_exchange_photos", book_id=book.id)

    return render(
        request,
        "seller/exchange_condition.html",
        {
            "book": book,
            "exchange_book": exchange_book,
        },
    )


@login_required
def seller_exchange_photo_delete(request, book_id, photo_id):

    seller = get_object_or_404(sellerprofile, user=request.user)

    book = get_object_or_404(Book, id=book_id, seller=seller)

    exchange_book = get_object_or_404(ExchangeBook, book=book, seller=seller)

    photo = get_object_or_404(
        ExchangeBookPhoto, id=photo_id, exchange_book=exchange_book
    )

    if request.method == "POST":

        photo.delete()

        messages.success(request, "Photo deleted successfully.")

    return redirect("seller_exchange_condition", book_id=book.id)


# EXCHANGE PRICING - STEP 3
@login_required
def seller_exchange_pricing(request, book_id):
    # Keep this legacy URL working for old bookmarks, but skip pricing entirely.
    seller = get_object_or_404(sellerprofile, user=request.user)
    book = get_object_or_404(Book, id=book_id, seller=seller)
    return redirect("seller_exchange_delivery", book_id=book.id)


# ============================================================
# EXCHANGE DELIVERY - STEP 4
# ============================================================


@login_required
def seller_exchange_delivery(request, book_id):

    seller = get_object_or_404(sellerprofile, user=request.user)

    book = get_object_or_404(Book, id=book_id, seller=seller)

    exchange_book = get_object_or_404(ExchangeBook, book=book, seller=seller)

    if request.method == "POST":

        # --------------------------------------------------
        # SAVE DRAFT
        # --------------------------------------------------

        if "save_draft" in request.POST:

            exchange_book.status = "draft"

            exchange_book.save()

            messages.success(request, "Exchange book saved as draft.")

            return redirect("all_exchange_books")

        # --------------------------------------------------
        # VALIDATE
        # --------------------------------------------------

        errors = []

        if not exchange_book.condition:

            errors.append("Book condition is required.")

        if exchange_book.photos.count() < 2:

            errors.append("At least 2 photos are required.")

        if errors:

            for error in errors:

                messages.error(request, error)

            return redirect("seller_exchange_condition", book_id=book.id)

        # --------------------------------------------------
        # REVIEW
        # --------------------------------------------------

        return redirect("seller_exchange_review", book_id=book.id)

    return render(
        request,
        "seller/exchange_delivery.html",
        {
            "book": book,
            "exchange_book": exchange_book,
            "current_step": 4,
            "edit_mode": True,
            "exchange_mode": True,
        },
    )


# ============================================================
# EXCHANGE REVIEW - STEP 5
# ============================================================


@login_required
def seller_exchange_review(request, book_id):

    seller = get_object_or_404(sellerprofile, user=request.user)

    book = get_object_or_404(Book, id=book_id, seller=seller)

    exchange_book = get_object_or_404(ExchangeBook, book=book, seller=seller)

    photos = exchange_book.photos.all()

    if request.method == "POST":

        action = request.POST.get("action")

        # --------------------------------------------------
        # SAVE DRAFT
        # --------------------------------------------------

        if action == "save_draft":

            exchange_book.status = "draft"

            exchange_book.save()

            messages.success(request, "Exchange book saved as draft.")

            return redirect("all_exchange_books")

        # --------------------------------------------------
        # PUBLISH / UPDATE
        # --------------------------------------------------

        if action in ["publish", "add_exchange", "update_exchange"]:

            errors = []

            # STEP 1
            if not book.title:
                errors.append("Book title is required.")

            if not book.author:
                errors.append("Author is required.")

            if not book.isbn:
                errors.append("ISBN is required.")

            if not book.publisher:
                errors.append("Publisher is required.")

            if not book.publication_year:
                errors.append("Publication year is required.")

            if not book.category:
                errors.append("Category is required.")

            if not book.language:
                errors.append("Language is required.")

            if not book.page_count:
                errors.append("Page count is required.")

            if not book.description:
                errors.append("Description is required.")

            if not book.cover_image:
                errors.append("Book cover is required.")

            # STEP 2
            if not exchange_book.condition:

                errors.append("Please select book condition.")

            if photos.count() < 2:

                errors.append("At least 2 photos are required.")

            # --------------------------------------------------
            # SHOW ERRORS
            # --------------------------------------------------

            if errors:

                for error in errors:

                    messages.error(request, error)

                return render(
                    request,
                    "seller/exchange_review.html",
                    {
                        "book": book,
                        "exchange_book": exchange_book,
                        "photos": photos,
                        "current_step": 5,
                        "edit_mode": True,
                        "exchange_mode": True,
                    },
                )

            # --------------------------------------------------
            # PUBLISH / UPDATE
            # --------------------------------------------------

            exchange_book.status = "published"

            exchange_book.save()

            messages.success(request, "Exchange book updated successfully.")

            return redirect("all_exchange_books")

    return render(
        request,
        "seller/exchange_review.html",
        {
            "book": book,
            "exchange_book": exchange_book,
            "photos": photos,
            "current_step": 5,
            "edit_mode": True,
            "exchange_mode": True,
        },
    )


# ============================================================
# DELETE EXCHANGE BOOK
# ============================================================


@login_required
def seller_delete_exchange(request, exchange_id):

    seller = get_object_or_404(sellerprofile, user=request.user)

    exchange_book = (
        ExchangeBook.objects.filter(id=exchange_id, seller=seller)
        .select_related("book")
        .first()
    )

    if exchange_book is None:
        messages.info(request, "This exchange listing was already deleted.")
        return redirect("all_exchange_books")

    if request.method == "POST":

        book = exchange_book.book

        exchange_book.delete()

        if book.orders.exists():
            messages.success(
                request,
                "Exchange listing deleted. The book was kept because it has existing orders.",
            )
        else:
            book.delete()
            messages.success(request, "Exchange book deleted successfully.")

    return redirect("all_exchange_books")


# ============================================================
# EDIT EXCHANGE - BASIC INFORMATION
# ============================================================


@login_required
def seller_edit_exchange(request, exchange_id):

    seller = get_object_or_404(sellerprofile, user=request.user)

    exchange_book = get_object_or_404(
        ExchangeBook.objects.select_related("book"), id=exchange_id, seller=seller
    )

    book = exchange_book.book

    category_choices = book_category_choices()
    language_choices = book_language_choices()

    # ==================================================
    # GET REQUEST
    # SHOW OLD BOOK DATA
    # ==================================================

    if request.method == "GET":

        return render(
            request,
            "seller/seller_add_book.html",
            {
                "edit_mode": True,
                "exchange_mode": True,
                # IMPORTANT
                "book": book,
                "exchange_book": exchange_book,
                "current_step": 1,
                "category_choices": category_choices,
                "language_choices": language_choices,
            },
        )

    # ==================================================
    # POST REQUEST
    # ==================================================

    title = request.POST.get("title", "").strip()
    author = request.POST.get("author", "").strip()
    isbn = request.POST.get("isbn", "").strip()
    publisher = request.POST.get("publisher", "").strip()
    publication_year = request.POST.get("publication_year", "").strip()
    category = request.POST.get("category", "").strip()
    language = request.POST.get("language", "").strip()
    page_count = request.POST.get("page_count", "").strip()
    description = request.POST.get("description", "").strip()

    cover_image = request.FILES.get("cover_image")

    # ==================================================
    # REQUIRED FIELDS
    # ==================================================

    required_fields = {
        "Title": title,
        "Author": author,
        "ISBN": isbn,
        "Publisher": publisher,
        "Publication Year": publication_year,
        "Category": category,
        "Language": language,
        "Page Count": page_count,
        "Description": description,
    }

    missing_fields = [name for name, value in required_fields.items() if not value]

    if missing_fields:

        messages.error(
            request, "Please fill all required fields: " + ", ".join(missing_fields)
        )

        return render(
            request,
            "seller/seller_add_book.html",
            {
                "edit_mode": True,
                "exchange_mode": True,
                "book": book,
                "exchange_book": exchange_book,
                "current_step": 1,
                "category_choices": category_choices,
                "language_choices": language_choices,
            },
        )

    # ==================================================
    # VALIDATE CATEGORY
    # ==================================================

    if category not in dict(category_choices):

        messages.error(request, "Please select a valid category.")

        return render(
            request,
            "seller/seller_add_book.html",
            {
                "edit_mode": True,
                "exchange_mode": True,
                "book": book,
                "exchange_book": exchange_book,
                "current_step": 1,
                "category_choices": category_choices,
                "language_choices": language_choices,
            },
        )

    # ==================================================
    # VALIDATE LANGUAGE
    # ==================================================

    if language not in dict(language_choices):

        messages.error(request, "Please select a valid language.")

        return render(
            request,
            "seller/seller_add_book.html",
            {
                "edit_mode": True,
                "exchange_mode": True,
                "book": book,
                "exchange_book": exchange_book,
                "current_step": 1,
                "category_choices": category_choices,
                "language_choices": language_choices,
            },
        )

    # ==================================================
    # UPDATE BOOK
    # ==================================================

    book.title = title
    book.author = author
    book.isbn = isbn
    book.publisher = publisher
    book.publication_year = publication_year or None
    book.category = category
    book.language = language
    book.page_count = page_count or None
    book.description = description

    # Only replace image when a new image is uploaded
    if cover_image:
        book.cover_image = cover_image

    book.save()

    messages.success(request, "Basic information updated successfully.")

    # ==================================================
    # GO TO STEP 2
    # ==================================================

    return redirect("seller_exchange_condition", book_id=book.id)


# client side
# CLIENT - ALL PUBLISHED EXCHANGE BOOKS


def client_exchange_books(request):
    return exchange(request)


# CLIENT - EXCHANGE BOOK DETAIL


def client_exchange_book_detail(request, exchange_id):

    exchange_book = get_object_or_404(
        ExchangeBook.objects.select_related("book", "seller").prefetch_related(
            "photos"
        ),
        id=exchange_id,
        status="published",
    )

    book = exchange_book.book
    seller = exchange_book.seller
    photos = exchange_book.photos.all()
    in_wishlist = (
        request.user.is_authenticated
        and Wishlist.objects.filter(
            user=request.user, exchange_book=exchange_book
        ).exists()
    )
    offered_books = []
    existing_exchange_request = None
    if request.user.is_authenticated:
        offered_books = Book.objects.filter(
            seller__user=request.user, exchange_details__status="published"
        ).order_by("title")
        existing_exchange_request = ExchangeRequest.objects.filter(
            exchange_book=exchange_book, requester=request.user
        ).first()

    return render(
        request,
        "exchange_book_detail.html",
        {
            "exchange_book": exchange_book,
            "book": book,
            "seller": seller,
            "photos": photos,
            "in_wishlist": in_wishlist,
            "offered_books": offered_books,
            "existing_exchange_request": existing_exchange_request,
        },
    )


#  seller Support Center
@login_required
def seller_support(request):
    tickets = SupportTicket.objects.filter(seller=request.user).order_by("-created_at")

    open_count = tickets.filter(status="open").count()

    in_progress_count = tickets.filter(status="in_progress").count()

    resolved_count = tickets.filter(status="resolved").count()

    context = {
        "tickets": tickets,
        "open_count": open_count,
        "in_progress_count": in_progress_count,
        "resolved_count": resolved_count,
    }

    return render(request, "seller/seller_support.html", context)


# Create a new support ticket.
@login_required
def seller_create_support_ticket(request):
    if request.method == "POST":

        subject = request.POST.get("subject", "").strip()
        category = request.POST.get("category", "").strip()
        priority = request.POST.get("priority", "").strip()
        message = request.POST.get("message", "").strip()

        if not subject:
            messages.error(request, "Please enter a subject.")

            return redirect("seller_support")

        if not category:
            messages.error(request, "Please select a category.")

            return redirect("seller_support")

        if not priority:
            priority = "medium"

        if not message:
            messages.error(request, "Please enter your issue.")

            return redirect("seller_support")

        SupportTicket.objects.create(
            seller=request.user,
            subject=subject,
            category=category,
            priority=priority,
            message=message,
            status="open",
        )

        messages.success(
            request, "Your support ticket has been submitted successfully."
        )

        return redirect("seller_support")

    return redirect("seller_support")


# View a single seller support ticket.
@login_required
def seller_support_ticket_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id, seller=request.user)

    return render(
        request, "seller/seller_support_ticket_detail.html", {"ticket": ticket}
    )


# aboutus
def about_us(request):
    return render(request, "about_us.html")

# help_center
def help_center(request):
    show_contact_form = request.GET.get("contact") == "1"
    tickets = (
        SupportTicket.objects.filter(seller=request.user).order_by("-created_at")
        if request.user.is_authenticated and show_contact_form
        else []
    )
    return render(
        request,
        "help_center.html",
        {
            "support_tickets": tickets,
            "show_contact_form": show_contact_form,
        },
    )


@login_required
def create_user_support_ticket(request):
    if request.method != "POST":
        return redirect("help_center")

    subject = request.POST.get("subject", "").strip()
    category = request.POST.get("category", "").strip()
    message = request.POST.get("message", "").strip()

    if not subject or not category or not message:
        messages.error(request, "Please complete the subject, category and message.")
        return redirect("/help/?contact=1#contact-support")

    SupportTicket.objects.create(
        seller=request.user,
        subject=subject,
        category=category,
        priority="medium",
        message=message,
        status="open",
    )
    messages.success(request, "Your query has been sent to BookSwap support.")
    return redirect("/help/?contact=1#contact-support")


@login_required
def user_support_ticket_detail(request, ticket_id):
    ticket = get_object_or_404(
        SupportTicket, id=ticket_id, seller=request.user
    )
    return render(
        request,
        "user_support_ticket_detail.html",
        {"ticket": ticket},
    )


@login_required
def edit_user_support_ticket(request, ticket_id):
    ticket = get_object_or_404(
        SupportTicket, id=ticket_id, seller=request.user, status="open"
    )

    if request.method == "POST":
        subject = request.POST.get("subject", "").strip()
        category = request.POST.get("category", "").strip()
        message = request.POST.get("message", "").strip()

        if not subject or not category or not message:
            messages.error(request, "Please complete the subject, category and message.")
        else:
            ticket.subject = subject
            ticket.category = category
            ticket.message = message
            ticket.save(update_fields=["subject", "category", "message", "updated_at"])
            messages.success(request, "Your support ticket was updated.")
            return redirect("user_support_ticket_detail", ticket_id=ticket.id)

    return render(
        request,
        "user_support_ticket_edit.html",
        {"ticket": ticket},
    )


@login_required
def delete_user_support_ticket(request, ticket_id):
    ticket = get_object_or_404(
        SupportTicket, id=ticket_id, seller=request.user, status="open"
    )
    if request.method == "POST":
        ticket.delete()
        messages.success(request, "Your support ticket was deleted.")
    return redirect("help_center")

# terms_privacy
def terms_privacy(request):
    return render(request, "terms_privacy.html")
# how_it_works
def how_it_works(request):
    return render(request, "how_it_works.html")
