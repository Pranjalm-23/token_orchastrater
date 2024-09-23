from flask import Flask, jsonify
from uuid import uuid4
from time import time, sleep
from threading import Lock, Thread
import heapq

app = Flask(__name__)
lock = Lock()

# In-memory data structures
keys = {}
blocked_keys = {}
key_heap = []

# keys = {}
# key_heap = []
# KEY_TTL = 3600  # example value

# Key TTL (Time to Live) in seconds
KEY_TTL = 120
BLOCK_DURATION = 60

# POST /keys: Generate new keys.
# Status: 201
@app.route('/keys', methods=['POST'])
def generate_key():
    """Generate a new key with a unique ID and a creation timestamp."""
    try:
        key_id = str(uuid4())
        created_at = time()
        print(created_at)
        keys[key_id] = {
            'created_at': created_at,
            'blocked': False,
            'blocked_at': None,
            'keep_alive_at': created_at + KEY_TTL
        }
        heapq.heappush(key_heap, (created_at + KEY_TTL, key_id))
        
        return jsonify({'keyId': key_id}), 201
    except Exception as e:
        print(f'Error generating key: {e}')
        return jsonify({}), 500

@app.route('/keys', methods=['GET'])
def get_key():
    """
    GET /keys: Retrieve an available key for client use.
    Status: 200 / 404 
    Response: { "keyId": "<keyID>" } / {}
    """
    try:
        with lock:
            available_keys = [k for k, v in keys.items() if not v['blocked']]
            if not available_keys:
                return jsonify({}), 404
            key_id = available_keys[0]
            # Client use needs the key to be blocked
            keys[key_id]['blocked'] = True
            keys[key_id]['blocked_at'] = time()
            blocked_keys[key_id] = time() + BLOCK_DURATION
            heapq.heappush(key_heap, (blocked_keys[key_id], key_id))
            return jsonify({'keyId': key_id}), 200
    except Exception as e:
        print(f'Error retrieving key: {e}')

# debug purpose
@app.route('/key', methods=['GET'])
def get_keys():
    return jsonify(keys)

@app.route('/keys/<key_id>', methods=['GET'])
def get_key_info(key_id):
    """
    GET /keys/:id: Provide information (e.g., assignment timestamps) about a specific key.
    Status: 200 / 404 
    Response: 
    { 
    "isBlocked" : "<true> / <false>", 
    "blockedAt" : "<blockedTime>", 
    "createdAt" : "<createdTime>" 
    } / {}
    """
    try:
        if key_id not in keys:
            return jsonify({}), 404
        key_info = keys[key_id]
        return jsonify({
            'isBlocked': key_info['blocked'],
            'blockedAt': key_info['blocked_at'],
            'createdAt': key_info['created_at']
        }), 200
    except Exception as e:
        print(f'Error retrieving key information: {e}')
        return jsonify({}), 500


@app.route('/keys/<key_id>', methods=['DELETE'])
def delete_key(key_id):
    """
    DELETE /keys/:id: Remove a specific key, identified by :id, from the system.
    Status: 200 / 404
    """
    try:
        with lock:
            if key_id in blocked_keys:
                return jsonify({"Key is blocked":key_id}), 200
            if key_id not in keys:
                return jsonify({}), 404
            del keys[key_id]
            if key_id in blocked_keys:
                del blocked_keys[key_id]
            return jsonify({"Deleted Key":key_id}), 200
    except Exception as e:
        print(f'Error deleting key: {e}')
        return jsonify({}), 500

@app.route('/keys/<key_id>', methods=['PUT'])
def unblock_key(key_id):
    """
    PUT /keys/:id: Unblock a key for further use.
    Status: 200 / 404
    """
    try:            
        with lock:
            if key_id not in keys:
                return jsonify({}), 404
            keys[key_id]['blocked'] = False
            keys[key_id]['blocked_at'] = None
            if key_id in blocked_keys:
                del blocked_keys[key_id]
            return jsonify({"Key Available for use: ":key_id}), 200
    except Exception as e:
        print(f'Error unblocking key: {e}')
        return jsonify({}), 500


@app.route('/keepalive/<key_id>', methods=['PUT'])
def keep_alive(key_id):
    """
    PUT /keepalive/:id: Signal the server to keep the specified key, identified by :id, from being deleted.
    Status: 200 / 404
    """
    try:
        with lock:
            if key_id not in keys:
                return jsonify({}), 404
            keys[key_id]['keep_alive_at'] = time() + KEY_TTL
            keys[key_id]['blocked_at'] = time()
            keys[key_id]['blocked'] = True
            blocked_keys[key_id] = time() + BLOCK_DURATION
            heapq.heappush(key_heap, (keys[key_id]['keep_alive_at'], key_id))
            return jsonify({"Key Blocked for 5 minutes: ":key_id}), 200
    except Exception as e:
        print(f'Error keeping key alive: {e}')
        return jsonify({}), 500
    
@app.route('/blocked/<key_id>', methods=['GET'])


def cleanup():
    """
    Cleanup routine for clearing expired keys
    """
    while True:
        sleep(1)
        with lock:
            while key_heap and key_heap[0][0] <= time():
                _, key_id = heapq.heappop(key_heap)
                if key_id in keys:
                    key_info = keys[key_id]
                    if key_info['keep_alive_at'] <= time():
                        del keys[key_id]
                    elif key_info['blocked'] and key_info['blocked_at'] + BLOCK_DURATION <= time():
                        key_info['blocked'] = False
                        key_info['blocked_at'] = None
                        del blocked_keys[key_id]

Thread(target=cleanup, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True)
    print("running")
