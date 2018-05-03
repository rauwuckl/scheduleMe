import api
import datetime
import json
import pytz
import traceback
max_days_in_future = 5



class Scheduler:
    def __init__(self, user_file):
        self.user = api.User.load_user_from_json(user_file)

        self.max_days_in_future = 5

        self.fake_today_debug = None#datetime.date(year=2018, month=10, day=18)

    def save_try_schedule_within_limit(self):
        try:
            return self.try_schedule_within_limit()
        except Exception as e:
            print("Something went wrong:")
            print(e)
            print(traceback.format_exc())




    def try_schedule_within_limit(self):
        if self.fake_today_debug is None:
            today = datetime.datetime.now(pytz.timezone("Europe/Berlin")).date()
        else:
            today = self.fake_today_debug

        tomorrow = today + datetime.timedelta(days=1)

        free_dates = api.get_free_dates(year_id = tomorrow.year, month_id = tomorrow.month)

        if free_dates is None:
            print("*", end=" ", flush=True)
            return False
        else:
            print("!")


        first_free_date = free_dates[0]

        if first_free_date - today < datetime.timedelta(days=self.max_days_in_future):
            print("Free date at {}".format(first_free_date))

            free_times = api.get_free_times(first_free_date)

            last_free_time = free_times[-1]

            if last_free_time - datetime.datetime.now(pytz.timezone("Europe/Berlin")).replace(tzinfo=None) > datetime.timedelta(hours=1):

                print("Trying to book appoitment at {}".format(last_free_time))

                result = api.book_appoitment(last_free_time, self.user)

                with open("output.json", "w") as f:
                    json.dump(result, f)

                return True
            else:
                print("{} was to soon".format(last_free_time))
                return False

        else:
            print("First free date is too far in the future {}".format(first_free_date))
            return False

    def continously_book(self, repeat_delay, max_try_time = None):
        """repeat_delay and max_try_time in seconds"""

        if max_try_time:
            n_max_tries = max_try_time / repeat_delay
            increment = 1
        else:
            increment = 0  # hacky workaround, that makes the loop run forever
            n_max_tries = 1

        booking_succesfull = False
        i = 0

        print("Starting Scheduling: ")

        while(not booking_succesfull and i <= n_max_tries):
            i += increment

            booking_succesfull = self.save_try_schedule_within_limit()

        if booking_succesfull:
            print("succesfully booked date")
        else:
            print("finished without success")


if __name__ == "__main__":
    timeAndDate = datetime.datetime.now(pytz.timezone("Europe/Berlin"))
    print("Now it is {} on {} in Germany".format(timeAndDate.time(), timeAndDate.date()))
    scheduler = Scheduler("user.json")
    scheduler.continously_book(0.1, None)