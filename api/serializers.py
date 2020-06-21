from rest_framework import serializers

from api.models import CustomUser, Role, ConnectionType, Connection, IndustryType, PciDss, BaselineConfiguration, \
    CsvModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'roles', 'is_active']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class ConnectionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectionType
        fields = '__all__'


class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = '__all__'


class IndustryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndustryType
        fields = '__all__'


class PciDssSerializer(serializers.ModelSerializer):
    class Meta:
        model = PciDss
        fields = '__all__'


class BaselineConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaselineConfiguration
        fields = '__all__'


class CsvModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CsvModel
        fields = '__all__'
