# Running the program
To run this Python program, you need to have Python installed along with all the necessary dependencies listed in the requirements.txt file. You can install them using the command listed below

pip install -r requirements.txt

# Program consists of 4 main windows, their main functionality and how to use such functionality are deatiled below

## Graph Creation Window
On this window there are two input columns, numbers in the range 2-50 can be entered within them
While the input columns are filled pressing the generate graph button will generate a graph of the specified size
Nodes on the edge can be removed to create the wanted graph shape
This graph can be submited to any of the next 3 windows through any of the 3 buttons below the generate graph button

## Player Vs. Player Window
This window allows for player vs player cops and robbers gameplay
Moves are played with mouse input by hovering over nodes and clicking
Legal moves are shown in green and what players turn it is is shown at the top of the screen
Moves can be played until the cop captures the robber
Once capture has occured the program needs to be closed out and restarted to be played again
## Player Vs. Strategy Window
This window allows for player vs strategy cops and robbers gameplay
Moves are made in the same way as the previous window, Cop moves will automatically played after robber moves without the need for a second players input
## Player Vs. Auto Strategy Window
This window allows for automatic cops and robbers gameplay agaisnt the strategy
Pressing the start button will cause the simulation to start and run until capture
Pressing the restart button will cause early stoppage of the automation and return to the graph creation window