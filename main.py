import api
import datetime
import json
import pytz
import traceback
import argparse
min_hours_from_now = 2
max_days_in_future = 5

earliest_time_in_day = True # if false it will book the latest available appointment on that day



class Scheduler:
    def __init__(self, user_file, today=None):
        self.user = api.User.load_user_from_json(user_file)

        self.user.login()

        self.max_days_in_future = 5
        self.min_hours_from_now = 2

        self.set_today = today # datetime.date(year=2019, month=7, day=15)

    def save_try_schedule_within_limit(self):
        try:
            return self.try_schedule_within_limit()
        except Exception as e:
            print("Something went wrong:")
            print(e)
            print(traceback.format_exc())



    def try_schedule_within_limit(self):
        if self.set_today is None:
            today = datetime.datetime.now(pytz.timezone("Europe/Berlin")).date()
        else:
            today = self.set_today

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

            acceptable_times = [f for f in free_times if self.time_is_acceptable(f)]

            if len(acceptable_times) != 0:
                if earliest_time_in_day:
                    best_time = acceptable_times[0]
                else:
                    best_time = acceptable_times[-1]


                print("Trying to book appoitment at {}".format(best_time))

                result = api.book_appoitment(best_time, self.user)

                with open("output.json", "w") as f:
                    json.dump(result, f)

                return True
            else:
                print("No acceptable time found")
                return False

        else:
            print("First free date is too far in the future {}".format(first_free_date))
            return False

    def time_is_acceptable(self, time):
        bool_val = ((time - datetime.datetime.now(pytz.timezone("Europe/Berlin")).replace(
            tzinfo=None)) > datetime.timedelta(hours=self.min_hours_from_now))

        if not bool_val:
            print("Appointment {} was sorted out at {}".format(time, datetime.datetime.now(pytz.timezone("Europe/Berlin"))))

        return bool_val



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
    parser = argparse.ArgumentParser()
    parser.add_argument('--book_date', default="", type=str)
    ARGS = parser.parse_args()

    timeAndDate = datetime.datetime.now(pytz.timezone("Europe/Berlin")).replace(tzinfo=None)
    print("Now it is {} on {} in Germany".format(timeAndDate.time(), timeAndDate.date()))

    if ARGS.book_date == "":
        print("booking today")
        scheduler = Scheduler("user.json")
        scheduler.continously_book(0.1, None)
    else:
        fake_today = datetime.datetime.strptime(ARGS.book_date, "%d.%m.%Y").date()

        print("trying to book on the day after {}".format(fake_today))
        scheduler = Scheduler("user.json", fake_today)
        scheduler.continously_book(0.1, None)
