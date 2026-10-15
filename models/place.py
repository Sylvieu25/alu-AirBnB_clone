#!/usr/bin/python3
"""Defines the Place class."""
from models.base_model import BaseModel


class Place(BaseModel):
    """Represents a place to stay.

    Attributes:
        city_id (str): the id of the City of the place.
        user_id (str): the id of the User who owns the place.
        name (str): the name of the place.
        description (str): the description of the place.
        number_rooms (int): the number of rooms.
        number_bathrooms (int): the number of bathrooms.
        max_guest (int): the maximum number of guests.
        price_by_night (int): the price for one night.
        latitude (float): the latitude of the place.
        longitude (float): the longitude of the place.
        amenity_ids (list): the ids of the Amenities of the place.
    """

    city_id = ""
    user_id = ""
    name = ""
    description = ""
    number_rooms = 0
    number_bathrooms = 0
    max_guest = 0
    price_by_night = 0
    latitude = 0.0
    longitude = 0.0
    amenity_ids = []
