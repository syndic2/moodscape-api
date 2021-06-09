import graphene

from .auth.queries import AuthQuery
from .auth.mutations import AuthMutation

from .user.queries import UserQuery
from .user.mutations import UserMutation

from .activity.queries import ActivityQuery

from .user_activities.queries import UserActivitiesQuery
from .user_activities.mutations import UserActivitiesMutation

from .article.queries import ArticleQuery
from .article.mutations import ArticleMutation

from .user_articles.queries import UserArticlesQuery
from .user_articles.mutations import UserArticlesMutation

from .feedback.queries import FeedbackQuery
from .feedback.mutations import FeedbackMutation

class QueryRoot(
        UserQuery, 
        ActivityQuery, 
        ArticleQuery,
        UserActivitiesQuery,
        UserArticlesQuery,
        FeedbackQuery,
        graphene.ObjectType
    ):
    pass

class MutationRoot(
        UserMutation, 
        ArticleMutation,
        UserActivitiesMutation,
        UserArticlesMutation,
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