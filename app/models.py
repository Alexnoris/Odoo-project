from django.db import models

# Create your models here.
class StockQuant(models.Model):
    product_id = models.IntegerField()
    location_id = models.IntegerField()
    company_id = models.IntegerField(default=1)
    quantity = models.FloatField()
    reserved_quantity = models.FloatField(default=0.0)

    class Meta:
        db_table = 'stock_quant'