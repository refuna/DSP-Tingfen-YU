
import psycopg2
import pandas as pd


# create a class for the database
class database():
    # create a function to connect to the database using psycopg2
    def __init__(self):
        self.db = psycopg2.connect(
            host="localhost",
            database="TTTest",
            user="postgres",
            password="ytf"
        )

    # insert a single prediction in the database
    def insert_single(self, db, req):
        # create an instance for the cursor
        cursor = db.cursor()
        try:
            # execute the query
            cursor.execute(req)
            db.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            db.rollback()
            cursor.close()
            return 1
        cursor.close()

    # get all the predictions from the database
    def get_all(self, db, req):
        # create an instance for the cursor
        cursor = db.cursor()
        try:
            # execute the query
            cursor.execute(req)
            # create a list to store the results
            li = []
            for row in cursor.fetchall(): # fetch all the results
                li.append(row)
            db.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            db.rollback()
            cursor.close()
            return 1 # return 1 if there is an error
        cursor.close()
        return li # return the list of results

    # store one prediction in the database
    def create_HousePricePrediction_single(self, predict_df):
        # create the sql query
        query = "INSERT into \"hp1\"(overallqual, grlivarea, garagearea, totalbsmtsf, street, lotshape, saleprice) values('%s',%s,%s,%s,'%s','%s',%s)" % (
            predict_df['OverallQual'][0], predict_df['GrLivArea'][0], predict_df['GarageArea'][0], predict_df['TotalBsmtSF'][0],
            predict_df['Street'][0] , predict_df['LotShape'][0], predict_df['SalePrice'][0])
        self.insert_single(self.db, query) # store one prediction in the database

        return predict_df

    # store multiple predictions in the database
    def create_HousePricePredictions_df(self, predict_df):
        # create the sql query
        for i in range(0, predict_df.shape[0]-1):
            query = "INSERT into \"hp1\"(overallqual, grlivarea, garagearea, totalbsmtsf, street, lotshape, saleprice) values('%s',%s,%s,%s,'%s','%s',%s)" % (
                predict_df.iloc[i]['OverallQual'], predict_df.iloc[i]['GrLivArea'], predict_df.iloc[i]['GarageArea'], predict_df.iloc[i]['TotalBsmtSF'],
                predict_df.iloc[i]['Street'], predict_df.iloc[i]['LotShape'],predict_df.iloc[i]['SalePrice'])
            self.insert_single(self.db, query) # store the prediction one by one in the database

        return predict_df

    # get all the predictions from the database
    def get_housePrices_predictions(self):
        query = "select * from  \"hp1\""
        return self.get_all(self.db, query)

