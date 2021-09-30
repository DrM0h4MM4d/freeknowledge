from . import jalali

def convert_to_jalali(date):
    months = [
        "فروردین",
        "اردیبهشت",
        "خرداد",
        "تیر",
        "مرداد",
        "شهریور",
        "مهر",
        "آبان",
        "آذر",
        "دی",
        "بهمن",
        "اسفند",
    ]

    time_to_str = "{},{},{}".format(date.year, date.month, date.day)
    time_to_tuple = jalali.Gregorian(time_to_str).persian_tuple()
    time_to_list = list(time_to_tuple)
    for index, mounth in enumerate(months):
        if time_to_list[1] == index + 1:
            time_to_list[1] = mounth
            break

    output = "{} {} {}, ساعت: {}:{}".format(
        time_to_list[2], 
        time_to_list[1], 
        time_to_list[0], 
        date.hour, 
        date.minute
    )
    return output