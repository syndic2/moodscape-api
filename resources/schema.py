import graphene

from .user.queries import UserQuery
from .user.mutations import UserMutation

from .auth.queries import AuthQuery
from .auth.mutations import AuthMutation

from .activity.queries import ActivityQuery
from .activity.mutations import ActivityMutation

from .mood.queries import MoodQuery
from .mood.mutations import MoodMutation

from .habit.queries import HabitQuery
from .habit.mutations import HabitMutation

from .psychology_disease.queries import PsychologyDiseaseQuery
from .psychology_disease.mutations import PsychologyDiseaseMutation

from .article.queries import ArticleQuery
from .article.mutations import ArticleMutation

from .theme.queries import ThemeQuery
from .theme.mutations import ThemeMutation

from .feedback.queries import FeedbackQuery
from .feedback.mutations import FeedbackMutation

class QueryRoot(
        UserQuery,
        MoodQuery,
        HabitQuery,
        ActivityQuery,
        PsychologyDiseaseQuery, 
        ArticleQuery,
        ThemeQuery,
        FeedbackQuery,
        graphene.ObjectType
    ):
    pass

class MutationRoot(
        UserMutation,
        MoodMutation,
        HabitMutation,
        ActivityMutation,
        PsychologyDiseaseMutation,
        ArticleMutation,
        ThemeMutation,
        FeedbackMutation,
        graphene.ObjectType
    ):
    pass

class AuthQueryRoot(AuthQuery, graphene.ObjectType):
    pass

class AuthMutationRoot(AuthMutation, graphene.ObjectType):
    pass

main_schema= graphene.Schema(query= QueryRoot, mutation= MutationRoot)
auth_schema= graphene.Schema(query= AuthQueryRoot, mutation= AuthMutationRoot)