from django.core.exceptions import BadRequest
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.permissions import CanModifyBooks, SafeJWTAuthentication
from books.models import Books
from books.serializers import BookSerializer


class BookView(APIView):
    authentication_classes = [SafeJWTAuthentication]
    permission_classes = [CanModifyBooks]

    @staticmethod
    @swagger_auto_schema(
        operation_description="Fetch all the books",
        responses={200: BookSerializer(many=True),
                   500: "There is some internal server error."})
    def get(request):
        try:
            books = Books.objects.all()
            books_data = BookSerializer(books, many=True).data
            return Response(books_data, status=status.HTTP_200_OK)
        except Exception as e:
            raise Exception(e)

    @staticmethod
    @swagger_auto_schema(
        operation_description="Add a new book",
        request_body=BookSerializer,
        responses={200: "A new book added successfully.",
                   400: "All the required information is not present.",
                   500: "There is some internal server error."})
    def post(request):
        try:
            book_serializer = BookSerializer(data=request.data)
            if book_serializer.is_valid():
                book_serializer.save()

                return Response("A new book added successfully.", status=status.HTTP_200_OK)
            else:
                raise BadRequest("All the required information is not present.")

        except BadRequest as e:
            raise BadRequest(e)
        except Exception as e:
            raise Exception(e)

    @staticmethod
    @swagger_auto_schema(
        operation_description="Update a book details",
        request_body=BookSerializer,
        responses={200: "A book details updated successfully.",
                   400: "All the required information is not present.",
                   404: "Book does not exists.",
                   500: "There is some internal server error."})
    def patch(request):
        try:
            if "book_id" not in request.data:
                raise BadRequest("All the required information is not present.")

            book = Books.objects.get(id=request.data["book_id"])

            update_book_serializer = BookSerializer(instance=book, data=request.data, partial=True)
            if update_book_serializer.is_valid():
                update_book_serializer.update(book, update_book_serializer.validated_data)

                return Response("A book details updated successfully.", status=status.HTTP_200_OK)
            else:
                raise BadRequest("All the required information is not present.")

        except Books.DoesNotExist as e:
            raise NotFound("Book does not exists.")
        except BadRequest as e:
            raise BadRequest(e)
        except Exception as e:
            raise Exception(e)

    @staticmethod
    @swagger_auto_schema(
        operation_description="Delete Book",
        responses={200: "A book deleted successfully.",
                   404: "Book does not exists.",
                   500: "There is some internal server error."})
    def delete(request, book_id):
        try:
            book = Books.objects.get(id=book_id)
            book.delete()

            return Response("A book deleted successfully.", status=status.HTTP_200_OK)

        except Books.DoesNotExist as e:
            raise NotFound("Book does not exists.", code=16404)
        except Exception as e:
            raise Exception(e)
