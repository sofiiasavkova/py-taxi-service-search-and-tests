from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Manufacturer, Car, Driver
from taxi.forms import CarForm


class SearchTestCase(TestCase):

    def setUp(self):
        # Створення користувача для тестування
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )

        # Авторизація користувача
        self.client.login(username="testuser", password="password123")

        # Створення тестових виробників, машин і водіїв
        self.manufacturer1 = Manufacturer.objects.create(
            name="Toyota", country="Japan"
        )
        self.manufacturer2 = Manufacturer.objects.create(
            name="Honda", country="Japan"
        )

        self.car1 = Car.objects.create(
            model="Corolla", manufacturer=self.manufacturer1
        )
        self.car2 = Car.objects.create(
            model="Civic", manufacturer=self.manufacturer2
        )

        self.driver1 = Driver.objects.create(
            username="johndoe",
            first_name="John",
            last_name="Doe",
            license_number="ABC12345"
        )
        self.driver2 = Driver.objects.create(
            username="janesmith",
            first_name="Jane",
            last_name="Smith",
            license_number="XYZ98765"
        )

    def test_search_manufacturer(self):
        # Тестуємо пошук за виробником
        response = self.client.get(
            reverse("taxi:manufacturer-list"), {"name": "Toyota"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Toyota")
        self.assertNotContains(response, "Honda")

    def test_search_car(self):
        # Тестуємо пошук за моделлю машини
        response = self.client.get(
            reverse("taxi:car-list"), {"model": "Corolla"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Corolla")
        self.assertNotContains(response, "Civic")

    def test_search_driver(self):
        # Тестуємо пошук за іменем водія
        response = self.client.get(
            reverse("taxi:driver-list"), {"username": "John"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "johndoe")
        self.assertNotContains(response, "janesmith")

    def test_search_multiple_terms(self):
        # Тестуємо пошук з кількома термінами
        response = self.client.get(
            reverse("taxi:manufacturer-list"), {"name": "Toyota Honda"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Toyota")
        self.assertContains(response, "Honda")

    def test_empty_search(self):
        # Тестуємо порожній пошук
        response = self.client.get(
            reverse("taxi:manufacturer-list"), {"name": ""}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Toyota")
        self.assertContains(response, "Honda")

    def test_search_not_found(self):
        # Тестуємо пошук, коли нічого не знайдено
        response = self.client.get(
            reverse("taxi:car-list"), {"model": "Tesla"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no cars in taxi")


class TestLoginRequired(TestCase):
    def test_login_required_for_driver_create(self):
        response = self.client.get(
            reverse("taxi:driver-create")
        )
        self.assertRedirects(
            response, "/accounts/login/?next=/drivers/create/"
        )


class CarFormTestCase(TestCase):
    def setUp(self):
        manufacturer = Manufacturer.objects.create(name="Tesla", country="USA")
        get_user_model().objects.create_user(
            username="testuser", password="password"
        )
        self.car = Car.objects.create(
            model="Model S", manufacturer=manufacturer
        )

    def test_car_form_valid(self):
        form = CarForm(
            data={
                "model": "Model X",
                "manufacturer": self.car.manufacturer.id,
                "drivers": [self.car.id]
            }
        )
        self.assertTrue(form.is_valid())

    def test_car_form_invalid(self):
        form = CarForm(
            data={
                "model": "",
                "manufacturer": self.car.manufacturer.id,
                "drivers": [self.car.id]
            }
        )
        self.assertFalse(form.is_valid())
