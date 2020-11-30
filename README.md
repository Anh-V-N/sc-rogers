# TL;DR
One of my family members received a text message, seemingly from Roger - her mobile phone network provider, claiming that her services were suspended and she needed to go to a specific website https://sc-rogers[dot]com and "verify" her information to settle the issue. Fortunately, she was able to tell that there was  something fishy about it. She didn't click on the link but instead sent me a screenshot of said message.  
![[screenshot.png]](screenshots/screenshot.png)  
After inspecting it, I determined that it is a  site standing up by some scammers to gather personal identifiable information, aka PII ( information such as full name, credentials, DoB, SIN number, credit card number, etc) from whoever falls for it. I decided to report it to its Domain name registrar and also feed it what it is asking for: PII. Please pardon my English since I am not a native and my code for being not as  clean as it can be.

# Technical details
## Manually poking at the site
I started my little investigation by looking up the domain via whois database

![[screenshot1.png]](screenshots/screenshot1.png) 

The domain name was registered today on namecheap.com at 17:42 and  the phising text was sent at 18:21 in the same day. I'm not sure what the timezone whois is based on so there might be a couple of hours different but regardless these guys work fast! I wondered if this domain had been flagged as malicious so  I looked it up again at [virustotal](https://www.virustotal.com/gui/url/0ef3f7481ee2c406169ab0b592d20e13e27366d139d005e85a6e9daa0106fb97/details) and so far only 1 engine identifies this domain as malicious/phising

![[screenshot2.png]](screenshots/screenshot2.png)

Ok, it's fair since the domain is literally just registered  a few hours ago. I wonder what exactly this new phising site is trying to do but before pointing my browser to this url, I take an extra step and look at it via curl. 

![[screenshot3.png]](screenshots/screenshot3.png)  

There are  just a few codes of php that include some php pages which I have no idea what they are doing and a  supicious document.write with encoded code. Using  Burp decoder, this is what comes back.

![[screenshot4.png]](screenshots/screenshot4.png)

It seems to be a bunch of html code that make up the page interface, nothing too interesting and I don't see any malicious javascript embeded in it neither. Since I already have Burp Suite running, I set the target scope and configured my browser to proxy through it. I spoofed my IP address and my user agent to something else before start interacting with the site itself. As expected, a login form is presented.

![[screenshot5.png]](screenshots/screenshot5.png)

I entered abitrary credentials to proceed and guess what? The site asks for more information.

![[screenshot6.png]](screenshots/screenshot6.png)

Again, more abitrary information to proceed. This 3rd page the scammer is nice enough to promise that he/she would keep my debit/credit card information "encrypted and secure". What a catch!

![[screenshot7.png]](screenshots/screenshot7.png)

After vonlunteering random credit card details, I was congratulated for completing the verification and promised that my account was fully restored and my browser redirected back to the legitimate rogers.com.  Even though I don't even have an account with Rogers, I still feel relieved and that my effort is appreciated. 

![[screenshot8.png]](screenshots/screenshot8.png)

But why stop here? Since they want PII so bad, why don't I give it more. After all I'm such a nice guy. But repeating the process is boring and painful, I don't really want to do it. This scenario reminded me of one of the youtube clips I watched. It is from Engineer Man where [he used python to automate such task](https://www.youtube.com/watch?v=UtNYzv8gLbs). I decided to redo his work with some extra flavors. 
## Automate the process with Python
First of all, I went back to Burp Suite to check out the requests my browser made.
Sorting the requests by method, it is easily to pick the exact 3 POST requests that submitted the information to the site.

![[screenshot9.png]](screenshots/screenshot9.png)

After googling some popular first names, last name, and street names and put them into seperated text files. I started coding with python. 
Firstly, I imported some modules  and defined some constants that I would need. Then I created 3 functions:  
**parseFile()** to parse the content of the text files.   
**newPerson()** to generate abitrary PII and random user agent. The user agent part may not needed, I add it to reduce the pattern of the generated data.
**submitInfo()** to actually send the generated data to the site.   
I have to admit that I am rusty and had to look up some documentations to put these code together. After finished coding and tested it against httpbin.org  and the target itself to confirm that the code works as intended, I let the script go nut! Lol. By the time I fisnish this write up, the site has been fed with PII from 3000+ non-existed people and counting. I hope they are happy with this amount of information and have a great time to filter these garbage data with the legitimate data from their victims.

![[screenshot10.png]](screenshots/screenshot10.png)  

The full script can be found here:

```python
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

```
