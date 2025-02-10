from rest_framework import serializers
from .models import Invoice, Comment, Leading, Supler, Status, Specialist

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class LeadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leading
        fields = '__all__'

class SuplerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supler
        fields = '__all__'

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

class SpecialistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialist
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    supplier = SuplerSerializer()
    comment = CommentSerializer()
    specialist = SpecialistSerializer()
    leading = LeadingSerializer()
    status = StatusSerializer()

    class Meta:
        model = Invoice
        fields = '__all__'
