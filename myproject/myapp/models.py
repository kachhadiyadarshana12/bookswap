from datetime import timedelta
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class readerprofile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="reader_profile"
    )
    full_name = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to="profile_photo/", blank=True, null=True)
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class sellerprofile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="seller_profile"
    )
    full_name = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to="seller_photos/", blank=True, null=True)
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=100)
    store_name = models.CharField(max_length=100, blank=True)
    seller_description = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class BookCategory(models.Model):
    code = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Book category"
        verbose_name_plural = "Book categories"

    def __str__(self):
        return self.name


class BookLanguage(models.Model):
    code = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Book language"
        verbose_name_plural = "Book languages"

    def __str__(self):
        return self.name


# seller add book
class Book(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]
    CATEGORY_CHOICES = [
        ("fiction", "Fiction"),
        ("non-fiction", "Non-Fiction"),
        ("finance", "Finance"),
        ("history", "History"),
        ("biography", "Biography"),
        ("science", "Science"),
        ("technology", "Technology"),
        ("self-help", "Self Help"),
        ("romance", "Romance"),
        ("education", "Education"),
        ("other", "Other"),
    ]
    LANGUAGE_CHOICES = [
        ("English", "English"),
        ("Gujarati", "Gujarati"),
        ("Hindi", "Hindi"),
        ("Marathi", "Marathi"),
        ("Bengali", "Bengali"),
        ("Tamil", "Tamil"),
        ("Telugu", "Telugu"),
        ("Other", "Other"),
    ]
    seller = models.ForeignKey(
        sellerprofile, on_delete=models.CASCADE, related_name="books"
    )
    cover_image = models.ImageField(upload_to="book_covers/")
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    isbn = models.CharField(max_length=13)
    publisher = models.CharField(max_length=150)
    publication_year = models.PositiveIntegerField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES)
    page_count = models.PositiveIntegerField()
    description = models.TextField(max_length=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    offer_percentage = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def offer_price(self):
        if self.price is None or self.offer_percentage is None:
            return None
        return self.price * (100 - self.offer_percentage) / 100

    class Meta:
        ordering = ["-created_at"]


# exchange book
class ExchangeBook(models.Model):

    CONDITION_CHOICES = [
        ("new", "New"),
        ("like_new", "Like New"),
        ("good", "Good"),
        ("fair", "Fair"),
        ("poor", "Poor"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]

    DAMAGE_CHOICES = [
        ("minor_cover_wear", "Minor cover wear"),
        ("creased_spine", "Creased spine"),
        ("page_markings", "Page markings"),
        ("water_damage", "Water damage"),
        ("highlighting", "Highlighting"),
        ("missing_pages", "Missing pages"),
        ("writing_margins", "Writing in margins"),
        ("dust_jacket_damage", "Dust jacket damage"),
        ("folded_corners", "Folded corners"),
        ("other", "Other"),
    ]

    # Existing Book sathe relation
    book = models.OneToOneField(
        "Book", on_delete=models.CASCADE, related_name="exchange_details"
    )

    # Seller profile
    seller = models.ForeignKey(
        "sellerprofile", on_delete=models.CASCADE, related_name="exchange_books"
    )

    # Step 2
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)

    # Checkbox selections
    specific_details = models.JSONField(default=list, blank=True)

    # Other / additional notes
    additional_notes = models.TextField(blank=True, null=True)

    # Step 3
    selling_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    # Draft / Published
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.book.title} - Exchange"

    class Meta:
        ordering = ["-created_at"]


class ExchangeBookPhoto(models.Model):

    exchange_book = models.ForeignKey(
        ExchangeBook, on_delete=models.CASCADE, related_name="photos"
    )

    photo = models.ImageField(upload_to="exchange_books/")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exchange_book.book.title} Photo"


class Wishlist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlist_items"
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="wishlist_items",
    )
    exchange_book = models.ForeignKey(
        ExchangeBook,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="wishlist_items",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"], name="unique_wishlist_book"
            ),
            models.UniqueConstraint(
                fields=["user", "exchange_book"], name="unique_wishlist_exchange_book"
            ),
        ]

    def __str__(self):
        item = self.exchange_book.book if self.exchange_book_id else self.book
        return f"{self.user.username} - {item.title}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("offer", "New Offer"),
        ("chat", "New Chat Message"),
        ("exchange", "Exchange Request"),
    ]
    
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications"
    )
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, default="offer"
    )
    exchange_request = models.ForeignKey(
        "ExchangeRequest", on_delete=models.CASCADE, null=True, blank=True, related_name="notifications"
    )
    is_read = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        if self.notification_type == "chat":
            return f"{self.user.username} - New chat message"
        if self.book:
            return f"{self.user.username} - New offer on {self.book.title}"
        return f"{self.user.username} - Notification"


class BookOrder(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash on delivery"),
        ("online", "Online payment"),
    ]
    STATUS_CHOICES = [
        ("placed", "Order placed"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]
    DELIVERY_STATUS_CHOICES = [
        ("pending", "Delivery pending"),
        ("packed", "Packed"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out for delivery"),
        ("delivered", "Delivered"),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Payment pending"),
        ("paid", "Paid"),
        ("failed", "Payment failed"),
    ]
    REFUND_STATUS_CHOICES = [
        ("not_applicable", "Not applicable"),
        ("pending", "Refund pending"),
        ("completed", "Refund completed"),
    ]

    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="orders")
    buyer = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="book_orders"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    payment_reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="placed")
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)
    recipient_name = models.CharField(max_length=100)
    recipient_phone = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80)
    postal_code = models.CharField(max_length=10)
    delivery_status = models.CharField(
        max_length=20, choices=DELIVERY_STATUS_CHOICES, default="pending"
    )
    delivery_note = models.TextField(blank=True)
    tracking_reference = models.CharField(max_length=100, blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    refund_status = models.CharField(
        max_length=20, choices=REFUND_STATUS_CHOICES, default="not_applicable"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} - {self.book.title}"

    @property
    def estimated_delivery_date(self):
        return self.created_at.date() + timedelta(days=7)

    @property
    def cancellation_deadline(self):
        return self.created_at + timedelta(days=3)

    @property
    def can_be_cancelled(self):
        return (
            self.status != "cancelled"
            and self.delivery_status == "pending"
            and timezone.now() <= self.cancellation_deadline
        )


class ExchangeRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]

    exchange_book = models.ForeignKey(
        ExchangeBook, on_delete=models.CASCADE, related_name="exchange_requests"
    )
    requester = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_exchange_requests"
    )
    offered_book = models.ForeignKey(
        Book,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="offered_exchange_requests",
    )
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["exchange_book", "requester"], name="unique_exchange_requester"
            )
        ]

    @property
    def owner(self):
        return self.exchange_book.seller.user

    def __str__(self):
        return f"{self.requester.username} -> {self.exchange_book.book.title}"


class ExchangeMessage(models.Model):
    exchange_request = models.ForeignKey(
        ExchangeRequest, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="exchange_messages"
    )
    body = models.TextField(max_length=2000)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender.username}: {self.body[:30]}"


# seller support 
class SupportTicket(models.Model):

    CATEGORY_CHOICES = [
        ("account", "Account & Profile"),
        ("books", "Books & Listings"),
        ("exchange", "Book Exchange"),
        ("orders", "Orders"),
        ("payment", "Payments"),
        ("delivery", "Delivery"),
        ("technical", "Technical Issue"),
        ("other", "Other"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="support_tickets"
    )

    subject = models.CharField(max_length=200)

    category = models.CharField(
        max_length=30, choices=CATEGORY_CHOICES, default="other"
    )

    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default="medium"
    )

    message = models.TextField()

    admin_reply = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.id} - {self.subject}"


class WebhookEvent(models.Model):
    event_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type} - {self.event_id}"


class PasswordResetOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='password_reset_otp')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now=True)

    def is_valid(self):
        return timezone.now() < self.created_at + timedelta(minutes=5)

