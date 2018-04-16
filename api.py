import requests
import datetime
import urllib
import json

form_header = {
    "Host": "timeacle.com",
    # Connection: keep-alive
    # Content-Length: 171
    # Pragma: no-cache
    # Cache-Control: no-cache
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Origin": "https://timeacle.com",
    "X-Requested-With": "XMLHttpRequest",
    # User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://timeacle.com/business/index/id/332/booking/appointment/row_id/254/iframe/true"
    # Accept-Encoding: gzip, deflate, br
    # Accept-Language: en-GB,en;q=0.9,en-US;q=0.8,de;q=0.7
    # Cookie: image-loaded=7; TICKETproduction=wtscwm; PHPSESSID=nkfbsoh5srcnfqono1pu80e3k7; _pk_ref.1.00b9=%5B%22%22%2C%22%22%2C1523868224%2C%22https%3A%2F%2Fwww.osnabrueck.de%2Fverwaltung%2Fterminvergabe%2Fauslaenderbehoerde-termin-vereinbaren.html%22%5D; _pk_ses.1.00b9=*; _pk_id.1.00b9=89c9c8716e11a02b.1523221241.5.1523870131.1523868224.
}

date_format_string = "%d.%m.%Y"
time_format_string = "%H:%M"

def get_free_dates(month_id, year_id):

    url_template = "https://timeacle.com/api/calendar/opendays/object/row/id/254/month/{month}/year/{year}"

    r = requests.get(url_template.format(month=month_id, year=year_id))

    if r.status_code != 200:
        print("Getting dates failed:")
        print(r)
        print(r.json())
        print(r.text)

    if r.json() is None:
        # print("Nothing availiable at {}.{}".format(month_id, year_id))
        return None
    else:
        available_days = r.json()[str(year_id)][str(month_id)]
        available_days_objects = [datetime.date(year=year_id, month=month_id, day=d) for d in available_days]
        return available_days_objects

def get_free_times(date):
    """date is datetime object"""

    data_template = "branch_id=332&row_id=254&date={date_string}&services%5B0%5D%5Bid%5D=423&services%5B0%5D%5Bcaption%5D=Bitte+buchen+Sie+pro+Person+einen+Termin%3A&services%5B0%5D%5Bamount%5D=1"
    url = "https://timeacle.com/api/booking/tickettime"

    date_string = date.strftime(date_format_string)

    # form_data = {"branch_id":332, "row_id":254, "date": date_string, "services[0][id]": 423,  "services[0][caption]": "Bitte buchen Sie pro Person einen Termin:", "services[0][amount]": 1}

    r = requests.post(url, data=data_template.format(date_string=date_string), headers=form_header)
    response = r.json()
    if response['slots'] is None:
        return None
    else:
        date_time_objects = [datetime.datetime.combine(date, parse_time(time_string))for time_string in response['slots']]
        return date_time_objects

def parse_time(time_string):
    int_values = [int(i) for i in time_string.split(":")]

    if len(int_values)!=2 :
        print("couldn't parse the times")
        return None
    else:
        hour, min = int_values

    return datetime.time(hour=hour, minute=min)

class User:

    @staticmethod
    def load_user_from_json(filename):

        with open(filename, "r") as f:
            info = json.load(f)

        return User(**info)

    def __init__(self, first_name, last_name, email, phone):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone

        self.user_id = None
        self.hash = None
        self.cookies = None

    def login(self):
        data = {"register_first_name": self.first_name,
            "register_last_name": self.last_name,
            "register_telephone": self.phone,
            "register_email": self.email}

        url_string = urllib.parse.urlencode(data)
        # print(url_string)

        url = "https://timeacle.com/ajaxform/register/type/nopass"
        r = requests.post(url, data=url_string, headers=form_header)
        response = r.json()


        self.user_id = response['user_id']
        self.hash = response['hash']
        self.cookies = r.cookies



def book_appoitment(appoitment_time, user):
    user.login()

    url = "https://timeacle.com/api/booking/ticketbooking"

    date_string = appoitment_time.strftime(date_format_string)
    time_string = appoitment_time.strftime(time_format_string)

    form_data = {"user_id": user.user_id, "row_id": 254, "date": date_string, "time": time_string,
    "services[0][id]": 423,
    "services[0][caption]": "Bitte buchen Sie pro Person einen Termin:",
    "services[0][amount]": 1,
    "hash": user.hash}

    url_string = urllib.parse.urlencode(form_data)

    r = requests.post(url, data=url_string, headers=form_header, cookies=user.cookies)

    return r.json()

# free_dates = get_free_dates(10, 2018)
# d1 = free_dates[-1]
#
# times = get_free_times(d1)
#
# last_time = times[-1]
#
#
# user = User(first_name="Clemens", last_name="Hutter", email="ch.23@web.de", phone="394993")
#
# t = datetime.datetime.now() + datetime.timedelta(days=1)
#
# print(t)
#
# booked = book_appoitment(t, user)