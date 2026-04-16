from rest_framework import serializers


class QuoteSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    current_price = serializers.FloatField()
    change = serializers.FloatField(allow_null=True)
    change_percent = serializers.FloatField(allow_null=True)
    high = serializers.FloatField(required=False)
    low = serializers.FloatField(required=False)
    open = serializers.FloatField(required=False)
    previous_close = serializers.FloatField(required=False)
    timestamp = serializers.IntegerField(required=False)


class SearchResultSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    description = serializers.CharField()
    type = serializers.CharField()


class CandleSerializer(serializers.Serializer):
    timestamp = serializers.IntegerField()
    open = serializers.FloatField()
    high = serializers.FloatField()
    low = serializers.FloatField()
    close = serializers.FloatField()
    volume = serializers.IntegerField()


class CandlesResponseSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    candles = CandleSerializer(many=True)


class MarketIndexSerializer(serializers.Serializer):
    name = serializers.CharField()
    index_symbol = serializers.CharField()
    symbol = serializers.CharField()
    current_price = serializers.FloatField(allow_null=True)
    change = serializers.FloatField(allow_null=True)
    change_percent = serializers.FloatField(allow_null=True)
    error = serializers.CharField(required=False)
