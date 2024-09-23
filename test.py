import requests
import time

BASE_URL = 'http://127.0.0.1:5000'

def test_generate_key():
    response = requests.post(f'{BASE_URL}/keys')
    if response.status_code == 201:
        key_id = response.json()['keyId']
        print(f'Key generated: {key_id}')
        return key_id
    else:
        print(f'Failed to generate key: {response.status_code}')
        return None

def test_get_key():
    response = requests.get(f'{BASE_URL}/keys')
    if response.status_code == 200:
        key_id = response.json()['keyId']
        print(f'Key retrieved: {key_id}')
        return key_id
    elif response.status_code == 404:
        print('No available keys to retrieve')
        return None
    else:
        print(f'Failed to retrieve key: {response.status_code}')
        return None

def test_get_key_info(key_id):
    response = requests.get(f'{BASE_URL}/keys/{key_id}')
    if response.status_code == 200:
        key_info = response.json()
        print(f'Key info: {key_info}')
    elif response.status_code == 404:
        print('Key not found')
    else:
        print(f'Failed to get key info: {response.status_code}')

def test_delete_key(key_id):
    response = requests.delete(f'{BASE_URL}/keys/{key_id}')
    if response.status_code == 200:
        print(f'Key deleted: {key_id}')
    elif response.status_code == 404:
        print('Key not found')
    else:
        print(f'Failed to delete key: {response.status_code}')

def test_unblock_key(key_id):
    response = requests.put(f'{BASE_URL}/keys/{key_id}')
    if response.status_code == 200:
        print(f'Key unblocked: {key_id}')
    elif response.status_code == 404:
        print('Key not found')
    else:
        print(f'Failed to unblock key: {response.status_code}')

def test_keep_alive(key_id):
    response = requests.put(f'{BASE_URL}/keepalive/{key_id}')
    if response.status_code == 200:
        print(f'Keep alive successful for key: {key_id}')
    elif response.status_code == 404:
        print('Key not found')
    else:
        print(f'Failed to keep alive key: {response.status_code}')

if __name__ == '__main__':
    key_id = test_generate_key()
    key_id1 = test_generate_key()
    key_id2 = test_generate_key()
    key_id3 = test_generate_key()
    time.sleep(1)

    if key_id:
        # Retrieve an available key (it should be the same key just created)
        retrieved_key_id = test_get_key()
        time.sleep(1)

        # Get key information
        if retrieved_key_id:
            test_get_key_info(retrieved_key_id)
            time.sleep(1)

            # Unblock the key
            test_unblock_key(retrieved_key_id)
            time.sleep(1)

            # Keep the key alive
            test_keep_alive(retrieved_key_id)
            time.sleep(1)

            # Delete the key
            test_delete_key(retrieved_key_id)
            
            retrieved_key_id = test_get_key()

