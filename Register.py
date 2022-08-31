from Database import Database
from pymongo import GEOSPHERE
class Register:
    def __init__(self, users):
        self.users = users
       

    def insertCutomers(self, data):
        customer_col = Database("TaxisandCustomers", "customers").getCollection()
        customer_col.delete_many({})
        try:
            customer_col.insert_many(data)
            customer_col.create_index([('location', GEOSPHERE)])
            return {'statusCode':200,'msg':"Successful insertion of Customer"}
        except:
            return {'statusCode':400,'msg':"Failed Operation"}

    def insertTaxis(self, data):
        booking_col = Database("TaxisandCustomers", "booking").getCollection()
        res = booking_col.delete_many({})
        taxi_col = Database("TaxisandCustomers", "taxis").getCollection()
        taxi_col.delete_many({})
        try:
            taxi_col.insert_many(data)
            taxi_col.create_index([('location', GEOSPHERE)])
            return {'statusCode':200,'msg':"Successful insertion of Taxis"}
        except:
            return {'statusCode':400,'msg':"Failed Operation"}
