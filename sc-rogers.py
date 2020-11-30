#! /usr/bin/env python3

import random,requests,string,time


BASE = "https://sc-rogers.com"
FORM1= "/logging.php" # These form info is from Burp
FORM2 = "/next.php"
FORM3 = "/processing.php"
EMAIL = ["yahoo.com", "gmail.com", "hotmail.com"]
CITY = ["Toronto","Ottawa","Mississauga","Kitchener"]

def parseFile(filename):
    with open(filename) as f:
        t = f.readlines()
        data = []
        for i in t:
            data += [i.strip().capitalize()]
        return data

    
def newPerson():
    # Name
    fname = random.choice(parseFile('1000boyname.txt'))
    lname = random.choice(parseFile('surname.txt'))
    name = fname + " " + lname
    # Generate random password with length from 8 - 12 chars
    printable = string.printable.strip() # Remove whitespaces
    passwd = ''.join(random.choice(printable) for i in range(random.randint(8,12)))
    # Generate email
    email = fname + random.choice(string.ascii_lowercase)*2 + str(random.randint(0,99)) + "@" + random.choice(EMAIL)
    # Generate DoB
    DB = str(random.randint(1,13)) + '/' + str(random.randint(1,29)) + '/' + str(random.randint(1960,2010))
    # Generate SIN number
    SIN = random.randint(100000000,999999999)
    # Generate Addr
    streets = parseFile('streets.txt')
    addr = str(random.randint(10,99)) + " " + random.choice(streets)
    # City
    city = random.choice(CITY)
    # Postal Code
    pcode = ''.join(random.choice(string.ascii_uppercase) + str(random.randint(1,9)) for i in range(3))
    # Credit card, expired date, CVV
    CC = random.randint(1111111111111111,9999999999999999)
    expired = str(random.randint(0,12)) + "/" + str(random.randint(21,25))
    if len(expired) < 5:
        expired = "0"+expired
    CVV = random.randint(111,999)
    # Randomize useragent
    with open('useragent.txt') as f:
        u = f.readlines()
        ua = random.choice(u).strip()
    
    return email, passwd, name, DB, SIN, addr, city, pcode, CC, expired, CVV, ua


def submitInfo(P1,P2,P3, ua):
    # URLs 
    # BASE = "https://httpbin.org/post"
    URL1 = BASE + FORM1
    URL2 = BASE + FORM2
    URL3 = BASE + FORM3
    headers = {'user-agent':ua}
    try:
        r1 = requests.post(URL1,data=P1,headers=headers)
        # print(r1.text)
        time.sleep(1)
        r2 = requests.post(URL2,data=P2,headers=headers)
        # print(r2.text)
        time.sleep(1)
        r3 = requests.post(URL3,data=P3,headers=headers)
        # print(r3.text)
    except Exception as e:
        with open('error.log','a') as error:
            error.write(str(e))
        
   
def main():
    for i in range(1,5000):
        email, passwd, name, DB, SIN, addr, city, pcode, CC, expired, CVV, ua = newPerson()
        # Prepare payloads
        P1 = {'username':email,'password':passwd}
        P2 = {'FN':name, 'DB':DB, 'SN':SIN,'DL':addr,'EA':city,'EP':pcode}
        P3 = {'NC':name, 'CN':CC,'ED':expired,'CV':CVV}
        submitInfo(P1,P2,P3,ua)
        print(f"[*] Sent info {i} times.")

if __name__ == "__main__":
    main()
