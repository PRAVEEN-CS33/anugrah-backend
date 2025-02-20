from twilio.rest import Client
# from flask import Flask, request, jsonify

# app = Flask(__name__)

# # Route to handle call creation
# @app.route('/call', methods=['POST', 'GET'])
def place_call(number):
    try:
        # Initialize the Twilio client with Account SID and Auth Token
        account_sid = 'AC913b92db6515d514ad2eb5584c1f5a3e'
        auth_token = '978e1d0414701ed944d284d466d5f1fd'
        client = Client(account_sid, auth_token)

        # Extract parameters from the incoming request
        from_number = '+15073964432'
        to_number = '+91'+number
        url = 'https://anugrah-7127.twil.io/call.xml'

        # Create the call with the record flag enabled
        call = client.calls.create(
            to=to_number,
            from_=from_number,
            record=True,
            url=url
        )

        # Log and return success response
        print(f"Call successfully placed. Call SID: {call.sid}")
        # return jsonify({"message": "Success!", "CallSID": call.sid}), 200

    except Exception as e:
        # Log and return error response
        print(f"Error placing call: {e}")
        # return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True, port=8000)
# place_call()