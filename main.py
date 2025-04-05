from typing import List, Dict
from enum import Enum
from abc import ABC, abstractmethod

class SeatType(Enum):
    GOLD = "gold"
    PREMIUM = "premium"

class SeatStatus(Enum):
    BOOKED = "booked"
    AVAILABLE = "available"

class User:
    def __init__(self, id: str, name: str, contact_no: str):
        self.id = id
        self.name = name
        self.contact_no = contact_no

class Admin(User):
    def __init__(self, id: str, name: str, contact_no: str):
        super().__init__(id, name, contact_no)
        self.shows: List["Show"] = []
        self.movies: List["Movie"] = []

    def add_show(self, show: "Show"):
        self.shows.append(show)

    def remove_show(self, show: "Show"):
        self.shows.remove(show)

    def add_movie(self, movie: "Movie"):
        self.movies.append(movie)

    def remove_movie(self, movie: "Movie"):
        self.movies.remove(movie)

class Customer(User):
    def __init__(self, id: str, name: str, contact_no: str):
        super().__init__(id, name, contact_no)
        self.bookings: Dict[str, "Booking"] = {}

    def create_booking(self, booking: "Booking"):
        self.bookings[booking.id] = booking

class UserFactory:
    @staticmethod
    def create_user(user_type: str, id: str, name: str, contact_no: str):
        if user_type == "admin":
            return Admin(id, name, contact_no)
        elif user_type == "customer":
            return Customer(id, name, contact_no)
        else:
            raise ValueError("Invalid user type")

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

class Booking:
    def __init__(self, id: str, seat: "Seat"):
        self.id = id
        self.seat = seat

class Movie:
    def __init__(self, id: str, name: str, title: str, duration: int, genre: str, shows: List["Show"]):
        self.id = id
        self.name = name
        self.title = title
        self.duration = duration
        self.genre = genre
        self.shows = shows

class Show:
    def __init__(self):
        self.id = None
        self.start_time = None
        self.end_time = None
        self.seats = None

class ShowBuilder(ABC):
    @abstractmethod
    def set_show_id(self, id: str):
        pass

    @abstractmethod
    def set_show_time(self, start_time: str, end_time: str):
        pass

    @abstractmethod
    def set_show_seats(self, seats: List["Seat"]):
        pass

    @abstractmethod
    def build(self):
        pass

class MovieShowBuilder(ShowBuilder):
    def __init__(self):
        self.show = Show()

    def set_show_id(self, id: str):
        self.show.id = id

    def set_show_time(self, start_time: str, end_time: str):
        self.show.start_time = start_time
        self.show.end_time = end_time

    def set_show_seats(self, seats: List["Seat"]):
        self.show.seats = seats

    def build(self):
        return self.show

class Director:
    def __init__(self, builder: ShowBuilder):
        self.builder = builder

    def build_show(self, id, start_time, end_time, seats):
        self.builder.set_show_id(id)
        self.builder.set_show_time(start_time, end_time)
        self.builder.set_show_seats(seats)
        return self.builder.build()

class Seat:
    def __init__(self, id: str, row: int, col: int, seat_type: SeatType, status: SeatStatus, pricing_strategy: PricingStrategy):
        self.id = id
        self.row = row
        self.col = col
        self.seat_type = seat_type
        self.status = status
        self.pricing_strategy = pricing_strategy

    def get_price(self, base_price: float) -> float:
        return self.pricing_strategy.get_price(base_price)

class Theater:
    def __init__(self, id: str, shows: List["Show"], address: "Address"):
        self.id = id
        self.shows = shows
        self.address = address

class Address:
    def __init__(self, id: str, address_line: str, city: str, state: str, pin: int):
        self.id = id
        self.address_line = address_line
        self.city = city
        self.state = state
        self.pin = pin

class SingletonMeta(type):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super().__call__(*args, **kwargs)
        return cls._instance[cls]

class TheaterRegistry(metaclass=SingletonMeta):
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.theaters: Dict[str, Theater] = {}
        self._initialized = True

    def add_theater(self, theater: Theater):
        self.theaters[theater.id] = theater

    def get_theater(self, theater_id: str):
        return self.theaters.get(theater_id)

if __name__ == "__main__":
    # Create users
    admin = UserFactory.create_user("admin", "1", "AdminUser", "9999999999")
    customer = UserFactory.create_user("customer", "2", "CustUser", "8888888888")

    # Create seats
    seats = [
        Seat("S1", 1, 1, SeatType.GOLD, SeatStatus.AVAILABLE, GoldPricingStrategy()),
        Seat("S2", 1, 2, SeatType.PREMIUM, SeatStatus.AVAILABLE, PremiumPricingStrategy())
    ]

    # Build a show
    builder = MovieShowBuilder()
    director = Director(builder)
    show = director.build_show("show1", "10:00", "12:00", seats)

    # Add show and movie
    admin.add_show(show)
    movie = Movie("M1", "Inception", "Inception", 150, "Sci-Fi", [show])
    admin.add_movie(movie)

    # Register theater
    address = Address("A1", "123 Main St", "Gotham", "NY", 12345)
    theater = Theater("T1", [show], address)
    registry = TheaterRegistry()
    registry.add_theater(theater)

    # Customer books a seat
    booking = Booking("B1", seats[0])
    customer.create_booking(booking)

    print("Customer bookings:", customer.bookings)
    print("Theater from registry:", registry.get_theater("T1").id)
