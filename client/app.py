from flask import Flask, request, jsonify, render_template
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

# SOAP client setup
wsdl_url = "http://127.0.0.1:9567/PyWebService/"
headers = {'content-type': 'text/xml;charset=UTF-8'}


# Home route
@app.route('/')
def home():
    return render_template('index.html')


# Route to render add user page
@app.route('/add_user_page')
def add_user_page():
    return render_template('add_user.html')


# Route to get user list
@app.route('/get_user_list', methods=['GET'])
def get_user_list():
    current_page = request.args.get('current_page', default=0, type=int)
    page_size = request.args.get('page_size', default=10, type=int)
    body = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pyw="PyWebService2">
           <soapenv:Header/>
           <soapenv:Body>
              <pyw:get_user_list>
                 <pyw:current_page>{current_page}</pyw:current_page>
                 <pyw:page_size>{page_size}</pyw:page_size>
              </pyw:get_user_list>
           </soapenv:Body>
        </soapenv:Envelope>
       """
    response = requests.post(wsdl_url, data=body, headers=headers, verify=False)
    root = ET.fromstring(response.text)
    namespace = {'pyw': 'PyWebService2'}
    element = root.find('.//pyw:get_user_listResult', namespace)
    if element is None:
        return jsonify({"error": "No data found"}), 404
    data = element.text
    return jsonify(data)


# Route to add a user
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json

    body = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pyw="PyWebService2">
           <soapenv:Header/>
           <soapenv:Body>
              <pyw:add_user>
                 <pyw:id>{data['id']}</pyw:id>
                 <pyw:user_name>{data['user_name']}</pyw:user_name>
                 <pyw:age>{data['age']}</pyw:age>
                 <pyw:sex>{data['sex']}</pyw:sex>
              </pyw:add_user>
           </soapenv:Body>
        </soapenv:Envelope>
       """
    response = requests.post(wsdl_url, data=body, headers=headers, verify=False)
    print(response.text)  # Debug print to see the SOAP response
    root = ET.fromstring(response.text)
    namespace = {'pyw': 'PyWebService2'}
    element = root.find('.//pyw:add_userResult', namespace)
    if element is None:
        return jsonify({"error": "Failed to add user"}), 500

    result = element.text
    if "error" in result:
        return result, 500
    return jsonify(result)


@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    id = request.args.get('id', type=int)
    if id is None:
        return jsonify({"error": "Index is required"}), 400

    body = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pyw="PyWebService2">
           <soapenv:Header/>
           <soapenv:Body>
              <pyw:delete_user>
                 <pyw:id>{id}</pyw:id>
              </pyw:delete_user>
           </soapenv:Body>
        </soapenv:Envelope>
       """
    response = requests.post(wsdl_url, data=body, headers=headers, verify=False)
    root = ET.fromstring(response.text)
    namespace = {'pyw': 'PyWebService2'}
    element = root.find('.//pyw:delete_userResult', namespace)
    if element is None:
        return jsonify({"error": "Failed to delete user"}), 500

    result = element.text
    if "error" in result:
        return result, 500
    return jsonify(result)


@app.route('/query_user', methods=['GET'])
def query_user():
    user_id = request.args.get('id', type=int)
    if user_id is None:
        return jsonify({"error": "User ID is required"}), 400

    body = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pyw="PyWebService2">
           <soapenv:Header/>
           <soapenv:Body>
              <pyw:query_user>
                 <pyw:id>{user_id}</pyw:id>
              </pyw:query_user>
           </soapenv:Body>
        </soapenv:Envelope>
       """
    response = requests.post(wsdl_url, data=body, headers=headers, verify=False)
    root = ET.fromstring(response.text)
    namespace = {'pyw': 'PyWebService2'}
    element = root.find('.//pyw:query_userResult', namespace)
    if element is None:
        return jsonify({"error": "User not found"}), 404

    result = element.text
    return jsonify(result)


@app.route('/edit_user', methods=['PUT'])
def edit_user():
    user_id = request.args.get('id', type=int)
    user_name = request.args.get('user_name')
    age = request.args.get('age', type=int)
    sex = request.args.get('sex', type=int)

    if None in (user_id, user_name, age, sex):
        return jsonify({"error": "All fields are required"}), 400

    body = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pyw="PyWebService2">
           <soapenv:Header/>
           <soapenv:Body>
              <pyw:edit_user>
                 <pyw:id>{user_id}</pyw:id>
                 <pyw:user_name>{user_name}</pyw:user_name>
                 <pyw:age>{age}</pyw:age>
                 <pyw:sex>{sex}</pyw:sex>
              </pyw:edit_user>
           </soapenv:Body>
        </soapenv:Envelope>
       """
    response = requests.post(wsdl_url, data=body, headers=headers, verify=False)
    root = ET.fromstring(response.text)
    namespace = {'pyw': 'PyWebService2'}
    element = root.find('.//pyw:edit_userResult', namespace)
    if element is None:
        return jsonify({"error": "Failed to edit user"}), 500

    result = element.text
    if "error" in result:
        return result, 500
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
