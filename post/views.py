from django.shortcuts import render, get_object_or_404
from rest_framework import status
from .models import Category, Comment, Post
from .serializer import PostSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters
from rest_framework import permissions, viewsets
from .permissions import IsAuthorOrReadOnly
from .serializer import (
    CommentReadSerializer,
    CommentWriteSerializer,

)


# Create your views here.


class PostList(APIView):
    def get(self, request):
        queryset = Post.objects.all()
        serializer = PostSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        user = self.request.user
        if user.is_staff:
            serializer = PostSerializer(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        if user.is_superuser:
            serializer = PostSerializer(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PostDetails(APIView):
    def get(self, request, id):
        user = self.request.user
        if user.is_superuser:
            post = get_object_or_404(Post, pk=id)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        if user.is_staff:
            post = Post.objects.only('id').get(user_id=self.request.user)
            serializer = PostSerializer(post)
            return Response(serializer.data)

    def put(self, request, id):
        user = self.request.user
        if user.is_superuser:
            post = get_object_or_404(Post, pk=id)
            serializer = PostSerializer(post, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        if user.is_staff:
            post = Post.objects.only('id').get(user_id=self.request.user)
            serializer = PostSerializer(post, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def delete(self, request, id):
        user = self.request.user
        if user.is_superuser:
            post = get_object_or_404(Post, pk=id)
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if user.is_staff:
            post = Post.objects.only('id').get(user_id=self.request.user.id)
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(viewsets.ModelViewSet):
    """
    CRUD comments for a particular post
    """

    queryset = Comment.objects.all()

    def get_queryset(self):
        res = super().get_queryset()
        post_id = self.kwargs.get("post_id")
        return res.filter(post__id=post_id)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return CommentWriteSerializer

        return CommentReadSerializer

    def get_permissions(self):
        if self.action in ("create",):
            self.permission_classes = (permissions.IsAuthenticated,)
        elif self.action in ("update", "partial_update", "destroy"):
            self.permission_classes = (IsAuthorOrReadOnly,)
        else:
            self.permission_classes = (permissions.AllowAny,)

        return super().get_permissions()


class LikePostAPIView(APIView):
    """
    Like, Dislike a post
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        user = request.user
        post = get_object_or_404(Post, pk=pk)

        if user in post.likes.all():
            post.likes.remove(user)

        else:
            post.likes.add(user)

        return Response(status=status.HTTP_200_OK)
