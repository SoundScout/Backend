from rest_framework import serializers
from datetime import date
from .models import Subscription, SubscriptionPlan

# ----------------------------
# Subscription Plan Serializer
# ----------------------------
class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'max_upload_rate', 'price']


# ----------------------------
# Subscription Serializer
# ----------------------------
class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.all(),
        source='plan',
        write_only=True
    )

    class Meta:
        model = Subscription
        fields = [
            'id',
            'artist',
            'plan',
            'plan_id',
            'status',
            'end_subscription',
            'created_at',
            'max_upload_rate',
            'price',
            'is_active',
        ]
        read_only_fields = ['artist', 'created_at', 'max_upload_rate', 'price', 'is_active']

    def validate(self, data):
        # If updating an existing subscription...
        if self.instance:
            # Check if it's already expired
            expiry = self.instance.end_subscription
            if expiry and expiry < date.today():
                raise serializers.ValidationError(
                    "Cannot modify a subscription that has already expired."
                )
        return data

    def create(self, validated_data):
        # Ensure artist is set from context/user, if needed
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['artist'] = request.user.artist  # or however you link artist
        return super().create(validated_data)