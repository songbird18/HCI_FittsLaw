import sys, pygame, os
import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pygame.locals import *
import random
import time

pygame.init()

# set dimensions and font for display
X = 1280
Y = 720
font = pygame.font.SysFont('microsoftsansserif', 24)

# create display and set window title
display = pygame.display.set_mode((X, Y))
pygame.display.set_caption("Murray, Chelsea - Fitt's Law Experiment")


# Displays a startup screen with a description of the test process
# Also displays a Start button for player to start when ready
def DisplayInitialScreen():
	# fill display with a light neutral background
	display.fill('ivory')

	greet = 'Welcome to the Fitt\'s Law test program.'
	greet_txt = font.render(greet, True, "black")
	gr_box = greet_txt.get_rect()
	gr_box.center = (X/2, Y - 600)
	display.blit(greet_txt, gr_box)

	exp = 'This program will collect data on mouse movement time across 5 difficulty levels, indices 2 through 6.'
	exp_txt = font.render(exp, True, "black")
	exp_box = exp_txt.get_rect()
	exp_box.center = (X/2, Y - 525)
	display.blit(exp_txt, exp_box)

	exp2 = 'Please click the two boxes, alternating, as quickly as possible. You will be timed starting at the first click.'
	exp2_txt = font.render(exp2, True, "black")
	exp2_box = exp2_txt.get_rect()
	exp2_box.center = (X/2, Y - 450)
	display.blit(exp2_txt, exp2_box)

	exp3 = 'The boxes will change width and distance twice per level. Each width/distance combo is a separate set of data.'
	exp3_txt = font.render(exp3, True, "black")
	exp3_box = exp3_txt.get_rect()
	exp3_box.center = (X/2, Y - 375)
	display.blit(exp3_txt, exp3_box)

	exp4 = 'At the conclusion of the test, the recorded movement time data will be presented.'
	exp4_txt = font.render(exp4, True, "black")
	exp4_box = exp4_txt.get_rect()
	exp4_box.center = (X/2, Y - 300)
	display.blit(exp4_txt, exp4_box)

	# draw rectangle for start button
	start = pygame.Rect((X/2) - 100, Y - 185, 200, 100)
	pygame.draw.rect(display, 'springgreen', start)

	# draw text on button
	smsg = 'Start'
	stxt = font.render(smsg, True, 'black')
	sbox = stxt.get_rect()
	sbox.center = (X/2, Y - 135)
	display.blit(stxt, sbox)

	pygame.display.flip()

	running = True
    
	# wait for click on start button
	while running:
		for event in pygame.event.get():
			# exit program if X is clicked
			if event.type == pygame.QUIT:
				exit()
			# if left mouse button clicks, get mouse position
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				pos = pygame.mouse.get_pos()
				# check if Start button clicked, move on if yes
				if start.collidepoint(pos):
					running = False
					break



# Displays a screen/warning prior to each trial set
def DisplayReadyScreen():
	# fill the screen to make a light neutral background
	display.fill('ivory')
		
	lvl = 'Current trial difficulty: ' + str(index)
	lvl_txt = font.render(lvl, True, "black")
	lvl_box = lvl_txt.get_rect()
	lvl_box.center = (X/2, (Y/2) - 100)
	
	count = 'The trial will begin in 5 seconds.'
	count_txt = font.render(count, True, "black")
	ct_box = count_txt.get_rect()
	ct_box.center = (X/2, (Y/2) + 100)
    
    # render greeting/startup screen
	display.blit(lvl_txt, lvl_box)
	display.blit(count_txt, ct_box)

	pygame.display.flip()


# Displays an info screen to tell player the trial has ended
def DisplayTrialEnd():
	display.fill('ivory')

	msg = 'The trial for difficulty index ' + str(index) + ' is complete.'
	msg_txt = font.render(msg, True, "black")
	msg_box = msg_txt.get_rect()
	msg_box.center = (X/2, Y/2)

	display.blit(msg_txt, msg_box)

	pygame.display.flip()



def DisplayResults(times, avg_by_trial, avg_by_id):
	# create directory for results in project location
	cd = os.path.dirname(__file__)
	res_dir = os.path.join(cd, 'Results/')

	# if this file path doesn't exist, make it so
	if not os.path.isdir(res_dir):
		os.makedirs(res_dir)

	# plot results from testing
	# averages over each index of difficulty
	plt.plot(avg_by_id)
	plt.ylabel('Time between clicks (seconds)')
	plt.xlabel('Index of difficulty')
	plt.xticks(np.arange(0,5, step=1), labels=[str(i+2) for i in range(5)])
	plt.title('Average click times by index of difficulty')
	plt.savefig(res_dir + 'id_times.png')
	plt.close()

	#averages for each width/dist combo across the ids
	plt.plot(avg_by_trial[0])

	for i in range(1, 5):
		plt.plot(avg_by_trial[i])


	plt.ylabel('Time between clicks (seconds)')
	plt.xlabel('Trial')
	plt.xticks(np.arange(0,3, step=1), labels=[str(i+1) for i in range(3)])
	plt.title('Average click times per trial')
	plt.legend(['ID 2', 'ID 3', 'ID 4', 'ID 5', 'ID 6'])
	plt.savefig(res_dir + 'trial_times.png')
	plt.close()

	# create displayable images for pygame using plots
	idp = pygame.image.load(res_dir + 'id_times.png').convert()
	trp = pygame.image.load(res_dir + 'trial_times.png').convert()

	# update display
	display.fill('ivory')
	display.blit(idp, (0,120))
	display.blit(trp, (640,120))
	pygame.display.flip()

	# export full dataset (all times, should be 150 entries) to csv
	times2d = times.reshape(-1, times.shape[-1])
	df = pd.DataFrame(times2d)
	df.index = ['2-1','2-2','2-3','3-1','3-2','3-3','4-1','4-2','4-3','5-1','5-2','5-3','6-1','6-2','6-3']
	df.to_csv(res_dir + 'click_times.csv')

	
#Generate a Fitts Law trial according to parameters for difficulty index
#as well as whether this is run 1, 2, or 3 for this difficulty index
def GenerateFittScreen(id, it):
	# the value of the ratio used in the logarithm
	r = (2**id) - 1


    #for any ID, r=2^ID and r=d/w + 1
	#so, d/w + 1 = 2^ID
	#the following distance/box width combos maintain this equation
	mult = 80/(2**(id - 2))
	d = it * mult * r
	w = it * mult


	# create 2 rectangles with center points 'd' distance from each other,
	# dimensions w*w
	a = pygame.Rect((X/2) - (0.5*d + 0.5*w), (Y/2 - 0.5*w), w, w)
	b = pygame.Rect((X/2) + (0.5*d - 0.5*w), (Y/2 - 0.5*w), w, w)

	# refresh background
	display.fill('ivory')

	# display squares
	pygame.draw.rect(display, 'red', a)
	pygame.draw.rect(display, 'blue', b)

	pygame.display.flip()

	# store click times
	click_times = []
	# track which button was last clicked
	button = 0
	# count clicks
	clicks = 0
	# if a correct button clicked, set to True
	clicked = False
	# track start time
	start = time.time()

	running = True
    
	while running:
		for event in pygame.event.get():
			# exit program if X is clicked
			if event.type == pygame.QUIT:
				exit()
			# if left mouse button clicks, get mouse position
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				pos = pygame.mouse.get_pos()
				# check if correct button clicked (either button correct if this is first click)
				if  a.collidepoint(pos) and (button == 0 or clicks == 0):
					clicked = True
					button = 1
					end = time.time()
				elif b.collidepoint(pos) and (button == 1 or clicks == 0):
					clicked = True
					button = 0
					end = time.time()
				# if correct button clicked, track click time and increment clicks
				# but do not record time if this is the initial click
				if clicked == True:
					if clicks != 0:
						click_times.append(end - start)
					clicks += 1
					start = end
					clicked = False
				# exit loop if clicked 10 times
				if clicks > 10:
					running = False
	# index of performance calculated without exp. constants (raw movement time)
	#base_ip = CalcIP(click_times)
	# return click times for this trial, as well as raw ip
	return click_times #base_ip
	


# EXECUTE TEST

index = 2

id_times = []

DisplayInitialScreen()

for id in range(2, 7):
	# Display start screen
	DisplayReadyScreen()
	# start screen prompts user for a 5 second wait
	time.sleep(5)
	trial_time = []
	trial_avg = []
	for it in range(1, 4):
		# not doing anything with ip yet
		# for every trial, get click times and add to running list
		click_times = GenerateFittScreen(id, it)
		trial_time.append(click_times)

	id_times.append(trial_time)
	
	DisplayTrialEnd()
	index += 1
	time.sleep(3)

# use this for data visualization later
times = np.array(id_times)
avg_by_trial = []
avg_by_id = []

#calculate average times for each trial and each id
for i in range(0, 5):
	# average for each id
	avg_id = 0
	# temp storage so that the avg by trial is a 2d array
	avg_tmp = []
	# iterate over trials
	for j in range(0, 3):
		# iterate over each trial, average the time data
		avg_tl = 0
		for k in range(0, 10):
			avg_tl += times[i][j][k]
		avg_tl = avg_tl / 10
		#add the average to the temp avg list
		avg_tmp.append(avg_tl)
		#add the trial average to an id average
		avg_id += avg_tl
	avg_id = avg_id / 3
	avg_by_trial.append(avg_tmp)
	avg_by_id.append(avg_id)

avg_by_trial = np.array(avg_by_trial)
avg_by_id = np.array(avg_by_id)

DisplayResults(times, avg_by_trial, avg_by_id)

#time.sleep(10)

#DisplayTestEnd(avg_by_id, avg_by_trial)

while True:
	for event in pygame.event.get():
		# exit program if X is clicked
		if event.type == pygame.QUIT:
			exit()

