from django.urls import path, include

# from .views import MenuItemView, SingleMenuItemView, CartView, OrderView, UserView
# from .views import MenuItemView, SingleMenuItemView, UserView, DeliveryCrewView, DeliveryCrewDeleteView, CartView
from .views import MenuItemView, SingleMenuItemView, ManagerUserView, ManagerSingleUserVeiw, ManagerDeliveryCrewView, ManagerSingleDeliveryCrewVeiw, CartView

urlpatterns = [
    path('menu-items', MenuItemView.as_view()),
    path('menu-items/<int:pk>', SingleMenuItemView.as_view()),
    path('groups/manager/users', ManagerUserView.as_view()),
    path('groups/manager/users/<int:pk>', ManagerSingleUserVeiw.as_view()),
    path('groups/delivery-crew/users', ManagerDeliveryCrewView.as_view()),
    path('groups/delivery-crew/users/<int:pk>',
         ManagerSingleDeliveryCrewVeiw.as_view()),
    path('cart/menu-items', CartView.as_view()),
    # path('orders', OrderView.as_view()),
    # path('orders/<int:pk>', OrderView.as_view()),
]
