from Database import Database
from pymongo import GEOSPHERE

class BookingTaxi:
    def __init__(self) -> None:
        self.taxi_col = Database("TaxisandCustomers", "taxis").getCollection()
        self.booking_col = Database("TaxisandCustomers", "booking").getCollection()
        self.customer_col = Database("TaxisandCustomers", "customers").getCollection()
        
    def findNearestTaxi(self,location,type):
        data = []
        query = {'location': {"$near": location}, "type":type, "status":{"$eq":"Available"}}
        for taxi in self.taxi_col.find(query).limit(3):
            data.append({'id':taxi['id'], 'name':taxi['name'],
                    'type':taxi['type'],'status':taxi['status'],
                    'location':taxi['location'], 'timestamp':str(taxi['timestamp'])})
        return data

    def setNotification(self, customerData, taxiData):
        try:
            self.customer_col.update_one({"id":customerData['id']},{"$set":{"status":"Requesting"}})
            for taxi in range(len(taxiData)):
                self.taxi_col.update_one({"id":taxiData[taxi]['id']},{"$set":{"status":"Pending"}})
                self.booking_col.insert_one({
                        "booking_id":"Booking_"+taxiData[taxi]['name'],
                        "taxi_id":taxiData[taxi]['id'],
                        "taxi":taxiData[taxi]['name'],
                        "customer":customerData["name"],
                        "status":taxiData[taxi]["status"],
                        "type":taxiData[taxi]["type"],
                        "timestamp":customerData["timestamp"],
                        "source":customerData["location"],
                        "destination":customerData["destination"],
                        "taxi_location":taxiData[taxi]["location"]})
            self.booking_col.create_index([("destination",GEOSPHERE)])
            return True
        except Exception as e:
            print(e)
            return False

    def getNotification(self,id):
        notification = {}
        noti = list(self.booking_col.find({'taxi_id':id, 'status':{'$ne':'Completed'}}))
        if len(noti) > 0:
            notification = noti[0]
            notification.pop('_id')
        
        return notification


    def deleteBooking(self, booking_id):
        self.booking_col.update_one({'booking_id':booking_id['booking_id'], 'status':{'$ne':'Completed'}}, {'$set':{'status':'Accepted'}})
        book = list(self.booking_col.find({'booking_id':booking_id['booking_id']}))
        customer_name = book[0]['customer']
        taxi_id=book[0]['taxi_id']

        self.taxi_col.update_one({'id':taxi_id}, 
                {'$set':{
                    'location':{'type':'Point','coordinates':book[0]['source']['coordinates']}}})
        

        self.customer_col.update_one({'name':customer_name}, {'$set':{'status':'Accepted'}})
        pending = self.booking_col.find({'booking_id':{"$ne":booking_id['booking_id']}})
        for taxi in pending:
            self.taxi_col.update_one({'id':taxi['taxi_id']}, {'$set':{'status':'Available'}})
            self.booking_col.delete_one({'taxi_id':taxi['taxi_id'], 'customer':taxi['customer']})
        
        return "Trip request accepted"
