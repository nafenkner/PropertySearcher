from flask import Flask, jsonify, request, render_template, redirect, url_for
from pymongo import MongoClient 
from bson.objectid import ObjectId
import bcrypt
from flask_cors import CORS
from flask_pymongo import PyMongo
import json

app=Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client['itemsDB']
collection = db['items']


@app.route('/') 
def home(): 
    return render_template('home.html') 

@app.route('/add_test_data', methods=['GET', 'POST'])
def add_test_data():
    if request.method == 'POST':
        db.products.insert_many(collection)
        message = "Test data added successfully"
    else:
        message = "Accessed via GET request. No data added."
    return render_template("add_test_data.html", message=message)


@app.route('/remove_test_data', methods=['GET', 'POST'])
def remove_test_data():
    if request.method == 'POST':
        db.products.delete_many({})
        message = "Test data removed successfully"
    else:
        message = "Accessed via GET request. No data removed."
    return render_template("remove_test_data.html", message=message)

@app.route('/results', methods=['GET']) 
def get_all_items(): 
    items = list(collection.find()) 
    for item in items: 
        item["_id"] = str(item["_id"]) 
    return render_template("results.html", items=items)

@app.route('/view', methods=['GET'])
def view_data():
    try:
        data = list(collection.find({}))
        for item in data:
            item["_id"] = str(item["_id"])
        return render_template('view_db.html', data=data)
    except Exception as e:
        return render_template('view_db.html', message='Error: {}'.format(e), data=None)
    

@app.route('/items/<field>', methods=['GET']) 
def items_with_field(field): 
    results = list(collection.find({field: {"$exists": True}}))   
    for item in results: 
        item["_id"] = str(item["_id"]) 
    return render_template("results.html", results=results, query="Specific Field")

@app.route("/<string:id>", methods=["DELETE"]) 
def delete_business(id): 
    result = collection.delete_one( { "_id" : ObjectId(id) } ) 
    if result.deleted_count == 1: 
        return jsonify({"Item was deleted."}), 204 
    else: 
        return jsonify({"error" : "Invalid ID" }), 404


@app.route('/less_than')
def less_than():
    results = collection.find({"age": {"$lt": 28}})
    return render_template('results.html', results=results, query="Less Than")

@app.route('/search', methods=['GET', 'POST'])
def search_items_by_name_pattern():
    try:
        if request.method == 'POST':
            query = request.form.get('query', '')
            # items = list(collection.find({"item_name": {"$regex": query, "$options": "i"}}))
            items = list(collection.find({"item_name": query}))
            for item in items:
                item["_id"] = str(item["_id"])
            return render_template('search.html', items=items, query=query)
        else:
            return render_template('search.html', items=[], query="")
    except Exception as e:
        return render_template('search.html', message=f"Error: {str(e)}", items=[], query="")
    
@app.route('/select_fields', methods=['GET', 'POST'])
def select_fields():
    if request.method == 'POST':
        try:
            fields = request.form.get('fields', '')
            field_list = [field.strip() for field in fields.split(',') if field.strip()]

            if not field_list:
                return render_template('select_fields.html', message="No fields specified.", data=[])

            projection = {field: 1 for field in field_list}
            results = list(collection.find({}, projection))

            for item in results:
                item["_id"] = str(item["_id"])

            return render_template('select_fields.html', message="Fields selected successfully.", data=results)
        except Exception as e:
            return render_template('select_fields.html', message=f"Error: {str(e)}", data=[])
    return render_template('select_fields.html', message="", data=[])

@app.route('/array_queries', methods=['GET', 'POST'])
def array_queries():
    if request.method == 'POST':
        try:
            query_type = request.form.get('query_type')
            array_field = request.form.get('array_field')
            value = request.form.get('value')
            criteria = request.form.get('criteria')
            values = request.form.get('values')

            if not query_type or not array_field:
                return render_template('array_queries.html', message="Array field and query type are required.", data=[])

            if query_type == 'match_values':
                results = list(collection.find({array_field: value}))
            elif query_type == 'match_criteria':
                results = list(collection.find({array_field: {"$elemMatch": json.loads(criteria)}}))
            elif query_type == 'match_all':
                results = list(collection.find({array_field: {"$all": json.loads(values)}}))
            else:
                return render_template('array_queries.html', message="Invalid query type.", data=[])

            for item in results:
                item["_id"] = str(item["_id"])

            if not results:
                return render_template('array_queries.html', message="Query executed successfully, but no matching data found.", data=[])

            return render_template('array_queries.html', message="Query executed successfully.", data=results)
        except Exception as e:
            return render_template('array_queries.html', message=f"Error: {str(e)}", data=[])
    return render_template('array_queries.html', message="", data=[])


@app.route('/aggregate', methods=['GET', 'POST'])
def aggregation_query():
    if request.method == 'POST':
        try:
            pipeline = request.form.get('pipeline', '[]')  # Get pipeline from form data
            pipeline = json.loads(pipeline)  # Convert string to JSON list

            if not pipeline or not isinstance(pipeline, list):
                return render_template('aggregate.html', message="Invalid aggregation pipeline.", results=[])

            results = list(collection.aggregate(pipeline))
            return render_template('aggregate.html', message="Aggregation successful.", results=results)
        except Exception as e:
            return render_template('aggregate.html', message=f"Error: {str(e)}", results=[])
    return render_template('aggregate.html', message="", results=[])

@app.route("/api/v1.0/books/<string:id>/reviews", methods=["POST"]) 
def add_new_review(id): 
    new_review = {  
        "_id" : ObjectId(), 
        "username" : request.form["username"], 
        "comment" : request.form["comment"], 
        "stars" : request.form["stars"] 
    } 

@app.route("/api/v1.0/businesses/<string:id>/reviews", methods=["GET"]) 
def fetch_all_reviews(id): 
    data_to_return = [] 
    business = collection.find_one({ "_id" : ObjectId(id) },{ "reviews" : 1, "_id" : 0 } ) 
    for review in business["reviews"]: 
        review["_id"] = str(review["_id"]) 
        data_to_return.append(review)
    return jsonify(data_to_return ), 200 

    collection.update_one( { "_id" : ObjectId(id) }, { "$push": { "reviews" : new_review } } ) 
    new_review_link = "http://localhost:5000/api/v1.0/businesses/"  + id +"/reviews/" + str(new_review['_id']) 
    return jsonify({ "url" : new_review_link } ), 201 

@app.route('/add', methods=['GET', 'POST'])
def add_new_document():
    if request.method == 'POST':
        try:
            name = request.form.get('item_name')
            category = request.form.get('category')
            price = request.form.get('price')

            if not name or not category or not price:
                return render_template('add.html', message="All fields (name, category, price) are required.")

            new_document = {
                "item_name": name,
                "category": category,
                "price": float(price)
            }

            collection.insert_one(new_document)

            return render_template('add.html', message="Document added successfully.")
        except Exception as e:
            return render_template('add.html', message=f"Error: {str(e)}")
    return render_template('add.html', message="")

@app.route('/update', methods=['GET', 'POST'])
def update_specific_document():
    if request.method == 'POST':
        try:
            name = request.form.get('item_name')
            category = request.form.get('category')
            price = request.form.get('price')

            if not name or not category or not price:
                return render_template('update.html', message="All fields (name, category, price) are required.")

            result = collection.update_one(
                {"item_name": name},
                {"$set": {"category": category, "price": float(price)}}
            )

            if result.matched_count == 0:
                return render_template('update.html', message="No document found with the given name.")

            return render_template('update.html', message="Document updated successfully.")
        except Exception as e:
            return render_template('update.html', message=f"Error: {str(e)}")
    return render_template('update.html', message="")

@app.route('/delete', methods=['GET', 'POST'])
def delete_specific_document():
    if request.method == 'POST':
        try:
            name = request.form.get('name')

            if not name:
                return render_template('delete.html', message="The name field is required.")

            result = collection.delete_one({"item_name": name})

            if result.deleted_count == 0:
                return render_template('delete.html', message="No document found with the given name.")

            return render_template('delete.html', message="Document deleted successfully.")
        except Exception as e:
            return render_template('delete.html', message=f"Error: {str(e)}")
    return render_template('delete.html', message="")

@app.route('/find', methods=['GET'])
def find_specfic_documents():

    results = collection.find({"FieldName":{"$in":valuesList}})

@app.route('/register', methods = ['POST'])
def register_user():
    data = request.json
    if not data or 'username' not in data or 'password' not in data: 
        return jsonify({"error": "Username or password not found."}), 400
    
    users_collection = mongo.db.users
    existing_user = users_collection.find_one({"username": data['username']})

    if existing_user:
        return jsonify({"Error": "User already exists"}), 400
    
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({
        "username": data['username'],
        "password": hashed_password.decode('utf-8')
    })

    return jsonify({"message": "User registered successfully."}), 201

    
    
if __name__ == '__main__':  
   app.run()