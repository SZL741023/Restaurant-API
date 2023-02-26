from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from .models import MenuItem, Cart, Order
from .serializers import MenuItemSerializer, CartSerializer, CartPriceSerializer, OrderSerializer, UserSerializer
from .permissions import IsManager, IsDeliveryCrew

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
# Create your views here.


class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method != "GET":
            permission_classes = [IsManager]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method != "GET":
            permission_classes = [IsManager]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


class ManagerUserView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = UserSerializer
    permission_classes = [IsManager]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username.is_valid():
            user = get_object_or_404(User, username=username)
            group = Group.objects.get(name="Manager")
            group.user_set.add(user)
            return JsonResponse(
                status=201,
                data={'message': 'User added to Manager Group successfully'})


class ManagerSingleUserVeiw(generics.RetrieveDestroyAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = UserSerializer
    permission_classes = [IsManager]

    def delete(self, request, *args, **kwargs):
        id = kwargs['pk']
        user = get_object_or_404(User, pk=id)
        group = Group.objects.get(name='Manager')
        group.user_set.remove(user)
        return JsonResponse(status=201,
                            data={'message', 'User delete from Manager Group'})


class ManagerDeliveryCrewView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Delivery Crew')
    serializer_class = UserSerializer
    permission_classes = [IsManager]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username.is_valid():
            user = get_object_or_404(User, username=username)
            group = Group.objects.get(name="Delivery Crew")
            group.user_set.add(user)
            return JsonResponse(
                status=201,
                data={
                    'message': 'User added to Delivery Crew Group successfully'
                })


class ManagerSingleDeliveryCrewVeiw(generics.RetrieveDestroyAPIView):
    queryset = User.objects.filter(groups__name='Delivery Crew')
    serializer_class = UserSerializer
    permission_classes = [IsManager]

    def delete(self, request, *args, **kwargs):
        id = kwargs['pk']
        user = get_object_or_404(User, pk=id)
        group = Group.objects.get(name='Delivery Crew')
        group.user_set.remove(user)
        return JsonResponse(
            status=201,
            data={'message', 'User delete from Delivery Crew Group.'})


class CartView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer_price = CartPriceSerializer(request.data)
        if serializer_price.is_valid():
            item_id = request.data['menuitem']
            item = get_object_or_404(MenuItem, id=item_id)
            quantity = request.data['quantity']
            price = int(quantity) * item.price
            try:
                Cart.objects.create(user=self.user,
                                    menuitem=item_id,
                                    quantity=quantity,
                                    unit_price=item.price,
                                    price=price)
            except:
                return JsonResponse(
                    status=409,
                    data={'message': 'Item can not add, please try again.'})
        return JsonResponse(status=201,
                            data={'message': 'Item added in the Cart.'})

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return JsonResponse(status=201,
                            data={'message': 'All items are deleted.'})
