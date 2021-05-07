import graphene

from extensions import mongo
from .types import AppFeedbackInput, AppFeedback

class FeedbackQuery(graphene.AbstractType):
    all_app_feedback= graphene.List(AppFeedback, fields= graphene.Argument(AppFeedbackInput))

    def resolve_all_app_feedback(self, info, fields):
        feedbacks= list(mongo.db.app_feedbacks.find(dict(fields)))

        def to_app_feedback_type(document):
            feedback= AppFeedback(document)

            return feedback

        return map(to_app_feedback_type, feedbacks)