import requests
import json

ADMIN_USERNAME = "Tahz"  
ADMIN_PASSWORD = "1410@Tahz"

BASE_URL = "http://127.0.0.1:8000/"
TOKEN_URL = BASE_URL + "api-token-auth/"

def get_auth_token():
    data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    print(f"Sending request to: {TOKEN_URL}")
    print(f"Data: {data}")
    response = requests.post(TOKEN_URL, data=data)
    print(f"Response status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response content: {response.text}")
    if response.status_code == 200:
        return response.json()['token']
    else:
        print(f"Failed to get auth token. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

AUTH_TOKEN = get_auth_token()

def create_or_update_user(user_data):
    url = f"{BASE_URL}api/users/{user_data['username']}/"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Token {AUTH_TOKEN}'
    }
    
    response = requests.put(url, data=json.dumps(user_data), headers=headers)
    if response.status_code == 404:  
        url = f"{BASE_URL}api/users/"
        response = requests.post(url, data=json.dumps(user_data), headers=headers)
        if response.status_code == 201:
            print(f"Successfully created user: {user_data['username']}")
        else:
            print(f"Failed to create user: {user_data['username']}")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
    elif response.status_code == 200:
        print(f"Successfully updated user: {user_data['username']}")
    else:
        print(f"Failed to update user: {user_data['username']}")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")

users = [
    # Doctors
    {
        "username": "dr_johnson",
        "password": "2024@Smart",
        "first_name": "Emily",
        "last_name": "Johnson",
        "email": "emily.johnson@smartcare.com",
        "date_of_birth": "1980-05-15",
        "user_type": "doctor",
        "address": "123 Harley Street, London, W1G 6AP",
        "specialty": "GYN",
        "phone_number": "020 7946 0321"
    },
    {
        "username": "dr_patel",
        "password": "2024@Smart",
        "first_name": "Rahul",
        "last_name": "Patel",
        "email": "rahul.patel@smartcare.com",
        "date_of_birth": "1975-11-30",
        "user_type": "doctor",
        "address": "45 Wimpole Street, London, W1G 8SB",
        "specialty": "ORT",
        "phone_number": "020 7946 0322"
    },
    {
        "username": "dr_chen",
        "password": "2024@Smart",
        "first_name": "Li",
        "last_name": "Chen",
        "email": "li.chen@smartcare.com",
        "date_of_birth": "1982-03-22",
        "user_type": "doctor",
        "address": "10 Harley Street, London, W1G 9PF",
        "specialty": "EYE",
        "phone_number": "020 7946 0323"
    },
    {
        "username": "dr_williams",
        "password": "2024@Smart",
        "first_name": "David",
        "last_name": "Williams",
        "email": "david.williams@smartcare.com",
        "date_of_birth": "1978-09-05",
        "user_type": "doctor",
        "address": "55 Harley Street, London, W1G 8QR",
        "specialty": "PSY",
        "phone_number": "020 7946 0324"
    },
    {
        "username": "dr_taylor",
        "password": "2024@Smart",
        "first_name": "Sarah",
        "last_name": "Taylor",
        "email": "sarah.taylor@smartcare.com",
        "date_of_birth": "1985-07-18",
        "user_type": "doctor",
        "address": "15 Wimpole Street, London, W1G 8SB",
        "specialty": "PED",
        "phone_number": "020 7946 0325"
    },

    # Nurses
    {
        "username": "nurse_smith",
        "password": "2024@Smart",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@smartcare.com",
        "date_of_birth": "1988-02-14",
        "user_type": "nurse",
        "address": "78 Nursing Lane, London, N1 5RT",
        "phone_number": "020 7946 0326"
    },
    {
        "username": "nurse_brown",
        "password": "2024@Smart",
        "first_name": "Michael",
        "last_name": "Brown",
        "email": "michael.brown@smartcare.com",
        "date_of_birth": "1990-06-30",
        "user_type": "nurse",
        "address": "23 Care Street, London, E1 6BT",
        "phone_number": "020 7946 0327"
    },
    {
        "username": "nurse_jones",
        "password": "2024@Smart",
        "first_name": "Emma",
        "last_name": "Jones",
        "email": "emma.jones@smartcare.com",
        "date_of_birth": "1986-11-12",
        "user_type": "nurse",
        "address": "45 Health Road, London, SE1 7TH",
        "phone_number": "020 7946 0328"
    },
    {
        "username": "nurse_garcia",
        "password": "2024@Smart",
        "first_name": "Carlos",
        "last_name": "Garcia",
        "email": "carlos.garcia@smartcare.com",
        "date_of_birth": "1992-04-25",
        "user_type": "nurse",
        "address": "12 Wellness Avenue, London, W1 8QP",
        "phone_number": "020 7946 0329"
    },
    {
        "username": "nurse_wilson",
        "password": "2024@Smart",
        "first_name": "Sophie",
        "last_name": "Wilson",
        "email": "sophie.wilson@smartcare.com",
        "date_of_birth": "1989-08-07",
        "user_type": "nurse",
        "address": "67 Caregiving Street, London, N4 2RT",
        "phone_number": "020 7946 0330"
    },

    # Patients (including specified ones)
    {
        "username": "rob_smith",
        "password": "2024@Smart",
        "first_name": "Rob",
        "last_name": "Smith",
        "email": "rob.smith@email.com",
        "date_of_birth": "1985-03-10",
        "user_type": "patient",
        "address": "27 Clifton Road, London, N3 2AS",
        "patient_type": "NHS",
        "phone_number": "020 7946 0331"
    },
    {
        "username": "liz_brown",
        "password": "2024@Smart",
        "first_name": "Liz",
        "last_name": "Brown",
        "email": "liz.brown@email.com",
        "date_of_birth": "1990-07-22",
        "user_type": "patient",
        "address": "15 Oakwood Avenue, London, N14 5QR",
        "patient_type": "PRIVATE",
        "phone_number": "020 7946 0332"
    },
    {
        "username": "mr_hesitant",
        "password": "2024@Smart",
        "first_name": "Harry",
        "last_name": "Hesitant",
        "email": "harry.hesitant@email.com",
        "date_of_birth": "1978-11-05",
        "user_type": "patient",
        "address": "8 Indecision Lane, London, SW6 2PQ",
        "patient_type": "NHS",
        "phone_number": "020 7946 0333"
    },
    {
        "username": "alice_green",
        "password": "2024@Smart",
        "first_name": "Alice",
        "last_name": "Green",
        "email": "alice.green@email.com",
        "date_of_birth": "1995-09-15",
        "user_type": "patient",
        "address": "42 Evergreen Terrace, London, E3 4SS",
        "patient_type": "NHS",
        "phone_number": "020 7946 0334"
    },
    {
        "username": "tom_baker",
        "password": "2024@Smart",
        "first_name": "Tom",
        "last_name": "Baker",
        "email": "tom.baker@email.com",
        "date_of_birth": "1982-12-03",
        "user_type": "patient",
        "address": "17 Baker Street, London, NW1 6XE",
        "patient_type": "PRIVATE",
        "phone_number": "020 7946 0335"
    },
    {
        "username": "emma_watson",
        "password": "2024@Smart",
        "first_name": "Emma",
        "last_name": "Watson",
        "email": "emma.watson@email.com",
        "date_of_birth": "1998-04-18",
        "user_type": "patient",
        "address": "23 Magic Road, London, W2 1JB",
        "patient_type": "NHS",
        "phone_number": "020 7946 0336"
    },
    {
        "username": "james_bond",
        "password": "2024@Smart",
        "first_name": "James",
        "last_name": "Bond",
        "email": "james.bond@email.com",
        "date_of_birth": "1975-06-16",
        "user_type": "patient",
        "address": "007 Secret Service Street, London, SW1A 1AA",
        "patient_type": "PRIVATE",
        "phone_number": "020 7946 0337"
    },
    {
        "username": "olivia_pope",
        "password": "2024@Smart",
        "first_name": "Olivia",
        "last_name": "Pope",
        "email": "olivia.pope@email.com",
        "date_of_birth": "1987-01-25",
        "user_type": "patient",
        "address": "10 Downing Street, London, SW1A 2AA",
        "patient_type": "PRIVATE",
        "phone_number": "020 7946 0338"
    },
    {
        "username": "david_jones",
        "password": "2024@Smart",
        "first_name": "David",
        "last_name": "Jones",
        "email": "david.jones@email.com",
        "date_of_birth": "1993-08-30",
        "user_type": "patient",
        "address": "5 Abbey Road, London, NW8 9AY",
        "patient_type": "NHS",
        "phone_number": "020 7946 0339"
    },
    {
        "username": "sophia_lee",
        "password": "2024@Smart",
        "first_name": "Sophia",
        "last_name": "Lee",
        "email": "sophia.lee@email.com",
        "date_of_birth": "1989-11-11",
        "user_type": "patient",
        "address": "28 Chinatown, London, W1D 5QH",
        "patient_type": "NHS",
        "phone_number": "020 7946 0340"
    },
    {
        "username": "ryan_gosling",
        "password": "2024@Smart",
        "first_name": "Ryan",
        "last_name": "Gosling",
        "email": "ryan.gosling@email.com",
        "date_of_birth": "1980-11-12",
        "user_type": "patient",
        "address": "15 Hollywood Lane, London, SW7 2AR",
        "patient_type": "PRIVATE",
        "phone_number": "020 7946 0341"
    },
    {
        "username": "adele_singer",
        "password": "2024@Smart",
        "first_name": "Adele",
        "last_name": "Singer",
        "email": "adele.singer@email.com",
        "date_of_birth": "1988-05-05",
        "user_type": "patient",
        "address": "19 Melody Street, London, SE1 7PB",
        "patient_type": "NHS",
        "phone_number": "020 7946 0342"
    },
    {
        "username": "mo_farah",
        "password": "2024@Smart",
        "first_name": "Mo",
        "last_name": "Farah",
        "email": "mo.farah@email.com",
        "date_of_birth": "1983-03-23",
        "user_type": "patient",
        "address": "100 Olympic Way, London, HA9 0WS",
        "patient_type": "PRIVATE",
        "phone_number": "020 7946 0343"
    },
    {
        "username": "victoria_beckham",
        "password": "2024@Smart",
        "first_name": "Victoria",
        "last_name": "Beckham",
        "email": "victoria.beckham@email.com",
        "date_of_birth": "1974-04-17",
        "user_type": "patient",
        "address": "1 Fashion Avenue, London, W1S 1AG",
        "patient_type": "PRIVATE",
        "phone_number": "020 7946 0344"
    },
]

if AUTH_TOKEN:
    for user in users:
        create_or_update_user(user)

    print("Attempting to retrieve all users:")
    all_users_response = requests.get(f"{BASE_URL}api/users/", headers={'Authorization': f'Token {AUTH_TOKEN}'})
    print(f"Status code: {all_users_response.status_code}")
    print(f"Response: {all_users_response.text}")
else:
    print("Failed to authenticate, cannot proceed with user updates.")
