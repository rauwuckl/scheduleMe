import api
import datetime
import json
import pytz
import traceback
max_days_in_future = 5



class Scheduler:
    def __init__(self, user_file):
        self.user = api.User.load_user_from_json(user_file)

        self.user.login()

        self.max_days_in_future = 5

        self.fake_today_debug = datetime.date(year=2018, month=11, day=14)

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

            acceptable_times = [f for f in free_times if self.time_is_acceptable(f)]

            if len(acceptable_times) != 0:

                best_time = acceptable_times[0]

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
            tzinfo=None)) > datetime.timedelta(hours=1))

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
    timeAndDate = datetime.datetime.now(pytz.timezone("Europe/Berlin")).replace(tzinfo=None)
    print("Now it is {} on {} in Germany".format(timeAndDate.time(), timeAndDate.date()))
    scheduler = Scheduler("user.json")
    scheduler.continously_book(0.1, None)
