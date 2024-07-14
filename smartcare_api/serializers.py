from rest_framework import serializers
from django.contrib.auth import get_user_model
from authentication.models import UserProfile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email', 
                  'date_of_birth', 'user_type', 'address', 'latitude', 'longitude', 
                  'patient_type', 'specialty')
        extra_kwargs = {'patient_type': {'required': False}, 'specialty': {'required': False}}

    def validate(self, data):
        user_type = data.get('user_type')
        patient_type = data.get('patient_type')
        specialty = data.get('specialty')

        if user_type == 'patient' and not patient_type:
            raise serializers.ValidationError("Patient type is required for patients.")
        elif user_type == 'doctor' and not specialty:
            raise serializers.ValidationError("Specialty is required for doctors.")
        elif user_type not in ['patient', 'doctor', 'nurse']:
            raise serializers.ValidationError("Invalid user type.")

        return data

    def create(self, validated_data):
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.update_or_create(
            user=user,
            defaults={'latitude': latitude, 'longitude': longitude}
        )
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super(UserSerializer, self).update(instance, validated_data)