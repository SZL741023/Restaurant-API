from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from datetime import date
from django.contrib.auth.models import User, Group
from .models import MenuItem, Cart, Order, OrderItem
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
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer_price = CartPriceSerializer(data=request.data)
        if serializer_price.is_valid():
            item_id = request.data['menuitem']
            item = get_object_or_404(MenuItem, id=item_id)
            quantity = request.data['quantity']
            price = int(quantity) * item.price
            try:
                Cart.objects.create(user=request.user,
                                    menuitem_id=item_id,
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


class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.request.method == 'GET' or 'POST':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsManager, IsDeliveryCrew]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.request.user.groups.filter(
                name='Manager').exists() or self.request.user.is_superuser:
            return Order.objects.all()
        elif self.request.user.groups.filter(name='Delivery Crew'):
            return Order.objects.filter(delivery_crew=self.request.user)
        else:
            return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        item_count = Cart.objects.all().filter(user=request.user).count()
        if item_count == 0:
            return HttpResponse("There is no item in the Cart.")
        data = request.data.copy()
        total_price = self.get_total_price()
        data['total'] = total_price
        data['date'] = date.today()
        order_serializer = OrderSerializer(data=data)
        if order_serializer.is_valid():
            order_serializer.save()
            order_ID = order_serializer['id']

            cart_items = Cart.objects.all().filter(user=request.user)

            for item in cart_items.values():
                OrderItem.objects.create(order=request.user,
                                         menuitem_id=item['menuitem_id'],
                                         quantity=item['quantity'],
                                         unit_price=item['unit_price'],
                                         price=item['price'])
            cart_items.delete()
            return JsonResponse(status=201, data=order_serializer.data)

    def get_total_price(self):
        total = 0
        cart = Cart.objects.all().filter(user=self.request.user)
        for item in cart.values():
            total += item['price']
        return total


class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer

    def get_permissions(self):
        order = Order.objects.get(pk=self.kwargs['pk'])
        if self.request.method == 'GET' and self.request.user == order.user:
            permission_classes = [IsAuthenticated]
        elif self.request.method == 'PUT' or self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, IsManager]
        else:
            permission_classes = [IsAuthenticated, IsDeliveryCrew, IsManager]
        return [permission() for permission in permission_classes]

    def get_queryset(self, *args, **kwargs):
        return Order.objects.filter(pk=self.kwargs['pk'])

    def put(self, request, *args, **kwargs):
        serializer_order = OrderSerializer(data=request.data)
        if serializer_order.is_valid():
            order_id = self.kwargs['pk']
            crew_id = request.data['delivery_crew']
            order = get_object_or_404(Order, pk=order_id)
            crew = get_object_or_404(User, pk=crew_id)
            order.delivery_crew = crew
            order.save()
            return JsonResponse(
                status=201,
                data={
                    'message':
                    f'{str(crew.username)} will ship the order {str(order_id)}'
                })

    def patch(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order.status = 1
        order.save()
        return JsonResponse(
            status=201,
            data={'message': f'The order {order.id} status is changed.'})

    def delete(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order_id = str(order['id'])
        order.delete()
        return JsonResponse(
            status=201, data={'message': f'The order {order_id} is deleted.'})
