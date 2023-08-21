from rest_framework import serializers
from users.models import User
from properties.models import (Property, PropertyOwnership, PROPERTY_STAGE_CHOICES,
    MODERATION_STATUS_CHOICES, CHOICES_FOR_PROPERTY_OWNERSHIP_STATUS)
from utils.constants import STAGES_OF_KYC_VERIFICATION


class KycVerificationSerializer(serializers.Serializer):

    KYC_STATUS_CHOICES = [
        ("approved", "Approval status"),
        ("rejected", "Rejection status"),
    ]

    user_id = serializers.IntegerField(required=True)
    kyc_verification_stage = serializers.ChoiceField(STAGES_OF_KYC_VERIFICATION, required=True)
    kyc_verification_status = serializers.ChoiceField(KYC_STATUS_CHOICES, required=True)

    class Meta:
        fields = ['user_id', 'kyc_verification_stage', 'kyc_verification_status']

    def validate(self, attrs):
        user_id = attrs.get('user_id', '')
        kyc_stage = attrs.get('kyc_verification_stage', '')
        verification_status = attrs.get('kyc_verification_status', '')

        users = User.objects.filter(id=user_id)

        if len(users) <= 0:
            raise serializers.ValidationError(
                "resource not found")

        user = users[0]
        user.stages_of_kyc_verification[kyc_stage] = verification_status == self.KYC_STATUS_CHOICES[0][0]
        user.stages_of_profile_completion[kyc_stage] = verification_status == self.KYC_STATUS_CHOICES[0][0]
        user.save()

        return user

class PropertyModerationSerializer(serializers.Serializer):

    property_id = serializers.UUIDField(required=True)
    status = serializers.ChoiceField(MODERATION_STATUS_CHOICES, required=True)

    class Meta:
        fields = ['property_id', 'status']

    def validate(self, attrs):
        property_id = attrs.get('property_id', '')
        status = attrs.get('status', '')

        prop = Property.objects.filter(id=property_id)

        if len(prop) <= 0:
            raise serializers.ValidationError(
                "resource not found")

        prop = prop[0]
        prop.moderation_status = status
        prop.save()

        return attrs


class ReviewPropertyOwnershipSerializer(serializers.Serializer):
    request_id = serializers.IntegerField(required=True)
    status = serializers.ChoiceField(CHOICES_FOR_PROPERTY_OWNERSHIP_STATUS, required=True)

    class Meta:
        fields = ['request_id', 'status']

    def validate(self, attrs):
        request_id = attrs.get('request_id', '')
        status = attrs.get('status', '')

        ownership_req = PropertyOwnership.objects.filter(id=request_id)
        if len(ownership_req) <= 0:
            raise serializers.ValidationError(
                "resource not found")

        properties = Property.objects.filter(id=ownership_req[0].property_id)
        if len(properties) <= 0:
            raise serializers.ValidationError(
                "resource not found")

        if status == CHOICES_FOR_PROPERTY_OWNERSHIP_STATUS[2][0]:

            # check if property has already been approved for another user
            existing_ownership_req = PropertyOwnership.objects.filter(property_id=ownership_req[0].property_id,
                                                                      user_type=ownership_req[0].user_type,
                                                                      status=CHOICES_FOR_PROPERTY_OWNERSHIP_STATUS[2][
                                                                          0])
            if len(existing_ownership_req) > 0:
                raise serializers.ValidationError(
                    "property has been approved for another user")

            # change property stage from 'listing' to 'marketplace' to 'sold'
            if properties[0].stage == PROPERTY_STAGE_CHOICES[0][0]:
                properties[0].stage = PROPERTY_STAGE_CHOICES[1][0]
            elif properties[0].stage == PROPERTY_STAGE_CHOICES[1][0]:
                properties[0].stage = PROPERTY_STAGE_CHOICES[2][0]

            properties[0].percentage_sold += ownership_req[0].percentage_ownership
            properties[0].save()

        ownership_req[0].status = status
        ownership_req[0].save()

        return attrs