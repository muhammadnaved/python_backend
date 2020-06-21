import io
import random

import ldap
import pandas
from django.contrib.auth import authenticate, login
from django.db import IntegrityError, transaction
from knox.views import LoginView as KnoxLoginView

# Create your views here.
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
import pyodbc
import cx_Oracle
import splunklib.client as client
import pysnow

from api.models import CustomUser, Role, ConnectionType, Connection, BaselineConfiguration, IndustryType, PciDss, \
    CsvModel
from api.serializers import UserSerializer, RoleSerializer, ConnectionTypeSerializer, ConnectionSerializer, \
    IndustryTypeSerializer, PciDssSerializer, BaselineConfigurationSerializer, CsvModelSerializer
from backend.settings import DEBUG


class CheckDBConnectionView(APIView):
    permission_classes = [AllowAny]

    def check_mssql_connection(self, connection_string):
        try:
            pyodbc.connect(connection_string,
                           driver="/usr/local/lib/libtdsodbc.so" if DEBUG is True else '/usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so')
        except pyodbc.Error as ex:
            return False
        return True

    def check_ldap_connection(self, connection_string, user, password):
        if connection_string.startswith("ldaps"):
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_SERVER)

        try:
            conn = ldap.initialize(connection_string)
            conn.simple_bind_s(user, password)
        except ldap.LDAPError as ex:
            return False

        return True

    def check_oracle_connection(self, connection_string):

        try:
            con = cx_Oracle.connect(connection_string)
            con.close()
        except cx_Oracle.DatabaseError as e:
            return False

        return True

    def check_splunk_connection(self, connection_string, user_name, password):

        try:
            client.connect(host=connection_string, username=user_name, password=password)
        except Exception as ex:
            return False

        return True

    def check_servicenow_connection(self, connection_string, user_name, password):
        try:
            pysnow.Client(instance=connection_string, user=user_name, password=password)
        except Exception as ex:
            return False

        return True


    def post(self, request):
        attrs = request.data
        type = attrs.get('type')
        connection_string = attrs.get('connection_string')
        user_name = attrs.get('user_name')
        password = attrs.get('password')

        if not type or not connection_string:
            return Response("Missing Fields.", status=status.HTTP_400_BAD_REQUEST)

        con_type = ConnectionType.objects.get(pk=type)

        if "MS SQL" == con_type.name:
            return Response(self.check_mssql_connection(connection_string))
        elif "LDAP" == con_type.name:
            if not user_name or not password:
                return Response("Missing Fields.", status=status.HTTP_400_BAD_REQUEST)
            return Response(self.check_ldap_connection(connection_string, user_name, password))
        elif "ORACLE" == con_type.name:
            return Response(self.check_oracle_connection(connection_string))
        elif "Splunk" == con_type.name:
            if not user_name or not password:
                return Response("Missing Fields.", status=status.HTTP_400_BAD_REQUEST)
            return Response(self.check_splunk_connection(connection_string, user_name, password))

        return Response(False)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        del data['roles']
        user = CustomUser.objects.create(**data)
        user.set_password(request.data.get('password'))
        user.roles.set(request.data.get('roles'))
        user.save()
        return Response(UserSerializer(user).data)


class RoleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class ConnectionTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ConnectionType.objects.all()
    serializer_class = ConnectionTypeSerializer


class ConnectionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer


class AccountView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ConfigurationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        config = BaselineConfiguration.objects.get()
        industry_types = IndustryType.objects.all()
        pci_dss = PciDss.objects.all()

        if config is None:
            return Response("Config not exist", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "industry_types": IndustryTypeSerializer(industry_types, many=True).data,
            "pci_dss": PciDssSerializer(pci_dss, many=True).data,
            "configuration": BaselineConfigurationSerializer(config).data,
        })

    def post(self, request):
        config = BaselineConfiguration.objects.get()

        if config is None:
            return Response("Config not exist", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = BaselineConfigurationSerializer(config, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CsvModelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        csv_data = CsvModel.objects.all()
        return Response(CsvModelSerializer(csv_data, many=True).data)

    def post(self, request):
        try:
            csv_content = request.data['content']
        except KeyError:
            return Response("CSV content missing", status=status.HTTP_400_BAD_REQUEST)

        #try:
        csv_data = pandas.read_csv(io.StringIO(csv_content), encoding="utf8", sep=None, engine='python')
        #except Exception ex:
        #    return Response("Can not read CSV", status=status.HTTP_400_BAD_REQUEST)

        col_count = len(csv_data.columns)

        if 5 != col_count:
            return Response("Number of columns don't match", status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                CsvModel.objects.all().delete()

                for index, row in csv_data.iterrows():
                    CsvModel.objects.create(col1=row.array[0],
                                            col2=row.array[1],
                                            col3=row.array[2],
                                            col4=row.array[3],
                                            col5=row.array[4])
        except IntegrityError:
            return Response("Error on DB persist")

        new_data = CsvModel.objects.all()
        return Response(CsvModelSerializer(new_data, many=True).data)


class CisoDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        graph_category = ["Identify", "Protect", "Detect", "Respond", "Recover"]
        graph_sub_category = ["Asset Management", "Business Environment", "Governance", "Risk Assessment", "Risk Management Strategy"]
        return Response({
            "budgetSummary": {
                "budgetYTD": 5.3,
                "budgetVariance": 0.7,
                "spentYTD": 4.3
            },
            "projectSummary": {
                "atRisk": random.randint(1, 20),
                "onHold": random.randint(1, 20),
                "delayed": random.randint(1, 20),
                "onTrack": random.randint(1, 20),
            },
            "cyberRiskData": (
                {
                    "title": category,
                    "percent": random.randint(0, 100),
                    "subData": (
                        {
                            "title": sub_category,
                            "percent": random.randint(0, 100),
                            "subData": (
                                {
                                    "title": "Graph " + str(i),
                                    "percent": random.randint(0, 100)
                                }
                                for i in range(1, random.randint(3, 9))
                            )
                        }
                        for sub_category in graph_sub_category
                    )
                }
                for category in graph_category
            ),
            "insiderThreat": {
                "threat1": (
                    {
                        "title": "Item " + str(i),
                        "percent": random.randint(0, 100),
                        "color": "#" + ''.join(random.choice('0123456789abcdef') for n in range(0, 6))
                    }
                    for i in range(0, 5)
                ),
                "threat2": (
                    {
                        "label": "Item " + str(i),
                        "value": random.randint(30, 100),
                        "color": "#" + ''.join(random.choice('0123456789abcdef') for n in range(0, 6))
                    }
                    for i in range(1, 6)
                ),
                "threat3": (
                    {
                        "label": "Item " + str(i),
                        "value": random.randint(30, 100),
                        "color": "#" + ''.join(random.choice('0123456789abcdef') for n in range(0, 6))
                    }
                    for i in range(1, 6)
                )
            },
            "issues": {
                "gauge": {
                    "title": "Graph 1",
                    "percent": random.randint(0, 100)
                },
                "issues": {
                    "critical": random.randint(0, 30),
                    "high": random.randint(0, 30),
                    "medium": random.randint(0, 30)
                },
                "graph": (
                    {
                        "label": "Item" + str(i),
                        "critical": random.randint(0, 30),
                        "high": random.randint(0, 30),
                        "medium": random.randint(0, 30)
                    }
                    for i in range(1, 5)
                )
            }
        })


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        attrs = request.data
        username = attrs.get('userName')
        password = attrs.get('password')

        if not username or not password:
            return Response("Missing Fields", status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request=request, username=username, password=password)

        if not user:
            return Response("Credential is not correct.", status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        return super(LoginView, self).post(request, format=None)
