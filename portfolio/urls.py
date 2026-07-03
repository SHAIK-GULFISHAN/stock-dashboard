from django.urls import path
from .views import portfolio, stocks_market, stock_detail

urlpatterns = [
    path('', portfolio, name='portfolio'),
    path('market/', stocks_market, name='stocks_market'),
    path('stock/<str:symbol>/', stock_detail, name='stock_detail'),
]