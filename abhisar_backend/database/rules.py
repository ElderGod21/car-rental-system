class Rules:
    @staticmethod
    def add(client, db, collection, data):
        return client[db][collection].insert_one(data).inserted_id
    @staticmethod
    def get(client, db, collection, query):
        return client[db][collection].find_one(query)
    
    @staticmethod
    def get_all(client, db, collection, query):
        return list(client[db][collection].find(query))
    
    @staticmethod
    def update(client, db, collection, query, data):
        return client[db][collection].update_one(query, {"$set": data})
    
    @staticmethod
    def delete(client, db, collection, query):
        return client[db][collection].delete_one(query)