import sys
import time
import numpy as np
from flask import Flask, jsonify, request

app = Flask(__name__)


from telemetrix import telemetrix


"""
const int StepX = 2;
const int DirX = 5;
const int StepY = 3;
const int DirY = 6;
const int StepZ = 4;
const int DirZ = 7;

"""

MUX_SELECT_PINS = [7, 6, 5, 4]




VAL_DEFAULT = [0 ]
MUX_READ_VAL_TIME = [0]
MUX_VAL_ACCUMULATE = [0]


BoardMem = np.zeros(shape=(9,9), dtype="int")



TRESHOLD = [
    [(178, 183), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
    [(180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
    [(180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
    [(180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
    [(180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
    [(180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
    [(180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
    [(180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
    [(180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
]


# pretty print 3 digit 2d array
def serial_board(BoardMem, dim):
    print("    +" + "-" * 46 + "+")
    max_widths = [max(len(str(c)) for c in col) for col in zip(*BoardMem)]
    for i in range(dim):
        print(' ', dim - i -1, "| ", end='')
        for j in range(dim):
            c = BoardMem[i][j]
            # Calculate the spacing needed based on maximum width of each column
            spaces_needed = max_widths[j] - len(str(c))
            print(' ' * spaces_needed, c, end=' ')
        print('|')
    print("    +" + "-" * 46 + "+")
    print("        " + "    ".join(str(i) for i in range(dim)))

#PIN_MODE setting
    
CB_PIN_MODE = 0
CB_PIN = 1
CB_VALUE = 2
CB_TIME = 3


# x y offset from feeding point to grid 0 0 
X_OFFSET = 0
Y_OFFSET = 0



#ELECTRO

"""
board.digital_write(DIGITAL_PIN, 1)
board.digital_write(DIGITAL_PIN, 0)
"""

ELECTROMAGNET = 3

# GPIO Pins 
X_PULSE_PIN = 2
X_DIRECTION_PIN = 5

Y_PULSE_PIN = 3
Y_DIRECTION_PIN = 6

ENABLE_PIN = 8

# flag to keep track of the number of times the callback
# was called. When == 2, exit program

x = 0
y = 0
exit_flag = 0
channel = 0
#y = 0


"""
Nothing = 0
WHITE = 1
BLACK = 2
"""


def read_val_callback(data):
    #date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[CB_TIME]))
    #x, y = calc_xy(data[CB_PIN])

    global MUX_READ_VAL_TIME 
    global MUX_VAL_ACCUMULATE

    #Store val to compute the averafe
    MUX_READ_VAL_TIME[data[CB_PIN]] += 1
    MUX_VAL_ACCUMULATE[data[CB_PIN]] += data[CB_VALUE]

    #PRINT OUT INFO
    #print(f"Pin: {data[CB_PIN]} Val: {data[CB_VALUE]}")


# motor call back function 
def the_callback(data):
    global exit_flag
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[2]))
    print(f'Motor {data[1]} relative  motion completed at: {date}.')
    exit_flag += 1


#call back that print out the current position 
def current_position_callback(data):
    print(f'current_position_callback returns {data[2]}\n')

#call back that print out the target position
def target_position_callback(data):
    print(f'target_position_callback returns {data[2]}')



# step the stepper motor for a relative distance from its current position
def step_relative(the_board:telemetrix, motor_num, target, speed):

    global exit_flag

    #the_board.stepper_enable_outputs(motor_num)
    
    # create an accelstepper instance for a TB6600 motor driver
    # if you are using a micro stepper controller board:
    # pin1 = pulse pin, pin2 = direction
    
    the_board.stepper_set_current_position(motor_num, 0)
    # set the max speed and acceleration
    the_board.stepper_set_max_speed(motor_num, 999)
    the_board.stepper_move_to(motor_num, target)
    if target <=0:
        speed = -speed
    the_board.stepper_set_speed(motor_num, speed)

    the_board.stepper_get_current_position(motor_num, current_position_callback)
    the_board.stepper_get_target_position(motor_num, target_position_callback)

    board.stepper_run_speed_to_position(motor_num, the_callback)


    print('Running Motor')
    

    # keep application running
    while exit_flag == 0:
        try:
            time.sleep(.2)
        except KeyboardInterrupt:
            board.shutdown()
            sys.exit(0)
    exit_flag = 0
    

def reset(board, speed):
    global x
    global y
    print(f"x is {x}, y is {y}")
    step_relative(board, motorX, -x * 495, speed)
    step_relative(board, motorY, -y * 495, speed)
    x = 0
    y = 0

def stepX(board, num, speed):
    step_relative(board, motorX, num * 495, speed)

def stepY(board, num, speed):
    step_relative(board, motorY, num * 495, speed)


@app.route('/movepiece')
def move(x, y, speed):

    x = request.args.get('x', 0)  # Default to 0 if not provided
    y = request.args.get('y', 0)  # Default to 0 if not provided

    electroMagnet_on()

    stepX(board, x-1, speed)
    stepY(board, y, speed)
    stepX(board, 1, speed)

    electroMagnet_off()

    return jsonify({'x': x, 'y': y, 'message': 'Response from Flask with parameters!'})



def electroMagnet_on():
    board2.digital_write(ELECTROMAGNET, 1)

def electroMagnet_off():
    board2.digital_write(ELECTROMAGNET, 0)

# check the sesnor matrix value and update board values accordingly
def check_board_val():

    global BoardMem
    global MUX_VAL_ACCUMULATE
    global MUX_READ_VAL_TIME
   

    for i in range(5, 6):
        sel_0 = i & 1
        sel_1 = (i >>1) & 1
        sel_2 = (i >>2) & 1
        sel_3 = (i >>3) & 1

        board2.digital_write(MUX_SELECT_PINS[0], sel_0)
        board2.digital_write(MUX_SELECT_PINS[1], sel_1)
        board2.digital_write(MUX_SELECT_PINS[2], sel_2)
        board2.digital_write(MUX_SELECT_PINS[3], sel_3)


        print(f"Selecting {sel_0} {sel_1} {sel_2} {sel_3} ")

        board2.enable_analog_reporting(0)
        #board2.enable_analog_reporting(1)
        #board2.enable_analog_reporting(2)
        
        #board2.enable_analog_reporting(3)
        #board2.enable_analog_reporting(4)
        #board2.enable_analog_reporting(5)

        time.sleep(0.1)

        board2.disable_analog_reporting(0)
        #board2.disable_analog_reporting(1)
        #board2.disable_analog_reporting(2)
        #board2.disable_analog_reporting(3)
        #board2.disable_analog_reporting(4)
        #board2.disable_analog_reporting(5)

        
        #j = 0
        #x, y = iteration_to_sesnor(i, j)
        #print(f"x: {x}, y:{y}")

        
        for j in range(len(MUX_VAL_ACCUMULATE)):
            # get the average val
            avg = round(MUX_VAL_ACCUMULATE[j] / MUX_READ_VAL_TIME[j])
            # get the x, y position given iteration and pin 
            x, y = iteration_to_sesnor(i, j)
            # get threshold
            black_upper, black_lower = TRESHOLD[x][y]
            # get previous val
            prev = BoardMem[x][y]
            # given threshold, prev and average, send change to webapp
            verifyCell(avg, prev, black_lower, black_upper)
            # update
            BoardMem[x][y] = avg
            # print out
            print(f"x: {x}, y:{y}, avg:{avg}")


        # reset counter vals   
        MUX_VAL_ACCUMULATE = VAL_DEFAULT
        MUX_READ_VAL_TIME = VAL_DEFAULT

        time.sleep(5)


        
            
            
"""

0 stands for nothing ~ in raw
1 stands for black ~ in raw
2 stands for white ~ in raw
webapp

Responsible for sending message to 
"""
def verifyCell(avg, prev, black_lower, black_upper):

    if prev == 0:
        pass

    elif avg > black_upper:
        if prev >= black_lower and prev <= black_upper:
            # nothing to black
            pass
        else:
            # nothing to white
            pass
    elif avg >= black_lower:
        if prev > black_upper:
            # black to nothing
            pass
        elif prev < black_lower:
            # nothing to white
            pass
    else:
        if prev > black_upper:
            # white  to nothing
            pass
        elif prev >= black_lower:
            # white to black
            pass
        

# transform mux select vals and output pin num to (x,y)

def iteration_to_sesnor(iteration, mux_num):
    if mux_num % 2 == 1:
        if iteration in range(0,9):
            if mux_num == 1:
                return (2, iteration)
            elif mux_num == 3:
                return (5, iteration)
            elif mux_num == 5:
                return (8, iteration)
        else:
            if mux_num == 1:
                return (1, iteration - 9)
            elif mux_num == 3:
                return (4, iteration - 9)
            elif mux_num == 5:
                return (7, iteration - 9)
    else:
        if iteration == 13:
            return (-1, -1)
        elif iteration in range(4, 13):
            if mux_num == 0:
                return (0, iteration - 4)
            elif mux_num == 2:
                return (3, iteration - 4)
            elif mux_num == 4:
                return (6, iteration - 4)
        else:
            if mux_num == 0:
                return (1, iteration + 5)
            elif mux_num == 2:
                return (4, iteration + 5)
            elif mux_num == 4:
                return (7, iteration + 5)
        
        
#========================================functions end here=====================================#


# instantiate telemetrix
#board = telemetrix.Telemetrix(arduino_instance_id = 1)
board2 = telemetrix.Telemetrix(arduino_instance_id= 2)

board2.set_pin_mode_analog_input(0 , differential=0, callback=read_val_callback)
#board2.set_pin_mode_analog_input(1 , differential=0, callback=read_val_callback)
#board2.set_pin_mode_analog_input(2 , differential=3, callback=read_val_callback)

board2.set_pin_mode_digital_output(ELECTROMAGNET)

for select in MUX_SELECT_PINS:
    board2.set_pin_mode_digital_output(select)



# init motors

#motorX = board.set_pin_mode_stepper(interface=1, pin1=X_PULSE_PIN,
 #                                                pin2=X_DIRECTION_PIN)


#motorY = board.set_pin_mode_stepper(interface=1, pin1=Y_PULSE_PIN,
  #                                               pin2=Y_DIRECTION_PIN)



#app.run(port=5000)
while True:
    try:
        # start the main function
        """
        dir = int(input("next "))
        action = actionQ[actionIndex]
        dist = distance[actionIndex]0

        if action == 0:
            stepX(board, dist, 800)
        else:
            stepY(board,dist, 800)
        """
        
        #x, y = map(int, input("Enter input:").split())
        
        #move(x,y, 800) 

        check_board_val()
        
        
        #resetX(board)
    except KeyboardInterrupt:
        sys.exit(0)