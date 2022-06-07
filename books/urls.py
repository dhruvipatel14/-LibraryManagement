from django.urls import path

from books.views import BookView

urlpatterns = [
    path("books", BookView.as_view()),
    path("books/<int:book_id>", BookView.as_view())
]
