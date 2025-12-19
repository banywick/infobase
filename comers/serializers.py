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

    def validate_name(self, value):
        # Проверяем, существует ли поставщик с таким именем
        if Supler.objects.filter(name=value).exists():
            raise serializers.ValidationError("Поставщик с таким названием уже существует.")
        return value

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

class SpecialistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialist
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    supplier = SuplerSerializer(read_only=True)
    comment = CommentSerializer(read_only=True)
    specialist = SpecialistSerializer(read_only=True)
    leading = LeadingSerializer(read_only=True)
    status = StatusSerializer(read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'

class InvoiceCreateSerializer(serializers.ModelSerializer):
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supler.objects.all(),
        write_only=True
    )
    comment = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(),
        write_only=True
    )
    specialist = serializers.PrimaryKeyRelatedField(
        queryset=Specialist.objects.all(),
        write_only=True
    )
    leading = serializers.PrimaryKeyRelatedField(
        queryset=Leading.objects.all(),
        write_only=True
    )
    # Поле status не обязательно, так как в модели есть default=1
    status = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(),
        required=False,  # Не обязательное поле
        write_only=True
    )

    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'date', 'supplier', 'article', 'quantity',
            'name', 'comment', 'description_problem', 'specialist',
            'leading', 'unit', 'project', 'status','description','party'
        ]

class InvoiceSerializerSpecialist(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'



