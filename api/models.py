from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class Role(models.Model):
    name = models.CharField(max_length=256)
    is_active = models.BooleanField(default=True)


class CustomUser(AbstractUser):
    roles = models.ManyToManyField(Role)


class ConnectionType(models.Model):
    name = models.CharField(max_length=256)


class Connection(models.Model):
    name = models.CharField(max_length=256)
    type = models.ForeignKey(ConnectionType, on_delete=models.CASCADE)
    connection_string = models.TextField()
    connection_id = models.CharField(max_length=256)
    connection_password = models.CharField(max_length=512)


class IndustryType(models.Model):
    name = models.CharField(max_length=256, default='', blank=False)


class PciDss(models.Model):
    name = models.CharField(max_length=256, default='', blank=False)


class BaselineConfiguration(models.Model):
    per_app_cloud = models.IntegerField()
    per_bus_act_outsource = models.IntegerField()
    per_it_outsource = models.IntegerField()
    org_scale = models.IntegerField()
    global_footprint = models.BooleanField()
    dom_loc_workforce = models.IntegerField()
    industry_type = models.ForeignKey(IndustryType, on_delete=models.CASCADE)
    pci_dss = models.ManyToManyField(PciDss)
    priv_reg_app = models.BooleanField()


class CsvModel(models.Model):
    col1 = models.CharField(max_length=256, default='', blank=True)
    col2 = models.CharField(max_length=256, default='', blank=True)
    col3 = models.CharField(max_length=256, default='', blank=True)
    col4 = models.CharField(max_length=256, default='', blank=True)
    col5 = models.CharField(max_length=256, default='', blank=True)
