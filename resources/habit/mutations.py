import graphene
from flask_graphql_auth import get_jwt_identity, query_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from utilities.helpers import auto_increment_id
from ..utility_types import ResponseMessage
from .types import HabitInput, Habit, ProtectedUserHabit