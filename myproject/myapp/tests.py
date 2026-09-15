from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Book, BookOrder, ExchangeBook, sellerprofile


class BookOrderTests(TestCase):
	def setUp(self):
		self.seller_user = User.objects.create_user(username="seller", password="testpass")
		self.buyer_user = User.objects.create_user(username="buyer", password="testpass")
		self.seller = sellerprofile.objects.create(
			user=self.seller_user,
			full_name="Book Seller",
			phone="9999999999",
			location="Ahmedabad",
		)
		self.book = Book.objects.create(
			seller=self.seller,
			title="Test Book",
			author="Test Author",
			isbn="1234567890123",
			publisher="Test Publisher",
			publication_year=2024,
			category="fiction",
			language="English",
			page_count=100,
			description="A test book",
			price=Decimal("500.00"),
			offer_percentage=10,
		)

	def test_browse_offers_sort_shows_only_offer_books(self):
		self.book.status = "published"
		self.book.save(update_fields=["status"])

		normal_book = Book.objects.create(
			seller=self.seller,
			title="Normal Book",
			author="Normal Author",
			isbn="9876543210123",
			publisher="Test Publisher",
			publication_year=2024,
			category="fiction",
			language="English",
			page_count=100,
			description="A normal test book",
			price=Decimal("400.00"),
			status="published",
		)

		response = self.client.get(reverse("browse"), {"sort": "offer"})

		self.assertEqual(response.context["book_count"], 1)
		self.assertContains(response, self.book.title)
		self.assertNotContains(response, normal_book.title)

	def test_cash_order_is_created_at_offer_price(self):
		self.client.force_login(self.buyer_user)

		response = self.client.post(
			reverse("buy_book", args=[self.book.id]),
			self.order_data("cash"),
		)

		order = BookOrder.objects.get()
		self.assertRedirects(response, reverse("user_profile"))
		self.assertEqual(order.amount, Decimal("450.00"))
		self.assertEqual(order.payment_method, "cash")
		self.assertEqual(order.payment_status, "pending")

	def test_online_order_is_paid_after_confirmation(self):
		self.client.force_login(self.buyer_user)

		self.client.post(
			reverse("buy_book", args=[self.book.id]),
			{**self.order_data("online"), "payment_confirmed": "1"},
		)

		order = BookOrder.objects.get()
		self.assertEqual(order.payment_method, "online")
		self.assertEqual(order.payment_status, "paid")

	def test_online_order_requires_confirmation(self):
		self.client.force_login(self.buyer_user)

		response = self.client.post(
			reverse("buy_book", args=[self.book.id]), self.order_data("online")
		)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(BookOrder.objects.exists())

	def test_duplicate_order_does_not_charge_twice(self):
		self.client.force_login(self.buyer_user)
		data = {**self.order_data("online"), "payment_confirmed": "1"}

		self.client.post(reverse("buy_book", args=[self.book.id]), data)
		response = self.client.post(reverse("buy_book", args=[self.book.id]), data)

		self.assertRedirects(response, reverse("user_profile"))
		self.assertEqual(BookOrder.objects.filter(book=self.book, buyer=self.buyer_user).count(), 1)

	def test_invalid_payment_method_does_not_create_order(self):
		self.client.force_login(self.buyer_user)

		response = self.client.post(
			reverse("buy_book", args=[self.book.id]),
			self.order_data("cheque"),
		)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(BookOrder.objects.exists())

	def test_invalid_contact_and_address_details_do_not_create_order(self):
		self.client.force_login(self.buyer_user)

		invalid_data = self.order_data("cash")
		invalid_data.update(
			{
				"recipient_phone": "98765abc10",
				"postal_code": "3800",
				"city": "A1medabad",
			}
		)
		response = self.client.post(
			reverse("buy_book", args=[self.book.id]), invalid_data
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Phone number must contain exactly 10 digits.")
		self.assertFalse(BookOrder.objects.exists())

	def test_seller_cannot_buy_own_book(self):
		self.client.force_login(self.seller_user)

		self.client.post(
			reverse("buy_book", args=[self.book.id]),
			self.order_data("cash"),
		)

		self.assertFalse(BookOrder.objects.exists())

	def test_checkout_page_and_seller_order_update(self):
		self.client.force_login(self.buyer_user)
		checkout_response = self.client.get(reverse("checkout", args=[self.book.id]))
		self.assertEqual(checkout_response.status_code, 200)

		self.client.post(reverse("buy_book", args=[self.book.id]), self.order_data("cash"))
		order = BookOrder.objects.get()

		self.client.force_login(self.seller_user)
		orders_response = self.client.get(reverse("seller_orders"))
		self.assertEqual(orders_response.status_code, 200)
		self.client.post(
			reverse("seller_update_order", args=[order.id]),
			{
				"payment_status": "paid",
				"delivery_status": "shipped",
				"tracking_reference": "TRK-123",
				"delivery_note": "Handed to courier",
			},
		)
		order.refresh_from_db()
		self.assertEqual(order.payment_status, "paid")
		self.assertEqual(order.delivery_status, "shipped")
		self.assertEqual(order.tracking_reference, "TRK-123")

	def test_buyer_can_cancel_online_order_and_refund_is_pending(self):
		self.client.force_login(self.buyer_user)
		self.client.post(reverse("buy_book", args=[self.book.id]), {**self.order_data("online"), "payment_confirmed": "1"})
		order = BookOrder.objects.get()

		response = self.client.post(reverse("cancel_order", args=[order.id]), {"cancellation_reason": "Changed my mind"})

		self.assertRedirects(response, reverse("user_profile"))
		order.refresh_from_db()
		self.assertEqual(order.status, "cancelled")
		self.assertEqual(order.refund_status, "pending")
		self.assertEqual(order.cancellation_reason, "Changed my mind")

	def test_buyer_must_provide_cancellation_reason(self):
		self.client.force_login(self.buyer_user)
		self.client.post(reverse("buy_book", args=[self.book.id]), self.order_data("cash"))
		order = BookOrder.objects.get()

		self.client.post(reverse("cancel_order", args=[order.id]), {"cancellation_reason": "   "})

		order.refresh_from_db()
		self.assertEqual(order.status, "placed")
		self.assertEqual(order.cancellation_reason, "")

	def test_only_buyer_can_cancel_and_packed_order_cannot_be_cancelled(self):
		self.client.force_login(self.buyer_user)
		self.client.post(reverse("buy_book", args=[self.book.id]), self.order_data("cash"))
		order = BookOrder.objects.get()

		self.client.force_login(self.seller_user)
		response = self.client.post(reverse("cancel_order", args=[order.id]))
		self.assertEqual(response.status_code, 404)

		self.client.force_login(self.buyer_user)
		order.delivery_status = "packed"
		order.save(update_fields=["delivery_status"])
		self.client.post(reverse("cancel_order", args=[order.id]))
		order.refresh_from_db()
		self.assertEqual(order.status, "placed")

	def test_order_cannot_be_cancelled_after_three_days(self):
		self.client.force_login(self.buyer_user)
		self.client.post(reverse("buy_book", args=[self.book.id]), self.order_data("cash"))
		order = BookOrder.objects.get()
		BookOrder.objects.filter(id=order.id).update(created_at=timezone.now() - timedelta(days=4))

		self.client.post(reverse("cancel_order", args=[order.id]))
		order.refresh_from_db()
		self.assertEqual(order.status, "placed")

	def test_draft_and_price_less_books_are_hidden_from_browse(self):
		self.book.status = "draft"
		self.book.save(update_fields=["status"])
		self.client.get(reverse("browse"))
		self.assertNotContains(self.client.get(reverse("browse")), self.book.title)

		self.book.status = "published"
		self.book.price = None
		self.book.save(update_fields=["status", "price"])
		self.assertNotContains(self.client.get(reverse("browse")), self.book.title)

	def test_seller_can_save_price_less_book_as_draft(self):
		self.client.force_login(self.seller_user)
		response = self.client.post(
			reverse("seller_add_book"),
			self.book_form_data(action="save_draft", price=""),
		)

		self.assertRedirects(response, reverse("all_sell_books"))
		draft = Book.objects.get(isbn="9876543210123")
		self.assertEqual(draft.status, "draft")
		self.assertIsNone(draft.price)

	def test_seller_cannot_publish_book_without_price(self):
		self.client.force_login(self.seller_user)
		response = self.client.post(
			reverse("seller_add_book"),
			self.book_form_data(action="publish", price=""),
		)

		self.assertRedirects(response, reverse("seller_add_book"))
		self.assertFalse(Book.objects.filter(isbn="9876543210123").exists())

	def test_seller_cannot_delete_book_with_existing_order(self):
		self.client.force_login(self.buyer_user)
		self.client.post(
			reverse("buy_book", args=[self.book.id]), self.order_data("cash")
		)

		self.client.force_login(self.seller_user)
		response = self.client.post(
			reverse("seller_delete_book", args=[self.book.id])
		)

		self.assertRedirects(response, reverse("all_sell_books"))
		self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

	def test_seller_can_delete_exchange_listing_with_existing_order(self):
		exchange_book = ExchangeBook.objects.create(
			book=self.book,
			seller=self.seller,
			condition="good",
		)
		self.client.force_login(self.buyer_user)
		self.client.post(
			reverse("buy_book", args=[self.book.id]), self.order_data("cash")
		)

		self.client.force_login(self.seller_user)
		response = self.client.post(
			reverse("seller_delete_exchange", args=[exchange_book.id])
		)

		self.assertRedirects(response, reverse("all_exchange_books"))
		self.assertFalse(ExchangeBook.objects.filter(pk=exchange_book.pk).exists())
		self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

	def test_deleting_missing_exchange_listing_redirects_instead_of_404(self):
		self.client.force_login(self.seller_user)

		response = self.client.post(
			reverse("seller_delete_exchange", args=[99999])
		)

		self.assertRedirects(response, reverse("all_exchange_books"))

	def test_seller_can_remove_offer_without_deleting_book(self):
		self.book.offer_percentage = 10
		self.book.save(update_fields=["offer_percentage"])
		self.client.force_login(self.seller_user)

		response = self.client.post(
			reverse("seller_edit_book", args=[self.book.id]),
			{"action": "remove_offer"},
		)

		self.assertRedirects(response, reverse("all_sell_books"))
		self.book.refresh_from_db()
		self.assertIsNone(self.book.offer_percentage)
		self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

	def order_data(self, payment_method):
		return {
			"payment_method": payment_method,
			"recipient_name": "Test Buyer",
			"recipient_phone": "9999999999",
			"address_line1": "123 Test Street",
			"city": "Ahmedabad",
			"state": "Gujarat",
			"postal_code": "380001",
		}

	def book_form_data(self, action, price):
		return {
			"action": action,
			"title": "Draft Book",
			"author": "Draft Author",
			"isbn": "9876543210123",
			"publisher": "Draft Publisher",
			"publication_year": "2024",
			"category": "fiction",
			"language": "English",
			"page_count": "120",
			"description": "A draft book description.",
			"price": price,
			"sale_type": "normal",
		}
