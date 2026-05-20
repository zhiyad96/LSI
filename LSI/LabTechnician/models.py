from django.db import models

class TestMenuMaster(models.Model):
    menu_code = models.CharField(max_length=20, unique=True)
    menu_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'test_menu_master'

    def __str__(self):
        return f"{self.menu_name} ({self.menu_code})"

class AssayMaster(models.Model):
    menu = models.ForeignKey(TestMenuMaster, on_delete=models.CASCADE, db_column='menu_id', related_name='assays', help_text="References test_menu_master — parent test category")
    assay_code = models.CharField(max_length=20, unique=True)
    assay_name = models.CharField(max_length=150)
    sample_type = models.CharField(max_length=50)
    tat_hours = models.SmallIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    normal_range = models.CharField(max_length=100, null=True, blank=True)
    unit = models.CharField(max_length=40, null=True, blank=True)
    status = models.CharField(max_length=10, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assay_master'

    def __str__(self):
        return f"{self.assay_name} ({self.assay_code})"

class OrderTransaction(models.Model):
    class Status(models.IntegerChoices):
        ORDERED = 1, 'Ordered'
        COLLECTED = 2, 'Collected'
        IN_LAB = 3, 'In-Lab'
        COMPLETED = 4, 'Completed'

    order_no = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey("Physician.PatientMaster", on_delete=models.CASCADE, db_column='patient_id', related_name='orders')
    ordered_by = models.ForeignKey("accounts.UserMaster", on_delete=models.CASCADE, db_column='ordered_by', related_name='orders_placed')
    ordered_at = models.DateTimeField()
    collected_by = models.ForeignKey("accounts.UserMaster", on_delete=models.SET_NULL, null=True, blank=True, db_column='collected_by', related_name='samples_collected')
    collected_at = models.DateTimeField(null=True, blank=True)
    received_by = models.ForeignKey("accounts.UserMaster", on_delete=models.SET_NULL, null=True, blank=True, db_column='received_by', related_name='samples_received')
    received_at = models.DateTimeField(null=True, blank=True)
    order_status = models.SmallIntegerField(choices=Status.choices, default=Status.ORDERED)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_transaction'

    def __str__(self):
        return self.order_no

class Results(models.Model):
    order = models.ForeignKey(OrderTransaction, on_delete=models.CASCADE, db_column='order_id', related_name='results')
    assay = models.ForeignKey(AssayMaster, on_delete=models.CASCADE, db_column='assay_id', related_name='results')
    result_value = models.CharField(max_length=200)
    unit = models.CharField(max_length=40, null=True, blank=True)
    normal_range = models.CharField(max_length=100, null=True, blank=True)
    flag = models.CharField(max_length=10, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    entered_by = models.ForeignKey("accounts.UserMaster", on_delete=models.CASCADE, db_column='entered_by', related_name='results_entered')
    entered_at = models.DateTimeField()
    verified_by = models.ForeignKey("accounts.UserMaster", on_delete=models.SET_NULL, null=True, blank=True, db_column='verified_by', related_name='results_verified')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'results'

    def __str__(self):
        return f"Result for {self.assay.assay_name} (Order: {self.order.order_no})"

