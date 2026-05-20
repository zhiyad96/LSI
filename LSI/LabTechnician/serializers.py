from rest_framework import serializers
from .models import TestMenuMaster, AssayMaster, OrderTransaction, Results
from accounts.models import UserMaster
from Physician.serializers import PatientSerializer

class TestMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestMenuMaster
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class AssaySerializer(serializers.ModelSerializer):
    menu_name = serializers.CharField(source='menu.menu_name', read_only=True)
    menu_code = serializers.CharField(source='menu.menu_code', read_only=True)

    class Meta:
        model = AssayMaster
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class ResultSerializer(serializers.ModelSerializer):
    assay_name = serializers.CharField(source='assay.assay_name', read_only=True)
    assay_code = serializers.CharField(source='assay.assay_code', read_only=True)
    entered_by_name = serializers.CharField(source='entered_by.full_name', read_only=True)

    class Meta:
        model = Results
        fields = '__all__'
        read_only_fields = ['entered_at', 'created_at', 'updated_at', 'entered_by']

class OrderTransactionSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.patient_name', read_only=True)
    patient_mrn = serializers.CharField(source='patient.mrn', read_only=True)
    ordered_by_name = serializers.CharField(source='ordered_by.full_name', read_only=True)
    collected_by_name = serializers.CharField(source='collected_by.full_name', read_only=True)
    results = ResultSerializer(many=True, read_only=True)
    
    class Meta:
        model = OrderTransaction
        fields = '__all__'
        read_only_fields = ['order_no', 'ordered_at', 'ordered_by', 'collected_by', 'collected_at', 'received_by', 'received_at', 'created_at', 'updated_at', 'order_status']
