from rest_framework import serializers
from users.models import User
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
                "user not found")

        user = users[0]
        user.stages_of_kyc_verification[kyc_stage] = verification_status == self.KYC_STATUS_CHOICES[0][0]
        user.stages_of_profile_completion[kyc_stage] = verification_status == self.KYC_STATUS_CHOICES[0][0]
        user.save()

        return user
