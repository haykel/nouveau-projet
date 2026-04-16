from django.urls import path
from app.stocks import views

urlpatterns = [
    path("stocks/search/", views.search_stocks),
    path("stocks/top10/", views.stock_top10),
    path("markets/indices/", views.market_indices),
    path("stocks/<str:ticker>/history/", views.stock_history),
    path("stocks/<str:ticker>/indicators/", views.stock_indicators),
    path("stocks/<str:ticker>/score/", views.stock_score),
    path("stocks/<str:ticker>/", views.stock_detail),
]
