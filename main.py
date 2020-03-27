import random
import logging
from datetime import timedelta, datetime
from math import log

def init_logger(logger_name, file):
    # create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.FileHandler(file, "w")
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger

# all time variables are in minutes

INFINITY = 10**5
LAMBDA_BUSY = 0.3  #lambda to use in busy hours
LAMBDA_REGULAR = 0.2  #lambda to use in regular hours
FOODS = ["sandwich", "sushi"]  #kinds of foods there are in kojo's kitchen
BUSY_HOURS = [(90, 90 + 120), (7 * 60, 7 * 60 + 120)]  #busy hours time intervals
FOOD_TIMES = [(3, 5), (5, 8)]  #time that takes in prepare food of type 0 (sandwiches) and food of type 1 (sushi)
T = 11 * 60  #time that kitchen closes

def gen_exp(l):
    u = random.uniform(0, 1)
    return -1.0 / l * log(u)

def is_between(t, range):
    return range[0] <= t <= range[1]

def in_busy_hours(cur_time):
    return is_between(cur_time, BUSY_HOURS[0]) or is_between(cur_time, BUSY_HOURS[1])

def simulation_two_employees():
    logger = init_logger('Two Employees Logger', 'two_employees.log')  #initializing logger

    t = 0  #cur time
    arrivals = 0  #number of arrivals

    n = 0  #number of people in the system
    who_first = 0  #which client is employee 1 attending?
    who_second = 0  #which client is employee 2 attending?

    t_out_1 = INFINITY  #time after employee 1 attended client
    t_out_2 = INFINITY  #time after employee 2 attended client

    t_in = [ 0 ]  #time that i-th (1-indexed) client entered
    t_out = [ 0 ]  #time that i-th (1-indexed) client exited
    food_wants = [ -1 ]  #what type of food does client i (1-indexed) wants?

    first_empl_req = 0  #how many requests first employee finished?
    second_empl_req = 0  #how many requests second employee finished?

    logger.info('All variables initialized')

    next_arrival = gen_exp(LAMBDA_REGULAR)  #time of next arrival

    while True:
        cur_time = min(next_arrival, t_out_1, t_out_2)

        logger.info(f'Cur time = {cur_time:.5f} (in mins)')

        if next_arrival != INFINITY and next_arrival == cur_time:
            t = next_arrival
            food_wants.append(random.randint(0, 1))
            t_in.append(t)
            t_out.append(0)
            arrivals += 1

            f = food_wants[arrivals]

            logger.info(f'Client #{arrivals} entered at time = {t:.5f} and '
                f'wants food of type: {f} ({FOODS[f]})')

            if who_first == 0:
                logger.info(f'Employee 1 will attend client #{arrivals}')

                n += 1
                who_first = arrivals
                t_out_1 = t + random.uniform(FOOD_TIMES[f][0], FOOD_TIMES[f][1])

                logger.info(f'Employee will finish the request of client #{arrivals} at time = {t_out_1:.5f}')

            elif who_second == 0:
                logger.info(f'Employee 2 will attend client #{arrivals}')

                n += 1
                who_second = arrivals
                t_out_2 = t + random.uniform(FOOD_TIMES[f][0], FOOD_TIMES[f][1])

                logger.info(f'Employee will finish the request of client #{arrivals} at time = {t_out_2:.5f}')

            else:
                logger.info(f'Client #{arrivals} will have to wait in the queue')

            logger.info('Generating next client...')

            if in_busy_hours(t):
                next_arrival = t + gen_exp(LAMBDA_BUSY)

                logger.info(f'Using busy lambda, '
                f'next arrival will ocurr at time = {next_arrival:.5f}')

            else:
                next_arrival = t + gen_exp(LAMBDA_REGULAR)

                logger.info(f'Using regular lambda, '
                f'next arrival will ocurr at time = {next_arrival:.5f}')

            if next_arrival > T:
                next_arrival = INFINITY

        elif t_out_1 != INFINITY and t_out_1 == cur_time:
            first_empl_req += 1
            t = t_out_1
            t_out[who_first] = t

            logger.info(f'Employee 1 finished client #{who_first} request at time = {t:.5f}')

            n -= 1
            next_guy = max(who_first, who_second) + 1
            who_first = 0 if next_guy > arrivals else next_guy
           
            if who_first == 0:
                t_out_1 = INFINITY

            else:
                f = food_wants[who_first]
                t_out_1 = t + random.uniform(FOOD_TIMES[f][0], FOOD_TIMES[f][1])

                logger.debug(f'The order of client #{who_first} will start to being processed, '
                    f'it will be finished at time = {t_out_1:.5f}')

        elif t_out_2 != INFINITY and t_out_2 == cur_time:
            second_empl_req += 1
            t = t_out_2
            t_out[who_second] = t

            logger.info(f'Employee 2 finished client #{who_second} request at time = {t:.5f}')

            n -= 1
            next_guy = max(who_first, who_second) + 1
            who_second = 0 if next_guy > arrivals else next_guy

            if who_second == 0:
                t_out_2 = INFINITY

            else:
                f = food_wants[who_second]
                t_out_2 = t + random.uniform(FOOD_TIMES[f][0], FOOD_TIMES[f][1])

                logger.debug(f'The order of client #{who_second} will start to being processed, '
                    f'it will be finished at time = {t_out_2:.5f}')

        else:
            break

    logger.info('Kojo\'s kitchen is closed!')

    logger.info('Summary:')

    logger.info(f'There were {arrivals} arrivals of clients')

    logger.info(f'First employee completed {first_empl_req} requests '
        f'second employee completed {second_empl_req} requests')

    cnt = 0
    for i in range(1, arrivals + 1):
        logger.info(f'Client #{i}, wanted food = {food_wants[i]} '
            f'arrived at time {t_in[i]:.5f} and exited at time {t_out[i]:.5f}')

        if t_out[i] - t_in[i] > 5:
            cnt += 1

    return cnt * 100 / arrivals

def simulation_three_employees():
    logger = init_logger('Three Employees Logger', 'three_employees.log')  #initializing logger

    t = 0  #cur time
    arrivals = 0  #number of arrivals

    n = 0  #number of people in the system
    who_first = 0  #which client is employee 1 attending?
    who_second = 0  #which client is employee 2 attending?
    who_third = 0  #which client is employee 3 attending?

    t_out_1 = INFINITY  #time after employee 1 attended client
    t_out_2 = INFINITY  #time after employee 2 attended client
    t_out_3 = INFINITY  #time after employee 3 attended client

    t_in = [ 0 ]  #time that i-th (1-indexed) client entered
    t_out = [ 0 ]  #time that i-th (1-indexed) client exited
    food_wants = [ -1 ]  #what type of food does client i (1-indexed) wants?

    first_empl_req = 0  #how many requests first employee finished?
    second_empl_req = 0  #how many requests second employee finished?
    third_empl_req = 0  #how many requests third employee finished?

    logger.info('All variables initialized')

    next_arrival = gen_exp(LAMBDA_REGULAR)  #time of next arrival

    while True:
        cur_time = min(next_arrival, t_out_1, t_out_2, t_out_3)

        logger.info(f'Cur time = {cur_time:.5f} (in mins)')

        if next_arrival != INFINITY and next_arrival == cur_time:
            t = next_arrival
            food_wants.append(random.randint(0, 1))
            t_in.append(t)
            t_out.append(0)
            arrivals += 1

            f = food_wants[arrivals]

            logger.info(f'Client #{arrivals} entered at time = {t:.5f} and '
                f'wants food of type: {f} ({FOODS[f]})')

            if who_first == 0:
                logger.info(f'Employee 1 will attend client #{arrivals}')

                n += 1
                who_first = arrivals
                t_out_1 = t + random.uniform(FOOD_TIMES[f][0], FOOD_TIMES[f][1])

                logger.info(f'Employee will finish the request of client #{arrivals} at time = {t_out_1:.5f}')

            elif who_second == 0:
                logger.info(f'Employee 2 will attend client #{arrivals}')

                n += 1
                who_second = arrivals
                t_out_2 = t + random.uniform(FOOD_TIMES[f][0], FOOD_TIMES[f][1])

                logger.info(f'Employee will finish the request of client #{arrivals} at time = {t_out_2:.5f}')

            elif in_busy_hours(t) and who_third == 0:
                logger.info(f'Employee 3 (busy hours) will attend client #{arrivals}')

                n += 1
                who_third = arrivals
                t_out_3 = t + random.uniform(FOOD_TIMES[f][0], FOOD_TIMES[f][1])

                logger.info(f'Employee will finish the request of client #{arrivals} at time = {t_out_3:.5f}')

            else:
                logger.info(f'Client #{arrivals} will have to wait in the queue')

            logger.info('Generating next client...')

            if in_busy_hours(t):
                next_arrival = t + gen_exp(LAMBDA_BUSY)

                logger.info(f'Using busy lambda, '
                f'next arrival will ocurr at time = {next_arrival:.5f}')

            else:
                next_arrival = t + gen_exp(LAMBDA_REGULAR)

                logger.info(f'Using regular lambda, '
                f'next arrival will ocurr at time = {next_arrival:.5f}')

            if next_arrival > T:
                next_arrival = INFINITY

        elif t_out_1 != INFINITY and t_out_1 == cur_time:
            first_empl_req += 1
            t = t_out_1
            t_out[who_first] = t

            logger.info(f'Employee 1 finished client #{who_first} request at time = {t:.5f}')

            n -= 1
            next_guy = max(who_first, who_second, who_third) + 1
            who_first = 0 if next_guy > arrivals else next_guy
           
            if who_first == 0:
                t_out_1 = INFINITY

            else:
                f = food_wants[who_first]
                t_out_1 = t + random.uniform(FOOD_TIMES[f][0], FOOD_TIMES[f][1])

                logger.debug(f'The order of client #{who_first} will start to being processed, '
                    f'it will be finished at time = {t_out_1:.5f}')

        elif t_out_2 != INFINITY and t_out_2 == cur_time:
            second_empl_req += 1
            t = t_out_2
            t_out[who_second] = t

            logger.info(f'Employee 2 finished client #{who_second} request at time = {t:.5f}')

            n -= 1
            next_guy = max(who_first, who_second, who_third) + 1
            who_second = 0 if next_guy > arrivals else next_guy

            if who_second == 0:
                t_out_2 = INFINITY

            else:
                f = food_wants[who_second]
                t_out_2 = t + random.uniform(FOOD_TIMES[f][0], FOOD_TIMES[f][1])

                logger.debug(f'The order of client #{who_second} will start to being processed, '
                    f'it will be finished at time = {t_out_2:.5f}')

        elif t_out_3 != INFINITY and t_out_3 == cur_time:
            third_empl_req += 1
            t = t_out_3
            t_out[who_third] = t

            logger.info(f'Employee 3 finished client #{who_third} request at time = {t:.5f}')

            n -= 1
            next_guy = max(who_first, who_second, who_third) + 1
            who_third = 0 if not in_busy_hours(t) or next_guy > arrivals else next_guy

            if who_third == 0:
                t_out_3 = INFINITY

            else:
                f = food_wants[who_third]
                t_out_3 = t + random.uniform(FOOD_TIMES[f][0], FOOD_TIMES[f][1])

                logger.debug(f'The order of client #{who_third} will start to being processed, '
                    f'it will be finished at time = {t_out_3:.5f}')

        else:
            break

    logger.info('Kojo\'s kitchen is closed!')

    logger.info('Summary:')

    logger.info(f'There were {arrivals} arrivals of clients')

    logger.info(f'First employee completed {first_empl_req} requests '
        f'second employee completed {second_empl_req} requests '
        f'third employee (busy hours) completed {third_empl_req} requests')

    cnt = 0
    for i in range(1, arrivals + 1):
        logger.info(f'Client #{i}, wanted food = {food_wants[i]} '
            f'arrived at time {t_in[i]:.5f} and exited at time {t_out[i]:.5f}')

        if t_out[i] - t_in[i] > 5:
            cnt += 1

    return cnt * 100 / arrivals

if __name__ == '__main__':
    print(f'Percent of clients who waited more than 5 minutes (2 employees) = {simulation_two_employees()}')
    print(f'Percent of clients who waited more than 5 minutes (3 employees) = {simulation_three_employees()}')
