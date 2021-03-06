import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel, TitleSlugDescriptionModel


class BlogpostQueryset(models.QuerySet):
    def full_text_search(self, text):
        return self.extra(
            select={'rank': "ts_rank_cd(to_tsvector('english', blogposts_blogpost.title || ' ' || blogposts_blogpost.description || ' ' || blogposts_blogpost.content), plainto_tsquery(%s), 32)"},
            select_params=(text,),
            where=("to_tsvector('english', blogposts_blogpost.title || ' ' || blogposts_blogpost.description || ' ' || blogposts_blogpost.content) @@ plainto_tsquery(%s)",),
            params=(text,),
            order_by=('-rank',)
        )


class CommentQueryset(models.QuerySet):
    def full_text_search(self, text):
        return self.extra(
            select={'rank': "ts_rank_cd(to_tsvector('english', blogposts_comment.content), plainto_tsquery(%s), 32)"},
            select_params=(text,),
            where=("to_tsvector('english', blogposts_comment.content) @@ plainto_tsquery(%s)",),
            params=(text,),
            order_by=('-rank',)
        )


class UUIDIdMixin(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class AuthorMixin(models.Model):
    class Meta:
        abstract = True

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, editable=False, verbose_name=_('author'),
        related_name='%(app_label)s_%(class)s_author'
    )


class Blogpost(UUIDIdMixin, TimeStampedModel, TitleSlugDescriptionModel, AuthorMixin):
    content = models.TextField(_('content'), blank=True, null=True)

    objects = BlogpostQueryset.as_manager()

    def __str__(self):
        return self.title


class Comment(UUIDIdMixin, TimeStampedModel, AuthorMixin):
    blogpost = models.ForeignKey(
        Blogpost, editable=False, verbose_name=_('blogpost'), related_name='comments'
    )
    content = models.TextField(_('content'), max_length=255, blank=False, null=False)

    objects = CommentQueryset.as_manager()
