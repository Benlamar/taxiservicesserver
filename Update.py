import json
from Database import Database

class Update:
    def __init__(self) -> None:
        self.customer_col = Database("TaxisandCustomers", "customers").getCollection()
        self.taxi_col = Database("TaxisandCustomers", "taxis").getCollection()
        self.booking_col = Database("TaxisandCustomers", "booking").getCollection()


    def updateTaxisLocation(self):
        try:
            data = []
            for taxi in self.taxi_col.find():
                data.append({'id':taxi['id'], 'name':taxi['name'], 'status':taxi['status'],
                        'type':taxi['type'],
                        'location':taxi['location'], 'timestamp':str(taxi['timestamp'])})
            return {"statusCode":200, "msg":data}
        except:
            return {"statusCode":404, "msg":"Data not found"}
    
    def updateCustomerLocation(self):
        try:
            data = []
            for customer in self.customer_col.find():
                data.append({'id':customer['id'], 'name':customer['name'], 
                        'location':customer['location'], 'status':customer['status'],
                        'timestamp':str(customer['timestamp'])})
            return {"statusCode":200, "msg":data}

        except:
            return {"statusCode":404, "msg":"Data not found"}

    def updateTripData(self, customer_id):
        customer = list(self.customer_col.find({'id':customer_id}))
        customer_name = customer[0]['name']

        try:
            data = []
            for book in self.booking_col.find({'customer':customer_name, 'status':{'$ne':'Completed'}}):                
                data.append({'name':book['taxi'], 
                        'location':book['taxi_location'], 'type':book['type']})
            return {"statusCode":200, "msg":data}
        except:
            return {"statusCode":404, "msg":"Data not found"}