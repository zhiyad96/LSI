from django.utils import timezone
from rest_framework import serializers
from .models import PatientMaster


def generate_mrn():
    prefix = 'MRN'
    year = timezone.now().year
    base = f"{prefix}{year}"
    last = PatientMaster.objects.filter(mrn__startswith=base).order_by('-mrn').first()
    if last and last.mrn[len(base):].isdigit():
        next_number = int(last.mrn[len(base):]) + 1
    else:
        next_number = 1
    return f"{base}{str(next_number).zfill(5)}"


class PatientSerializer(serializers.ModelSerializer):
    auto_generate_mrn = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = PatientMaster
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def validate_mrn(self, value):
        if value == "":
            return value
        if self.instance and self.instance.mrn == value:
            return value
        if PatientMaster.objects.filter(mrn=value).exists():
            raise serializers.ValidationError("MRN already exists.")
        return value

    def validate(self, attrs):
        auto_generate = attrs.get('auto_generate_mrn', False)
        mrn = attrs.get('mrn', '').strip()
        if self.instance:
            if 'mrn' in attrs and not mrn:
                if auto_generate:
                    attrs['mrn'] = generate_mrn()
                else:
                    raise serializers.ValidationError({'mrn': 'MRN is required unless auto-generate is enabled.'})
        else:
            if not mrn:
                if auto_generate:
                    attrs['mrn'] = generate_mrn()
                else:
                    raise serializers.ValidationError({'mrn': 'MRN is required unless auto-generate is enabled.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('auto_generate_mrn', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('auto_generate_mrn', None)
        return super().update(instance, validated_data)
