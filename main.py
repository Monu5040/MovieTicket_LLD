from typing import List, Dict
from enum import Enum
from abc import ABC, abstractmethod
import random

# ------------------ ENUMS ------------------ #
class SeatType(Enum):
    GOLD = "gold"
    PREMIUM = "premium"

class SeatStatus(Enum):
    BOOKED = "booked"
    AVAILABLE = "available"

# ------------------ USERS ------------------ #
class User:
    def __init__(self, id: str, name: str, contact_no: str):
        self.id = id
        self.name = name
        self.contact_no = contact_no

class Admin(User):
    def __init__(self, id: str, name: str, contact_no: str):
        super().__init__(id, name, contact_no)
        self.shows: List["Show"] = []
        self.movies: List["Movies"] = []

    def add_show(self, show: "Show"):
        self.shows.append(show)

    def remove_show(self, show: "Show"):
        self.shows.remove(show)

    def add_movie(self, movie: "Movies"):
        self.movies.append(movie)

    def remove_movie(self, movie: "Movies"):
        self.movies.remove(movie)

class Customer(User):
    def __init__(self, id: str, name: str, contact_no: str):
        super().__init__(id, name, contact_no)
        self.bookings: Dict[str, "Booking"] = {}

    def create_booking(self, booking: "Booking"):
        self.bookings[booking.id] = booking

    def cancel_booking(self, booking_id: str):
        if booking_id in self.bookings:
            booking = self.bookings[booking_id]
            for seat in booking.seats:
                seat.status = SeatStatus.AVAILABLE
            del self.bookings[booking_id]
            print(f"❎ Booking {booking_id} has been cancelled.")
        else:
            print(f"⚠️ No booking found with ID {booking_id}")

# ------------------ FACTORY ------------------ #
class UserFactory:
    @staticmethod
    def create_user(user_type: str, id: str, name: str, contact_no: str):
        if user_type == "admin":
            return Admin(id, name, contact_no)
        elif user_type == "customer":
            return Customer(id, name, contact_no)
        else:
            raise ValueError("Invalid user type")

# ------------------ STRATEGY ------------------ #
class PricingStrategy(ABC):
    @abstractmethod
    def get_price(self, base_price: float) -> float:
        pass

class GoldPricingStrategy(PricingStrategy):
    def get_price(self, base_price: float) -> float:
        return base_price * 1.5

class PremiumPricingStrategy(PricingStrategy):
    def get_price(self, base_price: float) -> float:
        return base_price * 2

# ------------------ PAYMENT SIMULATION ------------------ #
class PaymentGateway:
    @staticmethod
    def process_payment(amount: float) -> bool:
        print(f"💳 Processing payment of ₹{amount:.2f}...")
        return random.choice([True, True, True, False])

# ------------------ BOOKING ------------------ #
class Booking:
    def __init__(self, id: str, customer: Customer, show: "Show", seats: List["Seat"], base_price: float):
        self.id = id
        self.customer = customer
        self.show = show
        self.seats = seats
        self.total_price = sum(seat.get_price(base_price) for seat in seats)
        for seat in seats:
            seat.status = SeatStatus.BOOKED

# ------------------ MOVIE ------------------ #
class Movies:
    def __init__(self, id: str, name: str, title: str, duration: int, genre: str, shows: List["Show"]):
        self.id = id
        self.name = name
        self.title = title
        self.duration = duration
        self.genre = genre
        self.shows = shows

# ------------------ BUILDER ------------------ #
class Show:
    def __init__(self):
        self.id = None
        self.movie_id = None
        self.start_time = None
        self.end_time = None
        self.seats = None

class ShowBuilder(ABC):
    @abstractmethod
    def set_show_id(self, id: str): pass
    @abstractmethod
    def set_show_time(self, start_time: str, end_time: str): pass
    @abstractmethod
    def set_show_seats(self, seats: List["Seat"]): pass
    @abstractmethod
    def build(self): pass

class MovieShowBuilder(ShowBuilder):
    def __init__(self):
        self.show = Show()

    def set_show_id(self, id: str): self.show.id = id
    def set_show_time(self, start_time: str, end_time: str):
        self.show.start_time = start_time
        self.show.end_time = end_time
    def set_show_seats(self, seats: List["Seat"]): self.show.seats = seats
    def build(self): return self.show

class Director:
    def __init__(self, builder: ShowBuilder):
        self.builder = builder

    def build_show(self, id, start_time, end_time, seats):
        self.builder.set_show_id(id)
        self.builder.set_show_time(start_time, end_time)
        self.builder.set_show_seats(seats)
        return self.builder.build()

# ------------------ SEAT ------------------ #
class Seat:
    def __init__(self, id: str, row: int, col: int, seat_type: SeatType,
                 status: SeatStatus, pricing_strategy: PricingStrategy):
        self.id = id
        self.row = row
        self.col = col
        self.seat_type = seat_type
        self.status = status
        self.pricing_strategy = pricing_strategy

    def get_price(self, base_price: float) -> float:
        return self.pricing_strategy.get_price(base_price)

# ------------------ THEATER ------------------ #
class Address:
    def __init__(self, id: str, address_line: str, city: str, state: str, pin: int):
        self.id = id
        self.address_line = address_line
        self.city = city
        self.state = state
        self.pin = pin

class Theater:
    def __init__(self, id: str, shows: List[Show], address: Address):
        self.id = id
        self.shows = shows
        self.address = address

# ------------------ SINGLETON SERVICES ------------------ #
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class TheaterService(metaclass=SingletonMeta):
    def __init__(self):
        self.theaters: Dict[str, Theater] = {}

    def add_theater(self, theater: Theater):
        self.theaters[theater.id] = theater

    def search_by_city(self, city: str) -> List[Theater]:
        return [t for t in self.theaters.values() if t.address.city.lower() == city.lower()]

    def search_by_pin(self, pin: int) -> List[Theater]:
        return [t for t in self.theaters.values() if t.address.pin == pin]

class MovieService(metaclass=SingletonMeta):
    def __init__(self):
        self.movies: Dict[str, Movies] = {}

    def add_movie(self, movie: Movies):
        self.movies[movie.id] = movie

    def search_by_name(self, name: str) -> List[Movies]:
        return [m for m in self.movies.values() if m.name.lower() == name.lower()]

    def search_by_genre(self, genre: str) -> List[Movies]:
        return [m for m in self.movies.values() if m.genre.lower() == genre.lower()]

class ShowService(metaclass=SingletonMeta):
    def __init__(self):
        self.shows: Dict[str, Show] = {}

    def add_show(self, show: Show):
        self.shows[show.id] = show

    def search_by_movie(self, movie_id: str) -> List[Show]:
        return [s for s in self.shows.values() if s.movie_id == movie_id]

    def search_by_time(self, start_time: str) -> List[Show]:
        return [s for s in self.shows.values() if s.start_time == start_time]

# ------------------ FACADE ------------------ #
class SearchFacade:
    def __init__(self, movie_service, show_service, theater_service):
        self.movie_service = movie_service
        self.show_service = show_service
        self.theater_service = theater_service

    def search_movies_by_name(self, name: str):
        return self.movie_service.search_by_name(name)

    def search_movies_by_genre(self, genre: str):
        return self.movie_service.search_by_genre(genre)

    def search_shows_by_movie(self, movie_id: str):
        return self.show_service.search_by_movie(movie_id)

    def search_shows_by_time(self, start_time: str):
        return self.show_service.search_by_time(start_time)

    def search_theaters_by_city(self, city: str):
        return self.theater_service.search_by_city(city)

    def search_theaters_by_pin(self, pin: int):
        return self.theater_service.search_by_pin(pin)

# ------------------ MAIN ------------------ #
def main():
    # Setup
    admin = UserFactory.create_user("admin", "A1", "AdminUser", "1234567890")
    customer = UserFactory.create_user("customer", "C1", "CustomerUser", "9876543210")

    seats = [
        Seat("S1", 1, 1, SeatType.GOLD, SeatStatus.AVAILABLE, GoldPricingStrategy()),
        Seat("S2", 1, 2, SeatType.PREMIUM, SeatStatus.AVAILABLE, PremiumPricingStrategy()),
    ]

    builder = MovieShowBuilder()
    director = Director(builder)
    show = director.build_show("SH1", "10:00", "12:30", seats)

    movie = Movies("M1", "Inception", "Inception", 148, "Sci-Fi", [show])
    admin.add_show(show)
    admin.add_movie(movie)

    movie_service = MovieService(); movie_service.add_movie(movie)
    show_service = ShowService(); show.movie_id = movie.id; show_service.add_show(show)
    address = Address("ADDR1", "101 Movie Street", "Gotham", "NY", 10001)
    theater = Theater("T1", [show], address)
    theater_service = TheaterService(); theater_service.add_theater(theater)

    facade = SearchFacade(movie_service, show_service, theater_service)

    print("🔍 Searching for movie by name 'Inception'")
    for m in facade.search_movies_by_name("Inception"):
        print(f"🎬 Movie: {m.title}, Genre: {m.genre}, Duration: {m.duration} mins")

    print("\n⏰ Searching shows by start time '10:00'")
    for s in facade.search_shows_by_time("10:00"):
        print(f"🎟️ Show ID: {s.id}, Start Time: {s.start_time}, End Time: {s.end_time}")
        for seat in s.seats:
            print(f"  💺 Seat {seat.id}: {seat.seat_type.value} - ₹{seat.get_price(200):.2f}, Status: {seat.status.name}")

    print("\n🏢 Searching theaters in 'Gotham'")
    for t in facade.search_theaters_by_city("Gotham"):
        print(f"🎭 Theater ID: {t.id}, Address: {t.address.address_line}, City: {t.address.city}")

    # Booking
    base_price = 200.0
    print("\n🧾 Customer trying to book an available seat...")

    available_seats = [seat for seat in show.seats if seat.status == SeatStatus.AVAILABLE]
    if available_seats:
        selected_seats = [available_seats[0]]
        total_price = sum(seat.get_price(base_price) for seat in selected_seats)

        if PaymentGateway.process_payment(total_price):
            booking = Booking("B1", customer, show, selected_seats, base_price)
            customer.create_booking(booking)
            print(f"✅ Booking Successful! Booking ID: {booking.id}")
            print(f"   🎫 Seats Booked: {[seat.id for seat in booking.seats]}")
            print(f"   💰 Total Price: ₹{booking.total_price:.2f}")
        else:
            print("❌ Payment failed. Booking not completed.")
    else:
        print("❌ No available seats to book.")

    print("\n📄 Customer Booking History:")
    for b_id, b in customer.bookings.items():
        print(f"🆔 {b_id} | Show: {b.show.id} | Seats: {[s.id for s in b.seats]} | Total: ₹{b.total_price:.2f}")

    print("\n🔄 Cancelling booking 'B1'...")
    customer.cancel_booking("B1")

    print("\n📄 Updated Booking History:")
    for b_id, b in customer.bookings.items():
        print(f"🆔 {b_id} | Show: {b.show.id} | Seats: {[s.id for s in b.seats]} | Total: ₹{b.total_price:.2f}")

if __name__ == "__main__":
    main()
