from django.contrib import admin
from django.utils.text import slugify
from myapp.models import *


# Register your models here.
@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    def save_model(self, request, obj, form, change):
        if not obj.code:
            obj.code = slugify(obj.name)
        super().save_model(request, obj, form, change)


@admin.register(BookLanguage)
class BookLanguageAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    def save_model(self, request, obj, form, change):
        if not obj.code:
            obj.code = obj.name
        super().save_model(request, obj, form, change)


@admin.register(readerprofile)
class readerprofileadmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "full_name",
        "profile_photo",
        "phone",
        "location",
    )
    search_fields = (
        "user__username",
        "user__email",
        "full_name",
        "phone",
    )


@admin.register(sellerprofile)
class sellerprofileadmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "full_name",
        "profile_photo",
        "phone",
        "location",
        "store_name",
    )
    search_fields = (
        "user__username",
        "user__email",
        "full_name",
        "phone",
        "store_name",
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "author",
        "isbn",
        "seller",
        "category",
        "language",
        "publication_year",
        "page_count",
        "price",
        "offer_percentage",
        "created_at",
    )

    list_filter = (
        "category",
        "language",
        "publication_year",
        "created_at",
    )

    search_fields = (
        "title",
        "author",
        "isbn",
        "publisher",
        "seller__user__username",
        "seller__store_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)


@admin.register(BookOrder)
class BookOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "book",
        "buyer",
        "amount",
        "payment_method",
        "payment_status",
        "status",
        "created_at",
    )
    list_filter = ("payment_method", "payment_status", "status", "created_at")
    search_fields = ("book__title", "buyer__username", "buyer__email")
    readonly_fields = ("created_at", "updated_at")


# exchange
class ExchangeBookPhotoInline(admin.TabularInline):
    model = ExchangeBookPhoto
    extra = 1
    max_num = 6


@admin.register(ExchangeBook)
class ExchangeBookAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "book",
        "seller",
        "condition",
        "selling_price",
        "status",
        "created_at",
    )
    search_fields = (
        "book__title",
        "book__author",
        "book__isbn",
        "seller__user__username",
    )
    list_filter = (
        "condition",
        "status",
        "created_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    inlines = [ExchangeBookPhotoInline]


@admin.register(ExchangeBookPhoto)
class ExchangeBookPhotoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "exchange_book",
        "created_at",
    )
    search_fields = ("exchange_book__book__title",)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "exchange_book", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "book__title", "exchange_book__book__title")


@admin.register(ExchangeRequest)
class ExchangeRequestAdmin(admin.ModelAdmin):
    list_display = (
        "exchange_book",
        "requester",
        "offered_book",
        "status",
        "updated_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "requester__username",
        "exchange_book__book__title",
        "offered_book__title",
    )


@admin.register(ExchangeMessage)
class ExchangeMessageAdmin(admin.ModelAdmin):
    list_display = ("exchange_request", "sender", "created_at")
    search_fields = ("sender__username", "body")


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "subject",
        "seller",
        "category",
        "priority",
        "status",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "priority",
        "category",
        "created_at",
    )

    search_fields = (
        "subject",
        "message",
        "admin_reply",
        "seller__username",
        "seller__email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    fieldsets = (
        (
            "Ticket Information",
            {
                "fields": (
                    "seller",
                    "subject",
                    "category",
                    "priority",
                    "status",
                )
            },
        ),
        ("Seller Message", {"fields": ("message",)}),
        ("Admin Response", {"fields": ("admin_reply",)}),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
